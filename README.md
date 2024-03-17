The main node makes your conditioning go towards similar concepts so to enrich your composition or further away so to make it more precise.

It gathers similar pre-cond vectors for as long as the cosine similarity score diminishes. If it climbs back it stops. This allows to set a relative direction to similar concepts.

The nodes:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/8939ce9e-a131-4e17-9e51-12c101b214af)

## Vector sculptor text encode:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/06c556f0-537b-4acb-84bf-e0d702c085d0)

Does what I described above.

- Sculptor Intensity: How strong the effect will be. If the direction is not reversed I would say that up to 3 you will keep the overall meaning of your prompt. If reversed then don't go above one or face (enjoy?) randomness.
- Sculptor reversed:
  - off: goes towards the nearest vectors. This will make your generated images different in a generally good way. It can also reinforce the meaning of some words or make the images more colorful. Recommended intensity is above 1.
  - on: goes away from these nearest vectors. This might make the images sharper somehow or more precise with a low intensity but tends to have a more random effect in general. Recommended intensity is 1 and below.
- Token normalization: reworks the magnitude of each vectors. I recommand either "none" which leaves things by default or "mean" so to set every token's importance to their overall mean value. "set at 1" will set them all at 1 and I have no idea if this is a good idea. "mean of all tokens" will take the mean value of EVERY vectors within the pre-cond weights and is probably a bad idea but why not.

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


### intensity at 10 becomes total nonsense whatever the direction:

![00993UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/f54315f8-08d9-49a2-bfa7-9fc967697434)

![00991UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/514d9fa4-032b-4f5a-b5b8-8d0f812d9391)

## Note:

I make these nodes to try to understand things deeper. My maths can sometimes be wrong sometimes. Everything I do is self-taught with an overly top-to-bottom approach.
