import torch
import comfy.model_management as model_management

def get_closest_token_cosine_similarities(single_weight, all_weights, return_scores=False):
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    scores = cos(all_weights, single_weight.unsqueeze(0).to(all_weights.device))
    sorted_scores, sorted_ids = torch.sort(scores, descending=True)
    best_id_list = sorted_ids.tolist()
    if not return_scores:
        return best_id_list
    scores_list = sorted_scores.tolist()
    return best_id_list, scores_list

def refine_token_weight(token_id, all_weights, sculptor_threshold, subtract_difference):
    initial_weight = all_weights[token_id]
    initial_weight_copy = torch.clone(initial_weight)
    pre_mag = torch.norm(initial_weight_copy)
    concurrent_weights_ids, scores = get_closest_token_cosine_similarities(initial_weight,all_weights,True)
    concurrent_weights_ids, scores = concurrent_weights_ids[1:], scores[1:]

    s = [score for p, score in enumerate(scores) if p < 100 and score > sculptor_threshold][:100]
    if len(s) <= 1: return initial_weight.cpu(), 0
    scores = s
    concurrent_weights_ids = concurrent_weights_ids[:len(scores)]

    sum_of_scores = sum(scores)
    concurrent_weights = [all_weights[w] / torch.norm(all_weights[w]) for i, w in enumerate(concurrent_weights_ids)]
    initial_weight = initial_weight / torch.norm(initial_weight) * len(s) / sum_of_scores

    for x in range(len(concurrent_weights)):
        initial_weight += concurrent_weights[x] * (2 if not subtract_difference else 0.5)
    if subtract_difference:
        initial_weight = initial_weight_copy * 2 - initial_weight
    initial_weight = initial_weight * pre_mag / torch.norm(initial_weight)
    return initial_weight.cpu(), len(scores)

class vector_sculptor_node:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "text": ("STRING", {"multiline": True}),
                "sculptor_threshold": ("FLOAT", {"default": 0.55, "min": 0.5, "max": 1, "step": 0.05}),
                "sculptor_subtract" : ("BOOLEAN", {"default": False}),
            }
        }

    FUNCTION = "exec"
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = "conditioning"

    def exec(self, clip, text, sculptor_threshold, sculptor_subtract):
        ignored_token_ids = [49406, 49407, 0]
        initial_tokens = clip.tokenize(text)
        if sculptor_threshold < 1:
            total_found = 0
            total_replaced = 0
            total_candidates = 0
            for k in initial_tokens:
                clip_model = getattr(clip.cond_stage_model, f"clip_{k}", None)
                all_weights = torch.clone(clip_model.transformer.text_model.embeddings.token_embedding.weight).to(device=model_management.get_torch_device())
                for x in range(len(initial_tokens[k])):
                    for y in range(len(initial_tokens[k][x])):
                        token_id, attn_weight = initial_tokens[k][x][y]
                        if token_id not in ignored_token_ids:
                            total_candidates += 1
                            new_vector, n_found = refine_token_weight(token_id, all_weights, sculptor_threshold, sculptor_subtract)
                            initial_tokens[k][x][y] = (new_vector, attn_weight)
                            if n_found > 0:
                                total_found += n_found
                                total_replaced += 1
                        else:
                            initial_tokens[k][x][y] = (all_weights[token_id], attn_weight)
                del all_weights
            print(f"total_found: {total_found} / total_replaced: {total_replaced} / total_candidates: {total_candidates} / candidate proportion replaced: {round(100 * total_replaced / total_candidates, 2)}%")
        cond, pooled = clip.encode_from_tokens(initial_tokens, return_pooled=True)
        conditioning = [[cond, {"pooled_output": pooled}]]
        return (conditioning,)

NODE_CLASS_MAPPINGS = {
    "CLIP Vector Sculptor text encode": vector_sculptor_node,
}
