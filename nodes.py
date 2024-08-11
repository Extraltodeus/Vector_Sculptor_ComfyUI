import torch
import comfy.model_management as model_management
from copy import deepcopy

def maximum_absolute_values(tensors,reversed=False):
    shape = tensors.shape
    tensors = tensors.reshape(shape[0], -1)
    tensors_abs = torch.abs(tensors)
    if not reversed:
        max_abs_idx = torch.argmax(tensors_abs, dim=0)
    else:
        max_abs_idx = torch.argmin(tensors_abs, dim=0)
    result = tensors[max_abs_idx, torch.arange(tensors.shape[1])]
    return result.reshape(shape[1:])

def get_closest_token_cosine_similarities(single_weight, all_weights, return_scores=False):
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    scores = cos(all_weights, single_weight.unsqueeze(0).to(all_weights.device))
    sorted_scores, sorted_ids = torch.sort(scores, descending=True)
    best_id_list = sorted_ids.tolist()
    if not return_scores:
        return best_id_list
    scores_list = sorted_scores.tolist()
    return best_id_list, scores_list

def get_single_cosine_score(single_weight,concurrent_weight):
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    score = cos(concurrent_weight.unsqueeze(0), single_weight.unsqueeze(0)).item()
    return score

def refine_token_weight(token_id, all_weights, sculptor_method, sculptor_multiplier):
    initial_weight = all_weights[token_id]
    pre_mag = torch.norm(initial_weight)
    concurrent_weights_ids, scores = get_closest_token_cosine_similarities(initial_weight,all_weights,True)
    concurrent_weights_ids, scores = concurrent_weights_ids[1:], scores[1:]
    
    previous_cos_score = 0
    cos_score = 1
    iter_num = 0
    s = []
    tmp_weights = []
    
    ini_w = torch.clone(initial_weight)

    while previous_cos_score < cos_score:
        if iter_num > 0:
            previous_cos_score = cos_score
        s.append(scores[iter_num])
        current_weight = all_weights[concurrent_weights_ids[iter_num]]
        tmp_weights.append(current_weight)
        vec_sum = torch.sum(torch.stack(tmp_weights),dim=0)
        cos_score = get_single_cosine_score(ini_w, vec_sum)
        iter_num += 1
    del s[-1]
    del tmp_weights[-1]

    if len(s) <= 1: return initial_weight.cpu(), 0

    if sculptor_method == "maximum_absolute":
        concurrent_weights = torch.stack([ini_w/torch.norm(ini_w)]+[t/torch.norm(t) for i, t in enumerate(tmp_weights)])
        initial_weight = maximum_absolute_values(concurrent_weights)
        initial_weight *= pre_mag / torch.norm(initial_weight)
        return initial_weight.cpu(), len(s)
    elif sculptor_method == "add_minimum_absolute":
        concurrent_weights = torch.stack([ini_w/torch.norm(ini_w)]+[t/torch.norm(t) for i, t in enumerate(tmp_weights)])
        initial_weight_min = maximum_absolute_values(concurrent_weights, sculptor_method == "minimum_absolute")
        initial_weight = ini_w + initial_weight_min * sculptor_multiplier
        initial_weight *= pre_mag / torch.norm(initial_weight)
        return initial_weight.cpu(), len(s)
    
    concurrent_weights = torch.sum(torch.stack([t * s[i]**2 for i, t in enumerate(tmp_weights)]), dim=0)
    final_score = get_single_cosine_score(initial_weight,concurrent_weights) * sculptor_multiplier

    if sculptor_method == "backward":
        initial_weight = initial_weight + concurrent_weights * final_score
    elif sculptor_method == "forward":
        initial_weight = initial_weight - concurrent_weights * final_score

    initial_weight = initial_weight * pre_mag / torch.norm(initial_weight)
    return initial_weight.cpu(), len(s)

