The main node makes your conditioning go towards similar concepts so to enrich your composition or further away so to make it more precise.

It gathers similar pre-cond vectors for as long as the cosine similarity score diminishes. If it climbs back it stops. This allows to set a relative direction to similar concepts.

There are examples at the end but [you can also check this imgur album](https://imgur.com/a/WvPd81Y) which demonstrates the capability of improving variety.

The nodes:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/1515fdd9-2aaf-45ec-990a-1d9ab15e9592)


From Backward 5 to forward 1.5 "average keep magnitude" up until the middle and slerp the way back:



https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/231b83d7-7b86-481f-9da5-2373513c2cd5



## Vector sculptor text encode:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/295a4170-8a59-4a62-ae11-7dac516f9a3c)

Does what I described above.

- **Sculptor Intensity**: How strong the effect will be. Forward is best from 0 to 1 for photorealistic images anb 1 to 2 for more artistic purpose.
- **Sculptor method**:
  - **forward**: Subtract the nearest vectors. Going above 1 might have adversarial effects.
  - **backward**: Add them instead.
  - **maximum_absolute**: Normalize the vectors and selects the values that are the furthest from 0. The intensity has no effect here besides disabling if set at 0. This tends to make the compositions more complex on simple subjects and more chaotic on complex prompts. Can be beneficial or not depending on what. It's mostly for fun but can give extremely nice results with abstract concepts.
- **Token normalization**: reworks the magnitude of each vectors. I recommand either "none" which leaves things by default or "mean" so to set every token's importance to their overall mean value. "set at 1" will set them all at 1 and I have no idea if this is a good idea. "mean of all tokens" will take the mean value of EVERY vectors within the pre-cond weights and is probably a bad idea but also why not.

If the intensity is set at 0 the token's normalization is still into effect. Setting it at 0 and selecting "none" will return a default Comfy conditioning.

Both directions offer valid variations no matter the subject.

For general use I recommand forward at 0.5 for the positive prompt and to "stay in place" for the negative.

Normalizing the tokens magnitudes at their mean seems to have a positive effect too. Especially with the negative prompt which tends to lower my ratio of burned images.

## Conditioning (Slerp) and Conditioning (Average keep magnitude):

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/36830dc8-47bc-4cd5-abd9-dc9b799fa70f)

Since we are working with vectors, doing weighted averages might be the reason why things might feel "dilute" sometimes:

"Conditioning (Average keep magnitude)" is a cheap slerp which does a weighted average with the conditionings and their magnitudes.

"Conditioning (Slerp)" will do an actual slerp and might be preferable.

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/89a6d968-717c-492e-a9b1-b360e54d1504)

With an average we're losing ~alti~ magnitude.

## "Conditioning normalize magnitude to empty:

![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/57b9bbc4-7581-4fd8-bce3-b1c0d342a42b)

Makes the overall intensity of the conditioning to the one of an empty cond. I have no idea if this is an actually good idea. It tends to give more balanced images regarding the colors and contrasts but also gave me more molten people.

If using SDXL the values are worked separately for clip_g and clip_l


# Examples (same seed side by side):

## SD 1.x

![00545UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/10a3a4b7-f291-4927-be19-2f6df3d0a6a8)

![00724UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/f576deac-b90f-431f-b83a-2ff391bed15f)

![00608UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/438621c6-e878-4dc0-8e66-d2f0d95261ea)

## SDXL:

![01785UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/9a47419a-b34a-489a-bb4d-0181cb966abf)

![01796UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/2bb08802-8e26-4348-83f0-1132c875fdfb)

![01816UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/9453d4fc-15d7-4554-ba12-b50b810ebceb)


Forward at 0.5~1.0 it seems to cure the "always the same face" effect:

![01324UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/5a72f150-2b04-401e-981d-e68330f6bcdf)

With a lower intensity the effect can still be seen without necessarily changing the composition:

![01489UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/e1b71f84-7175-4db0-af56-171391bf1489)

![01515UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/4f16dcf5-85b3-4b01-871d-1f7b5ffe29ce)



_"dark enchanted forest with colorful glowing lights, digital painting, night, black amoled wallpaper, wintery fog, fantasy"_

![01851UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/a3217e71-ef4e-482d-936a-522e1756c9ba)

![01847UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/226f33eb-a908-4d54-b71f-52e3be2ed2b6)


Too much forward will overreach your general meaning and become more unpredictable:

![01823UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/7a45f3fe-c5d5-4036-aa1f-336e85629c0e)

![01835UI_00001_](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/e22d60be-98e8-4f45-855f-ef1cc4369f2b)


![image](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/36bd7b2d-e667-4087-ac0b-eeda397dfb11)



## More on SD 1.5:

![part_1](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/25936e12-3d0d-406e-a372-2fc21af0f3e5)

![part_2](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/db56a2a8-8048-4e46-931e-ffd68c1ebd29)

![part_3](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/6d1f76ea-72ea-48a8-8d56-ce929a939cd4)


## Note:

I make these nodes to try to understand things deeper. My maths can sometimes be wrong. Everything I do is self-taught with an overly top-to-bottom approach.

Some things like the fact that I'm not turning the cosine similarity score into a linear value might look like an oversight but doing so tends to diminish the effect of the node too strongly and is therefore a deliberate choice.

I feel that what I have done might also be done by tweaking the activation functions but I haven't got that far. Yet.

Also kittens seems immune to this transformation and inherits little suits before turning into AI chaos.

![kit](https://github.com/Extraltodeus/Vector_Sculptor_ComfyUI/assets/15731540/34b4f33d-1272-471c-9fc0-4dd8c0358526)

