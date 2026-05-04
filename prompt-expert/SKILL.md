---
name: 提示词专家
description: "Use when the user asks to write, improve, or generate image prompts for AI image generation, including Chinese requests like 帮我写提示词, 写生图 prompt, 根据参考图写 prompt, 角色海报提示词, 风格化海报, 插画提示词, 封面提示词, or visual prompt exploration. Also use when the user provides an image they think is visually good and asks to analyze, reverse-engineer, extract, or generalize its style into a reusable prompt. The skill should select style, composition, shot type, lighting, color, material, mood, post-processing, symbols, and constraints for the user instead of asking them to choose. Distinguish subject-reference images from style-reference images."
---

# 提示词专家

## Purpose

Write high-quality Chinese prompts for image generation. The user does not need to know art terms; infer the visual direction from their goal and choose an effective aesthetic recipe.

Default target is a general image generation model, not Midjourney or SDXL. Add platform-specific syntax only when the user asks for it.

## Hard Rules

- **Image role triage:** Classify every provided image before writing. It is either a subject reference, a style reference, or an edit target.
  - If the user says 修改, 替换, 保持原图, 在图上改, remove, edit, inpaint, or preserve the original image while changing part of it, classify as **edit target**.
  - If the user says 这张图做得好, 风格, 质感, 反推, 提取美学, 通用 prompt, style reference, or asks why the image works visually, classify as **style reference**.
  - If the user says 参考这个人, 这个角色, 主体, 服装, 发型, 姿态, 表情, identity, or character reference, classify as **subject reference**.
  - If the user only says "参考这张图写 prompt" and the role cannot be inferred, ask exactly one question: "这张图是参考主体，还是参考风格？"
- **Subject reference rule:** If the user provides an image to identify or preserve a person/character/object, use it only for the subject: identity, silhouette, pose logic, hair, outfit, recognizable design traits, and expression cues. Do not inherit the image's style, composition, color palette, lighting, material, texture, era, mood, or post-processing unless explicitly requested.
- **Style reference rule:** If the user says the image is a good example, asks to analyze/反推/提取风格/保留质感/生成通用 prompt, treat it as a style reference. Strip the original subject, specific characters, text, logos, plot, and unique story details. Preserve only the aesthetic system.
- **Universal design framework:** Every mode must internally consider 7 control dimensions plus 15 visual dimensions. The 7 controls are use case, subject fidelity, style hierarchy, visual thesis, typography/text policy, model stability strategy, and negative constraints. The 15 visual dimensions are image style, components, composition, shot/storyboard type, lighting, tone/color science, medium/material texture, mood, render/camera parameters, era/cultural context, spatial logic/perspective, information density/negative space, dynamic state, post-processing/digital traces, and symbolic features.
- **No hard mapping:** Do not bind a subject type to one fixed style. Use the aesthetic library as decision support, not a template cage.
- **Creative coherence:** Each prompt should have one dominant visual thesis. Combine styles only when their roles are clear, such as "flat vector foreground + photographic background" or "Swiss grid structure + punk texture layer".
- **Ask rarely:** If the subject and output intent are usable, make tasteful assumptions. Ask only when the missing detail would fundamentally change the subject or cannot be inferred.
- **Do not generate images by default:** This skill writes prompts. If the user explicitly asks to generate the image, use the image generation workflow after writing or confirming the prompt.

## Workflow

### Mode A: Write or Improve Prompts

1. Parse the request:
   - Subject: person, character, object, brand, scene, product, poster, cover, UI, space, etc.
   - Intended use: poster, key visual, cover, avatar, concept art, ad, social graphic, wallpaper, product mockup.
   - Required content: names, exact text, reference image role, aspect ratio, must-keep details.
   - Constraints: safe depiction, no text, avoid ordinary standing pose, keep subject recognizable, etc.

2. Establish the 7 control dimensions:
   - Use case: poster, key visual, cover, avatar, product ad, wallpaper, social graphic, concept art, etc.
   - Subject fidelity: exact identity, recognizable traits, loose mood, or fully replaceable subject.
   - Style hierarchy: main style, supporting technique, surface/material layer, post-processing layer.
   - Visual thesis: one sentence that explains what the image is trying to express.
   - Typography/text policy: no text, abstract unreadable type, readable title, magazine layout, vertical type, etc.
   - Model stability strategy: simplify or constrain anything likely to cause subject loss, color drift, unreadable text, or excessive clutter.
   - Negative constraints: failure modes specific to the chosen recipe.

3. Design the 15 visual dimensions:
   - For pure text requests, design all 15 dimensions proactively.
   - For subject-reference images, take only subject identity/shape/outfit/pose cues from the image; design all aesthetic dimensions independently unless the user explicitly asks to inherit them.
   - For style-reference images, reverse-engineer the 15 dimensions from the image and generalize them.
   - For saved recipes, inherit the recipe's aesthetic system and fill gaps for the new subject/use case.

4. Form a visual thesis:
   - Write an internal one-sentence goal, such as "cold futuristic solitude", "aggressive underground poster", "quiet summer digital melancholy", or "luxury ritual object".
   - Use that thesis to choose dimensions, not the other way around.

5. Load references only as needed:
   - `references/aesthetic_decision_matrix.md`: use for soft aesthetic judgment and dimension selection.
   - `references/style_library_v1.md`: use only when broader style vocabulary is needed. Prefer `rg -n '^#|关键词|<topic>' references/style_library_v1.md` or the heading index; do not load the full file by default.
   - `references/prompt_patterns.md`: use for output templates and reusable prompt structures.
   - `references/style_reverse_engineering.md`: use when reverse-engineering style from an image.
   - `references/style_recipe_registry.md`: use first when the user asks to reuse a saved style, previous style, or named visual recipe.
   - `references/examples.md`: use when output behavior is uncertain or needs calibration.

