# Style Reverse Engineering

Use this when the user provides an image because they like its visual style and wants a reusable prompt. This is different from subject reference mode.

## Goal

Extract the image's aesthetic soul and turn it into a generic Chinese prompt. The prompt must let the user replace the subject while preserving the visual system.

Required placeholder:

```text
[在此处替换为您想要生成的主体内容]
```

## Strip From the Source Image

Remove:

- Specific character names, IP names, real people, logos, brand marks.
- Exact readable text, slogans, captions, UI labels, watermarks.
- Specific plot events or narrative facts that are not necessary to the style.
- One-off subject details that would make the prompt only reproduce the original image.

Keep:

- Visual grammar, composition, perspective, color logic, medium, lighting, mood, texture.
- Abstract symbolic devices such as barcode-like marks, warning labels, torn-paper edges, geometric panels, grids, windows, or abstract type blocks.
- General subject treatment, such as "silhouette", "full-body dynamic pose", "close-up bust", or "central object as icon".

## High-Weight Signal Calibration

Use this as an internal weighting pass before the 15-dimension analysis. It is not a new output mode and does not replace any existing dimension.

First identify the six signals most likely to drive image generation:

- Subject treatment: how the replaceable subject is rendered, framed, posed, or abstracted.
- Core art/design movement: the strongest named style family, such as constructivism, editorial minimalism, cyberpunk anime, or retro print.
- Composition mechanism: the dominant layout engine, such as diagonal cuts, window overlays, grids, radial pressure, or central icon framing.
- Color limitation: the strict palette, contrast system, spot-color behavior, or cold/warm logic.
- Material/post-processing system: print texture, paper wear, glitch traces, RGB shift, halftone, grain, blur, or scan artifacts.
- Emotional atmosphere: the stable mood that ties the visual choices together.

Then use the 15 dimensions to fill gaps, add constraints, and preserve nuance. Do not distribute prompt length evenly across all dimensions; prioritize the high-weight signals in the final prompt.

If the user provides an original prompt or nearby prompt evidence, treat it as calibration evidence for which words are high-signal. Keep the final output as a generic style recipe with the subject placeholder.

### Core Drivers vs Decorative Noise

- **核心驱动:** Style, composition, color, material, post-processing, mood, and subject treatment that would visibly change the generated image if removed.
- **装饰噪声:** Corner numbers, tiny labels, signatures, incidental UI boxes, one-off icons, and small layout ornaments. Keep only 2-4 representative devices, and only when they help describe the visual language.
- If a decorative device repeats across the whole image or organizes the layout, promote it to a symbolic/composition feature. If it appears once in a corner, compress or omit it.
- Avoid turning every visible object into a prompt requirement. The goal is to preserve the transferable system, not inventory the image.

## Internal 15-Dimension Analysis

Analyze internally, but do not output the analysis unless asked.

1. **Image style:** design/art family, illustration/photography/3D/mixed-media category, dominant style stack.
2. **Image components:** subject/background/graphic elements/texture layers/type blocks/symbols.
3. **Composition:** center, diagonal, radial, grid, window overlay, collage, negative space, full bleed.
4. **Shot/storyboard type:** wide shot, full body, medium shot, close-up, extreme close-up, low angle, high angle, Dutch angle, animation still, poster key visual.
5. **Lighting:** hard/soft, high-key/low-key, rim light, backlight, neon, golden hour, blue hour, flat graphic light.
6. **Tone and color science:** mono/duotone/tritone, complementary, analogous, cold-warm contrast, saturation, brightness, print spot-color behavior.
7. **Medium/material texture:** vector, cel shading, line art, Riso, screen print, paper, film grain, chrome, glass, concrete, watercolor, photo blur.
8. **Mood and atmosphere:** lonely, sacred, melancholic, rebellious, elegant, playful, oppressive, dreamy, documentary, futuristic.
9. **Render/camera parameters:** lens feel, focal length impression, depth of field, motion blur, exposure, render type, edge quality.
10. **Era and cultural context:** retro, Y2K, Soviet, punk zine, Japanese minimalism, Art Deco, cyberpunk, contemporary editorial, etc.
11. **Spatial logic and perspective:** one/two/three-point perspective, orthographic, isometric, fisheye, telephoto compression, impossible space, layered depth.
12. **Information density and negative space:** sparse, balanced, dense, controlled chaos, subject readability.
13. **Dynamic state:** still, suspended instant, impact frame, motion trail, wind, falling, reaching, glitch displacement.
14. **Post-processing and digital traces:** pixel sorting, RGB shift, chromatic aberration, JPEG blocks, CRT scanlines, halftone, dust, scratches, light leak.
15. **Symbolic features:** labels, arrows, halos, frames, windows, grids, barcodes, stamps, warning marks, technical annotations, abstract typography.

## Output Rules

- Output one complete Chinese prompt.
- Do not include headings, bullet points, explanations, or analysis.
- Start with or prominently include `[在此处替换为您想要生成的主体内容]`.
- The prompt should be reusable for different subjects.
- The only bracketed placeholder allowed in the final prompt is `[在此处替换为您想要生成的主体内容]`.
- Replace every other template placeholder with concrete language inferred from the image.
- Use clear aesthetic language, not vague praise.
- If the source image includes text, transform it into "abstract typography blocks / non-readable graphic text elements" unless exact text is explicitly requested.
- If the source image's subject is central to composition, abstract it as "主体", "人物/物体", "核心视觉焦点", or "剪影/线稿/动态姿态" instead of copying identity.
- Append one short save question after the prompt unless the user explicitly requests prompt-only output: `要把这个风格配方保存到 skill 里以后复用吗？`

## Saving Confirmed Recipes

If the user confirms saving a reverse-engineered style recipe:

- Append the recipe to `references/style_recipe_registry.md`.
- If the registry still says "No saved recipes yet.", remove that line when adding the first recipe.
- Use the registry format exactly: name, tags, visual thesis, use for, avoid for, prompt.
- Save a reusable prompt, not a record of the source image.
- The saved prompt must keep only the subject placeholder and must not include original characters, text, logos, IP names, or plot details.

## Generic Output Template

```text
[在此处替换为您想要生成的主体内容]，采用[主视觉风格]，融合[表现技法]与[媒介/材质纹理]。画面成分由[主体处理方式]、[背景/环境]、[图形元素/符号层]构成，采用[构图方式]与[分镜/镜头类型]，通过[空间逻辑/透视关系]建立画面张力。光影呈现[光影特质]，色调采用[色彩科学/色彩限定/冷暖关系]，整体具有[情绪与氛围]。画面带有[时代感/文化语境]，信息密度[密度描述]，留白[留白策略]，动态状态呈现[瞬时感/运动痕迹]。后期包含[数字痕迹/印刷痕迹/摄影痕迹]，并加入[符号化特征]作为抽象视觉语言。限制：不要复刻原图中的具体角色、文字、标志或情节；文字仅作为不可读的图形排版元素；保持原图的美学质感、构图逻辑、色彩关系和材质氛围。
```

## Compact Output Template

Use this when the user explicitly asks for a concise prompt:

```text
[在此处替换为您想要生成的主体内容]，采用[主风格]与[技法/材质]融合的视觉语言，[构图/镜头/透视]，[色彩科学]，[光影]，[信息密度/留白]，[动态状态]，[后期痕迹]，[符号化特征]，整体氛围[情绪]；不要复刻原图具体角色、文字、标志或情节，只保留可迁移的美学质感。
```