def vector_sculptor_tokens(clip, text, sculptor_method, token_normalization, sculptor_multiplier):
    ignored_token_ids = [49406, 49407, 0]
    initial_tokens = clip.tokenize(text)
    total_found = 0
    total_replaced = 0
    total_candidates = 0
    
    for k in initial_tokens:
        mean_mag = 0
        mean_mag_count = 0
        to_mean_coords = []
        if k.lower() == "g":
            actual_multiplier = sculptor_multiplier * 4 / 1.5 #2048 to 768, this gives the same effect intensity on both CLIP
        else:
            actual_multiplier = sculptor_multiplier
        clip_model = getattr(clip.cond_stage_model, f"clip_{k}", None)
        all_weights = torch.clone(clip_model.transformer.text_model.embeddings.token_embedding.weight).to(device=model_management.get_torch_device())
        if token_normalization == "mean of all tokens":
            all_mags = torch.stack([torch.norm(t) for t in all_weights])
            mean_mag_all_weights = torch.mean(all_mags, dim=0).item()
        for x in range(len(initial_tokens[k])):
            for y in range(len(initial_tokens[k][x])):
                token_id, attn_weight = initial_tokens[k][x][y]
                if token_id not in ignored_token_ids and sculptor_multiplier > 0:
                    total_candidates += 1
                    new_vector, n_found = refine_token_weight(token_id,all_weights, sculptor_method, actual_multiplier)
                    if n_found > 0:
                        total_found += n_found
                        total_replaced += 1
                else:
                    new_vector = all_weights[token_id]
                if token_normalization != "none" and y != 0 and token_id != 2:
                    if token_normalization == "mean" or token_normalization == "mean * attention":
                        mean_mag += torch.norm(new_vector).item()
                        mean_mag_count += 1
                        to_mean_coords.append([x,y])
                    elif token_normalization == "set at 1":
                        new_vector /= torch.norm(new_vector)
                    elif token_normalization == "default * attention":
                        new_vector *= attn_weight
                    elif token_normalization == "set at attention":
                        new_vector = new_vector / torch.norm(new_vector) * attn_weight
                        # new_vector /= torch.norm(new_vector) * attn_weight
                    elif token_normalization == "mean of all tokens":
                        new_vector = new_vector / torch.norm(new_vector) * mean_mag_all_weights
                        # new_vector /= torch.norm(new_vector) * mean_mag_all_weights
                initial_tokens[k][x][y] = (new_vector, attn_weight)
        if (token_normalization == "mean" or token_normalization == "mean * attention") and mean_mag_count > 0:
            mean_mag /= mean_mag_count
            for x, y in to_mean_coords:
                token_weight, attn_weight = initial_tokens[k][x][y]
                if token_normalization == "mean * attention":
                    twm = attn_weight
                else:
                    twm = 1
                token_weight = token_weight / torch.norm(token_weight) * mean_mag * twm
                initial_tokens[k][x][y] = (token_weight, attn_weight)
        del all_weights
    if total_candidates > 0:
        print(f"total_found: {total_found} / total_replaced: {total_replaced} / total_candidates: {total_candidates} / candidate proportion replaced: {round(100*total_replaced/total_candidates,2)}%")
    return initial_tokens

class vector_sculptor_node:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "text": ("STRING", {"multiline": True}),
                "sculptor_intensity": ("FLOAT", {"default": 1, "min": 0, "max": 10, "step": 0.01}),
                "sculptor_method" : (["forward","backward","maximum_absolute","add_minimum_absolute"],),
                "token_normalization": (["none", "mean", "set at 1", "default * attention", "mean * attention", "set at attention", "mean of all tokens"],),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING","STRING",)
    RETURN_NAMES = ("Conditioning","Parameters_as_string",)
    CATEGORY = "conditioning"

    def exec(self, clip, text, sculptor_intensity, sculptor_method, token_normalization):
        sculptor_tokens = vector_sculptor_tokens(clip, text, sculptor_method, token_normalization, sculptor_intensity)
        cond, pooled = clip.encode_from_tokens(sculptor_tokens, return_pooled=True)
        conditioning = [[cond, {"pooled_output": pooled}]]
        if sculptor_intensity == 0 and token_normalization == "none":
            parameters_as_string = "Disabled"
        else:
            parameters_as_string = f"Intensity: {round(sculptor_intensity,2)}\nMethod: {sculptor_method}\nNormalization: {token_normalization}"
        return (conditioning,parameters_as_string,)

def add_to_first_if_shorter(conditioning1,conditioning2,x=0):
    min_dim = min(conditioning1[x][0].shape[1],conditioning2[x][0].shape[1])
    if conditioning2[x][0].shape[1]>conditioning1[x][0].shape[1]:
        conditioning2[x][0][:,:min_dim,...] = conditioning1[x][0][:,:min_dim,...]
        conditioning1 = conditioning2
    return conditioning1

# cheap slerp / I will bet an eternity doing regex that this is the dark souls 2 camera direction formula
def average_and_keep_mag(v1,v2,p1):
    m1 = torch.norm(v1)
    m2 = torch.norm(v2)
    v0 = v1 * p1 + v2 * (1 - p1)
    v0 = v0 / torch.norm(v0) * (m1 * p1 + m2 * (1 - p1))
    return v0

# from  https://discuss.pytorch.org/t/help-regarding-slerp-function-for-generative-model-sampling/32475
def slerp(high, low, val):
    dims = low.shape

    #flatten to batches
    low = low.reshape(dims[0], -1)
    high = high.reshape(dims[0], -1)

    low_norm = low/torch.norm(low, dim=1, keepdim=True)
    high_norm = high/torch.norm(high, dim=1, keepdim=True)

    # in case we divide by zero
    low_norm[low_norm != low_norm] = 0.0
    high_norm[high_norm != high_norm] = 0.0

    omega = torch.acos((low_norm*high_norm).sum(1))
    so = torch.sin(omega)
    res = (torch.sin((1.0-val)*omega)/so).unsqueeze(1)*low + (torch.sin(val*omega)/so).unsqueeze(1) * high
    return res.reshape(dims)
    
