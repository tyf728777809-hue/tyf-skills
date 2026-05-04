# Style Recipe Registry

This file stores reusable visual style recipes confirmed by the user. Do not add entries automatically after every reverse-engineering run. Append a recipe only after the user explicitly confirms saving, such as "保存", "沉淀", "以后复用", or "加入 skill".

## Save Rules

- Save only transferable aesthetics: style system, composition logic, color logic, material/texture, lighting, mood, post-processing, symbolic language, and constraints.
- Do not save original images, specific character names, IP names, real names, logos, readable text, watermarks, or plot details.
- The only bracketed placeholder allowed in a saved prompt is `[在此处替换为您想要生成的主体内容]`.
- Replace all other template placeholders before saving.
- Prefer concise recipe names that can be matched by natural language later.

## Match Rules

When the user asks to reuse a previous style, match against:

- Recipe name
- Tags
- Visual thesis
- Use for / Avoid for
- Distinctive phrases inside the prompt

If one recipe clearly matches, use it directly. If several match, ask the user to choose by recipe name. If none match, fall back to fresh prompt design.

## Entry Format

````markdown
## <中文短名称>

- Tags: <风格标签、色彩、构图、材质、氛围>
- Visual thesis: <一句话视觉命题>
- Use for: <适合的主体/场景>
- Avoid for: <不适合的场景>
- Prompt:
```text
[在此处替换为您想要生成的主体内容]，...
```
````

## Saved Recipes

No saved recipes yet.

