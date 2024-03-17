The main node makes your conditioning go towards similar concepts so to enrich your composition or further away so to make it more precise.

It gathers similar pre-cond vectors for as long as the cosine similarity score diminishes. If it climbs back it stops. This allows to set a relative direction to similar concepts.

The nodes:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/e1d1a56b-d383-43e3-ac6f-59cc27cadd8f)

## Vector sculptor text encode:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/295a4170-8a59-4a62-ae11-7dac516f9a3c)

Does what I described above.

- **Sculptor Intensity**: How strong the effect will be. If the direction is not reversed I would say that up to 3 you will keep the overall meaning of your prompt. If reversed then don't go above 1~2.5 or face (enjoy?) randomness.
- **Sculptor method**:
  - **forward**: goes towards the nearest vectors. This will make your generated images different in a generally good way. It can also reinforce the meaning of some words or make the images more colorful. Recommended intensity is above 1.
  - **backward**: goes away from these nearest vectors. This might make the images sharper somehow or more precise with a low intensity but tends to have a more random effect in general. Recommended intensity is 1 and below.
  - **maximum_absolute**: Normalize the vectors and selects the values that are the furthest from 0. The intensity has no effect here besides disabling if set at 0. This tends to make the compositions more complex on simple subjects and more chaotic on complex prompts. Can be beneficial or not depending on what. It's mostly for fun but can give extremely nice results with abstract concepts.
- **Token normalization**: reworks the magnitude of each vectors. I recommand either "none" which leaves things by default or "mean" so to set every token's importance to their overall mean value. "set at 1" will set them all at 1 and I have no idea if this is a good idea. "mean of all tokens" will take the mean value of EVERY vectors within the pre-cond weights and is probably a bad idea but also why not.

If the intensity is set at 0 the token's normalization is still into effect. Setting it at 0 and selecting "none" will return a default Comfy conditioning.

Both directions offer valid variations no matter the subject.

## Conditioning (Slerp):

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/36830dc8-47bc-4cd5-abd9-dc9b799fa70f)

Since we are working with vectors, doing weighted averages might be the reason why things might feel "dilute" sometimes:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/89a6d968-717c-492e-a9b1-b360e54d1504)

With an average we're losing magnitude.

## "Conditioning normalize magnitude to empty:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/57b9bbc4-7581-4fd8-bce3-b1c0d342a42b)

Makes the overall intensity of the conditioning to the one of an empty cond. I have no idea if this is an actually good idea. It tends to give more balanced images regarding the colors and contrasts but also gave me more molten people.

If using SDXL the values are worked separately for clip_g and clip_l


# Examples (same noise seed, euler/20 steps):

### Going towards similar vectors:

![00859UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/c2fb0adf-0fcb-4cab-9162-fb8a5859173b)

"a plate with a few bananas":

![01027UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/13c845e3-cf48-48b7-81b8-f478a8099407)

<sub>Above 7 it would become way too random.</sub>

### Going away from similar vectors:


![00983UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/31bdd670-705d-4c82-a65e-0ca0619e8438)

"a plate with a few bananas":

![01066UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/cd731651-c802-46c4-b5a6-eae9c9a2879b)

<sub>There is slightly less clutter</sub>

### Maximum absolute:

![03184UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/cdc50ef9-d427-4cd1-b945-33f7f91eef4b)

# Example with SDXL:

prompt is: "dark enchanted forest with colorful glowing lights, digital painting, night, black amoled wallpaper, wintery fog, fantasy"

Default:

![03371UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/0bb67f1f-f8fb-4725-b32e-134f7061b4ae)

<sub>_Bleh..._</sub>

The settings are written in the images:

![03374UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/5d434870-e8d8-4aeb-811c-df69311450bb)

![03375UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/acc419bb-004d-4795-bd5f-cd5ef75862af)

![03376UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/f38313bc-8827-458d-a7e8-dfcc8e1dc54a)

![03377UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/e506c276-1f1d-4c08-9ce9-a1e23a02bc57)

<sub>_Did I just Midjourney SDXL???_</sub>

![03390UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/e156c495-1358-498a-b37e-ac90f68941c8)

![03391UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/8477e529-603f-4751-9bd3-09ac359000f8)

![03393UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/a31b7869-b62c-4cc8-81cb-f027f0cb19b6)

![03394UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/0da64f0c-2409-461c-8ec9-c005463f1678)

![03396UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/f1c32db6-61ba-46c6-addf-ef974ebb73d2)

Maximum absolute didn't do well this time:

![03397UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/0d650597-5b3d-461e-8cf6-b6c60b021606)



### intensity at 10 becomes total nonsense whatever the direction:

![00993UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/f54315f8-08d9-49a2-bfa7-9fc967697434)

![00991UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/514d9fa4-032b-4f5a-b5b8-8d0f812d9391)

## Note:

I make these nodes to try to understand things deeper. My maths can sometimes be wrong sometimes. Everything I do is self-taught with an overly top-to-bottom approach.

Also kittens seems immune to this transformation and inherits little suits before turning into AI chaos.

![kit](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/34b4f33d-1272-471c-9fc0-4dd8c0358526)