class slerp_cond_node:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_to": ("CONDITIONING",),
                "conditioning_from": ("CONDITIONING",),
                "conditioning_to_strength": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.01}),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "conditioning"

    def exec(self, conditioning_to, conditioning_from,conditioning_to_strength):
        cond1 = deepcopy(conditioning_to)
        cond2 = deepcopy(conditioning_from)
        for x in range(min(len(cond1),len(cond2))):
            min_dim = min(cond1[x][0].shape[1],cond2[x][0].shape[1])
            if cond1[x][0].shape[2] == 2048:
                cond1[x][0][:,:min_dim,:768] = slerp(cond1[x][0][:,:min_dim,:768], cond2[x][0][:,:min_dim,:768], conditioning_to_strength)
                cond1[x][0][:,:min_dim,768:] = slerp(cond1[x][0][:,:min_dim,768:], cond2[x][0][:,:min_dim,768:], conditioning_to_strength)
            else:
                cond1[x][0][:,:min_dim,...] = slerp(cond1[x][0][:,:min_dim,...], cond2[x][0][:,:min_dim,...], conditioning_to_strength)
            cond1 = add_to_first_if_shorter(cond1,cond2,x)
        return (cond1,)

class average_keep_mag_node:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_to": ("CONDITIONING",),
                "conditioning_from": ("CONDITIONING",),
                "conditioning_to_strength": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.01}),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "conditioning"

    def exec(self, conditioning_to, conditioning_from,conditioning_to_strength):
        cond1 = deepcopy(conditioning_to)
        cond2 = deepcopy(conditioning_from)
        for x in range(min(len(cond1),len(cond2))):
            min_dim = min(cond1[x][0].shape[1],cond2[x][0].shape[1])
            if cond1[x][0].shape[2] == 2048:
                cond1[x][0][:,:min_dim,:768] = average_and_keep_mag(cond1[x][0][:,:min_dim,:768], cond2[x][0][:,:min_dim,:768], conditioning_to_strength)
                cond1[x][0][:,:min_dim,768:] = average_and_keep_mag(cond1[x][0][:,:min_dim,768:], cond2[x][0][:,:min_dim,768:], conditioning_to_strength)
            else:
                cond1[x][0][:,:min_dim,...] = average_and_keep_mag(cond1[x][0][:,:min_dim,...], cond2[x][0][:,:min_dim,...], conditioning_to_strength)
            cond1 = add_to_first_if_shorter(cond1,cond2,x)
        return (cond1,)
    
class norm_mag_node:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING",),
                "empty_conditioning": ("CONDITIONING",),
                "enabled" : ("BOOLEAN", {"default": True}),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "conditioning"

    def exec(self, conditioning, empty_conditioning, enabled):
        if not enabled: return (conditioning,)
        cond1 = deepcopy(conditioning)
        empty_cond = empty_conditioning[0][0]
        empty_tokens_no = empty_cond[0].shape[0]

        for x in range(len(cond1)):
            for y in range(len(cond1[x][0])):
                for z in range(len(cond1[x][0][y])):
                    if cond1[x][0][y][z].shape[0] == 2048:
                        cond1[x][0][y][z][:768] = cond1[x][0][y][z][:768]/torch.norm(cond1[x][0][y][z][:768]) * torch.norm(empty_cond[0][z%empty_tokens_no][:768])
                        cond1[x][0][y][z][768:] = cond1[x][0][y][z][768:]/torch.norm(cond1[x][0][y][z][768:]) * torch.norm(empty_cond[0][z%empty_tokens_no][768:])
                    else:
                        cond1[x][0][y][z] = cond1[x][0][y][z]/torch.norm(cond1[x][0][y][z]) * torch.norm(empty_cond[0][z%empty_tokens_no])
        return (cond1,)

class conditioning_merge_clip_g_l:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "cond_clip_l": ("CONDITIONING",),
                "cond_clip_g": ("CONDITIONING",),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "conditioning"

    def exec(self, cond_clip_l, cond_clip_g):
        conditioning_l = deepcopy(cond_clip_l)
        conditioning_g = deepcopy(cond_clip_g)
        for x in range(min(len(conditioning_g),len(conditioning_l))):
            min_dim = min(conditioning_g[x][0].shape[1],conditioning_l[x][0].shape[1])
            conditioning_g[x][0][:,:min_dim,:768] = conditioning_l[x][0][:,:min_dim,:768]
        return (conditioning_g,)
    
NODE_CLASS_MAPPINGS = {
    "CLIP Vector Sculptor text encode": vector_sculptor_node,
    "Conditioning (Slerp)": slerp_cond_node,
    "Conditioning (Average keep magnitude)": average_keep_mag_node,
    "Conditioning normalize magnitude to empty": norm_mag_node,
    "Conditioning SDXL merge clip_g / clip_l": conditioning_merge_clip_g_l,
}
