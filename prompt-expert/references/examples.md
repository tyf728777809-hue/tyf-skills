# Examples

Use these examples to calibrate output behavior. They are not style limits.

## Example 1: Text Request Produces Three Candidates

User:

```text
帮我写一个 deepseek v4 拟人化动漫女性角色宣传海报的提示词。
```

Expected behavior:

- Use Mode A.
- Internally apply the 7 control dimensions and 15 visual dimensions.
- Output three candidates: 推荐方向, 更大胆方向, 更克制方向.
- Each candidate includes a copyable Chinese prompt and a short breakdown.
- The skill chooses style, composition, color, material, mood, and constraints without asking the user to choose.
- Do not show the internal 7+15 analysis unless the user asks for the breakdown.

Shape:

````markdown
## 推荐方向

```text
生成一张 DeepSeek v4 拟人化动漫女性角色宣传海报，角色以动态半身或全身姿态作为核心视觉焦点，采用俄国构成主义与现代极简矢量插画融合的视觉语言...
```

拆解：俄构几何结构 + 三色限定 + 丝网印刷颗粒，适合表现 AI 产品的工业力量感与品牌识别。
````

## Example 2: Subject Reference Does Not Inherit Style

User:

```text
参考这张人物图里的角色，帮我写一张现代海报 prompt。
```

Expected behavior:

- If the wording clearly points to the character/person/subject, use subject reference mode.
- Preserve identity, silhouette, hair, outfit, pose logic, and recognizable traits.
- Treat the image as subject input only.
- Internally apply the 7 control dimensions and 15 visual dimensions to redesign the aesthetic system.
- Do not inherit the reference image's style, composition, color, lighting, material, mood, era, perspective, density, post-processing, or symbolic language unless the user explicitly asks for that too.

Required phrase:

```text
参考图仅用于识别主体，不继承参考图的画风、构图、配色、光影、材质或后期效果。
```

## Example 3: Style Reference Produces One Universal Prompt

User:

```text
这张图做得很好，请反推它的视觉风格，生成通用 prompt。
```

Expected behavior:

- Use Mode B.
- Internally analyze all 15 dimensions.
- Use the 7 control dimensions to make the extracted style reusable, subject-replaceable, and stable.
- Output one complete Chinese prompt only, plus the short save question.
- Do not output the analysis process.
- Do not keep original character, readable text, logo, IP name, or plot.
- The only bracketed placeholder in the prompt is `[在此处替换为您想要生成的主体内容]`.

Shape:

```text
[在此处替换为您想要生成的主体内容]，采用现代极简平面海报与数字故障艺术融合的视觉语言，画面由错位矩形视窗、透明切片、细密扫描线和大面积纯色负空间构成...
```

```text
要把这个风格配方保存到 skill 里以后复用吗？
```

## Example 4: Save Confirmed Creates Registry Entry

User:

```text
保存，以后叫它蓝白故障天空风。
```

Expected behavior:

- Append one entry to `references/style_recipe_registry.md`.
- Save only reusable style recipe information.
- Do not include original image, character name, readable text, logo, or plot.

Shape:

````markdown
## 蓝白故障天空风

- Tags: 数字故障, Pixel Sorting, 克莱因蓝, 白色负空间, 矩形视窗, 积云纹理, 冷静忧郁
- Visual thesis: 用蓝白极简空间和故障窗口切片制造清澈但疏离的数字天空感。
- Use for: 二次元角色海报, AI 品牌视觉, 音乐封面, 数字空间感插画
- Avoid for: 写实纪实摄影, 暖色复古广告, 高密度朋克拼贴
- Prompt:
```text
[在此处替换为您想要生成的主体内容]，采用现代极简平面设计与数字故障艺术融合的视觉语言...
```
````