6. Produce the output:
   - Default: 3 candidate prompts.
   - Candidate roles: recommended direction, bolder experimental direction, restrained/polished direction.
   - For each candidate, include a directly copyable prompt and a short breakdown of why the aesthetic choices fit.
   - If the user explicitly asks for one prompt, provide one strongest prompt plus a short rationale.
   - Do not show the 7+15 framework as a checklist unless the user asks to see the analysis.

### Mode B: Reverse-Engineer Style From a Good Image

Use this mode when the user provides an image as a style reference, for example "这张图做得好", "分析这张图的视觉风格", "反推 prompt", "提取美学灵魂", or "生成通用风格 prompt".

Mode B overrides Mode A. Do not output three candidates, a breakdown, or the 15-dimension analysis unless the user explicitly asks for them.

Required behavior:

- Act as a top AI image prompt expert.
- Before expanding into the 15 dimensions, perform an internal **高权重视觉信号校准**: identify the subject treatment, core art/design movement, composition mechanism, color limitation, material/post-processing system, and emotional atmosphere. These six signals set output priority; the 15 dimensions fill gaps and constraints rather than receiving equal prompt length.
- Inspect the image across all 15 dimensions: image style, image components, composition, shot/storyboard type, lighting, tone and color science, medium/material texture, mood and atmosphere, render/camera parameters, era and cultural context, spatial logic and perspective, information density and negative space, dynamic state or instantaneity, post-processing and digital traces, symbolic features.
- Use the 7 control dimensions to turn the image-specific analysis into a reusable, stable, subject-replaceable prompt.
- When the user provides the original prompt or nearby prompt evidence, use it only to calibrate which visual signals are likely high-weight. Do not change the generic style-recipe output format.
- Do not output the analysis unless the user asks for it.
- Output one complete, high-level Chinese prompt.
- Put `[在此处替换为您想要生成的主体内容]` at the beginning or core subject position.
- Remove original characters, text, logos, IP names, exact story events, and specific plot details.
- Preserve transferable aesthetics: structure, color logic, material, light, space, mood, camera/render behavior, digital traces, and constraints.
- Preserve only 2-4 representative low-weight decorative devices unless they are structurally central to the style; do not let corner labels, small UI marks, signatures, numbers, or one-off icons dominate the prompt.
- Include a constraint that any text from the original image should not be reproduced; typography may be described only as abstract graphic elements when it is central to the style.
- After the prompt, append one short save question: "要把这个风格配方保存到 skill 里以后复用吗？" If the user explicitly asks to only output the prompt, do not append the question.
- If the user confirms saving, append a new entry to `references/style_recipe_registry.md` using the registry format. Never save the original image, specific character/IP names, readable text, logos, or plot details.

### Mode C: Reuse Saved Style Recipes

Use this mode when the user says 用上次那个风格, 用之前保存的风格, 用某个质感, or describes a saved recipe naturally.

- Load `references/style_recipe_registry.md` first.
- Match by recipe name, tags, visual thesis, use cases, and avoid cases.
- If exactly one high-confidence recipe matches, reuse its prompt and replace only `[在此处替换为您想要生成的主体内容]` with the new subject, then lightly adapt constraints if needed.
- Apply the 7 control dimensions to the new use case and fill any missing visual dimensions from the saved recipe.
- If multiple recipes could match, list the matching recipe names and ask the user to choose.
- If no recipe matches, say no saved recipe matched and fall back to Mode A.

## Mode A Output Format

````markdown
## 推荐方向

```text
[可直接复制的完整中文 prompt]
```

拆解：[主风格] + [构图] + [色彩] + [材质/后期] + [氛围]，一句话说明为什么适合。

## 更大胆方向

```text
[可直接复制的完整中文 prompt]
```

拆解：[说明]

## 更克制方向

```text
[可直接复制的完整中文 prompt]
```

拆解：[说明]
````

## Style Reverse-Engineering Output Format

For style-reference images, output the prompt only, plus the short save question unless the user asked for prompt-only output:

```text
[在此处替换为您想要生成的主体内容]，[完整通用中文提示词，覆盖风格、成分、构图、分镜、光影、色彩、材质、氛围、参数、时代文化、空间透视、信息密度、动态状态、后期痕迹、符号化特征与限制]
```

要把这个风格配方保存到 skill 里以后复用吗？

## Prompt Quality Checklist

Before finalizing, ensure the prompt includes:

- Subject is concrete and visually actionable.
- Use case is clear enough for the prompt structure.
- Subject fidelity is explicit when a reference image or known character is involved.
- Visual thesis is coherent and not just a pile of style tags.
- Style hierarchy is clear: main style, supporting technique, surface/material layer, and post-processing layer.
- Style stack has a clear hierarchy: main style, supporting technique, medium/material.
- Composition is explicit: framing, layout, perspective, and information density.
- Color system is controlled: two-color, three-color, complementary, muted, high saturation, film color grade, etc.
- Lighting is specific: hard light, soft light, backlight, noon sunlight, neon reflection, low-key, high-key, etc.
- Texture and post-processing are concrete: halftone, risograph, screen print, film grain, pixel sorting, RGB shift, chromatic aberration, paper wear, etc.
- Mood is coherent with the visual system.
- Typography/text policy is safe: no random text unless text is explicitly required; abstract text must be unreadable graphic texture.
- Model stability is protected: subject silhouette, color limits, complexity, and failure modes are controlled.
- Negative constraints prevent common failures: ordinary frontal pose, messy background, random text, style leakage from reference image, low-resolution face, extra subject, excessive color noise.
