# Aesthetic Decision Matrix

This reference is a soft judgment system. It should expand creative choice, not restrict it.

## Core Principle

Do not use fixed mappings like "anime character must use cel shading" or "AI product must use blue gradients". Instead:

```text
user need -> visual thesis -> aesthetic signals -> dimension choices -> coherent prompt
```

Good prompts usually combine:

```text
subject + main style + technique + medium/material + composition + lighting + color system + mood + constraints
```

## Control Dimensions

Use these 7 upper-level controls before choosing visual details. They explain why the image should look a certain way and prevent the prompt from becoming a style-word list.

1. **Use case / delivery goal:** poster, character key visual, album cover, social cover, avatar, product ad, wallpaper, concept art, UI mockup, packaging, etc. The use case determines density, framing, text strategy, and polish level.
2. **Subject fidelity / replaceability:** decide whether the subject must be exact, only recognizable, loosely inspired, or fully replaceable. For subject-reference images, this is the only dimension primarily supplied by the image.
3. **Style hierarchy:** assign each style signal a job: main style, supporting technique, surface/material layer, and post-processing layer. Avoid equal-weight style stacking.
4. **Visual thesis:** one sentence that states what the image expresses, such as "a cold AI system as a solitary modern icon" or "a rebellious underground poster frozen at the moment of intrusion".
5. **Typography / text policy:** no text, abstract unreadable type, readable title, magazine cover layout, vertical type, technical labels, or poster typography. Prevent random text unless exact text is requested.
6. **Model stability strategy:** constrain color count, simplify background, protect subject silhouette, keep text unreadable if not exact, reduce conflicting styles, and prevent effects from swallowing the subject.
7. **Negative constraints / failure modes:** style-specific avoid rules, such as "glitch must not obscure the face", "minimalism must not become empty", "Riso wear must not become dirty", or "subject reference must not leak style".

## Universal 15-Dimension Framework

Every prompt mode should consider these dimensions internally. Do not output them as a table unless the user asks for analysis.

1. **Image style:** design/art family and dominant visual language.
2. **Image components:** subject, background, graphic elements, symbolic layers, texture layers.
3. **Composition:** centered, diagonal, radial, grid, collage, window overlay, negative space, full bleed, etc.
4. **Shot/storyboard type:** full body, medium shot, close-up, low angle, Dutch angle, animation still, poster key visual, etc.
5. **Lighting:** hard/soft, high-key/low-key, backlight, rim light, neon reflection, golden hour, blue hour, flat graphic light.
6. **Tone and color science:** monochrome, duotone, tritone, complementary, analogous, saturation, cold/warm contrast, print spot colors.
7. **Medium/material texture:** vector, cel shading, line art, Riso, screen print, paper, film grain, chrome, glass, watercolor, photo blur.
8. **Mood and atmosphere:** lonely, sacred, melancholic, rebellious, elegant, playful, oppressive, dreamy, documentary, futuristic.
9. **Render/camera parameters:** lens feel, focal length, depth of field, motion blur, exposure, render type, edge quality.
10. **Era and cultural context:** Art Deco, retro, Soviet/Eastern European, Y2K, punk zine, Japanese minimalism, oriental futurism, contemporary editorial.
11. **Spatial logic and perspective:** one/two/three-point perspective, orthographic, isometric, fisheye, telephoto compression, impossible space, layered depth.
12. **Information density and negative space:** sparse, balanced, dense, controlled chaos, subject readability.
13. **Dynamic state / instantaneity:** still, suspended instant, impact frame, wind, falling, reaching, motion trail, glitch displacement.
14. **Post-processing and digital traces:** pixel sorting, RGB shift, chromatic aberration, JPEG blocks, CRT scanlines, halftone, scratches, light leak.
15. **Symbolic features:** labels, arrows, halos, frames, windows, grids, barcodes, stamps, warning marks, technical annotations, abstract typography.

## Dimension Source by Mode

| Mode | Subject source | 7 control dimensions | 15 visual dimensions |
|---|---|---|---|
| Pure text prompt | User request plus inferred intent | Designed by the skill | Designed by the skill |
| Subject-reference image | Image provides identity, silhouette, outfit, pose logic, recognizable traits | Designed by the skill unless user specifies otherwise | Designed by the skill; do not inherit from the image unless explicitly requested |
| Style-reference image | Original subject is stripped and generalized | Used to make the style reusable and stable | Reverse-engineered from the image, then generalized |
| Saved recipe reuse | New user subject replaces the placeholder | Inherited from recipe and adapted to new use case | Inherited from recipe; fill missing dimensions for the new subject |

## Decision Dimensions

### 1. Image Style

Choose a dominant style and 1-2 supporting styles.

Useful families:

- Modern graphic design: minimalism, Swiss Style, Bauhaus, Constructivism, De Stijl, brutalism, neo-brutalism, anti-design, editorial design.
- Poster and print: vintage poster, propaganda poster, Riso, screen print, letterpress, newspaper print, punk zine, grunge, pop art, halftone.
- Illustration: flat illustration, vector art, cel-shaded anime, retro anime, comic style, manga screentone, editorial illustration, concept art, line art.
- Mixed media: line drawing over photography, collage, torn paper, paper texture, digital overlay, photographic background plus flat foreground.
- Digital aesthetics: cyberpunk, pixel sorting, glitch art, old web, Windows 95, Frutiger Aero, Y2K chrome, holographic, FUI/HUD.
- Cultural and era context: Art Deco, Art Nouveau, Renaissance, Baroque, ukiyo-e, ink painting, Dunhuang mural, guochao, oriental futurism, retrofuturism.

### 2. Image Components

Decide what the image is made of:

- Main subject only: clean hero image, icon-like, suitable for strong posters.
- Subject + symbolic environment: subject carries narrative through a few meaningful objects or graphic signs.
- Subject + abstract visual system: geometry, type blocks, grids, windows, slices, halftone, data fragments.
- Foreground/background contrast: flat line art foreground with photographic background; detailed subject against empty space.
- Layered collage: multiple panels, paper fragments, windows, stickers, labels, scans, textures.

### 3. Composition

Choose composition to control energy:

- Centered: stable, product-like, iconic, ritual.
- Symmetrical: ceremonial, luxury, sacred, formal.
- Asymmetrical: modern, editorial, tense, intelligent.
- Diagonal: motion, conflict, speed, industrial force.
- Radial: attack, explosion, propaganda, pop impact.
- Grid-based: rational, Swiss, editorial, technology, system.
- Window overlay: digital space, memory, fragmented identity.
- Split screen: contrast, duality, before/after, parallel worlds.
- Full bleed: immersive, cinematic, editorial.
- Negative space: quiet, premium, lonely, poetic.
- High-density collage: punk, rave, maximalist, underground, overloaded information.

### 4. Shot Type and Framing

Use shot language when the prompt needs visual direction:

- Establishing wide shot: worldbuilding, architecture, large environment.
- Full body: fashion, character design, action pose, poster silhouette.
- Medium shot: character poster, expression + body language balance.
- Close-up: emotion, identity, product detail.
- Extreme close-up: tension, luxury detail, sensory impact.
- Low angle: power, monumentality, heroism, pressure.
- High angle: vulnerability, surveillance, loneliness.
- Dutch angle: instability, dreaminess, unease, speed.
- First-person view: immersion, immediacy.
- Animation storyboard frame: dynamic narrative moment, not static posing.

### 5. Lighting

Select light as a mood engine:

- Hard noon light: clean, sharp, summer, surreal, high contrast.
- Soft diffused light: gentle, lifestyle, romantic, calm.
- Low-key light: suspense, luxury, noir, pressure.
- High-key light: clean, commercial, airy, medical, beauty.
- Backlight/rim light: silhouette, divinity, stage presence.
- Neon reflection: cyberpunk, nightlife, urban digital.
- Golden hour: nostalgia, warmth, memory, farewell.
- Blue hour: melancholy, cinematic quiet, city solitude.
- Direct flash: youth culture, fashion snapshot, Y2K, party.
- Volumetric light: sacred, mysterious, atmospheric.
- Flat graphic light: poster, vector, screen print, comic.

### 6. Tone and Color Science

Control color through relationships, not only names:

- Monochrome: disciplined, iconic, severe.
- Duotone: clean, memorable, brand-like.
- Three-color limit: poster strength, print realism, high control.
- Complementary colors: conflict, energy, commercial impact.
- Split complementary: rich but still controlled.
- Analogous colors: harmony, softness, atmosphere.
- High saturation: pop, youth, speed, advertising.
- Low saturation: premium, documentary, poetic, quiet.
- Cold/warm contrast: cinematic depth, emotional duality.
- CMYK/Riso spot colors: print feel, independent publishing.
- Klein blue + white: cold modernity, summer clarity, digital purity.
- Black/white/orange: punk, alarm, underground, threat.
- Teal-orange film grade: cinematic but use sparingly to avoid generic output.
- Bleach bypass: harsh realism, steel, war, documentary tension.

### 7. Medium, Material, and Texture

Use material to make the image feel physically produced:

- Print: screen print, risograph, offset, newspaper, letterpress, halftone, ink bleed.
- Paper: aged paper, torn paper, fiber texture, folded poster, worn edges.
- Drawing: pencil, ink, charcoal, white line art, engraving, etching.
- Paint: watercolor, oil, acrylic, gouache, airbrush.
- Digital: pixel sorting, RGB shift, scanlines, compression blocks, UI overlay.
- Product material: chrome, brushed metal, translucent plastic, frosted glass, rubber, ceramic, carbon fiber, holographic foil.
- Space material: concrete, wood, marble, fabric, lacquer, glass, smoke, liquid.

### 8. Mood and Atmosphere

Pick one primary mood and one secondary tension:

- Quiet, clean, lonely, sacred, nostalgic, dreamy, melancholic.
- Rebellious, oppressive, aggressive, industrial, chaotic, underground.
- Light, fashionable, playful, fresh, summery, urban.
- Luxurious, ritualistic, mysterious, precise, futuristic.
- Documentary, raw, intimate, lo-fi, memory-like.

### 9. Render or Camera Parameters

Use only when they help:

- Illustration/render: vector, flat color, hard-edge shadow, cel shading, NPR, isometric, low poly, clay 3D, collectible figure render.
- Photography: focal length, wide angle, telephoto compression, macro, shallow depth of field, film grain, motion blur, long exposure.
- Poster output: high contrast, sharp edges, clean silhouette, print texture, no random text, balanced negative space.

## Advanced Dimensions

### Era and Cultural Context

Use era/culture as a meaning layer:

- 1920s Art Deco: luxury, jazz, gold geometry.
- 1950s retro: consumer optimism, kitchen appliances, soft advertising colors.
- 1970s: warm print, music poster, grain, analog nostalgia.
- 1980s neon: synthwave, arcade, grid, night drive.
- 1990s: magazine, grunge, zine, raw youth culture.
- Y2K: chrome, transparent plastic, early internet, glossy tech.
- Soviet/Eastern European graphic language: severe geometry, propaganda tension, red/black contrast.
- Japanese minimalism/wabi-sabi: quiet, natural, incomplete, restrained.
- Oriental futurism: traditional signs plus future technology.

### Spatial Logic and Perspective

Use space to make the image memorable:

- One-point perspective: corridor, road, tunnel, focus and destiny.
- Two-point perspective: architecture, product, urban space.
- Three-point perspective: skyscrapers, low-angle hero tension.
- Orthographic/axonometric: diagrams, technical clarity, system thinking.
- Fisheye/wide-angle distortion: pressure, youth culture, surreal intrusion.
- Telephoto compression: dense city, fashion editorial, surveillance.
- Impossible space: surrealism, dreamcore, conceptual posters.
- Layered foreground/midground/background: cinematic depth.
- Transparent windows/cutaways: inner world, memory, digital identity.

### Information Density and Negative Space

Choose density deliberately:

- Very low density: luxury, meditation, solitude, premium tech.
- Medium density: editorial, character poster, balanced commercial visual.
- High density: punk, rave, cyber, maximalism, zine, information overload.
- Controlled chaos: dense texture but clear subject silhouette.

### Dynamic State

Avoid static posing when the user asks for energy:

- Turning back, falling, reaching, sprinting, floating, leaning, wind-blown clothing.
- Freeze-frame impact, time slice, motion blur, afterimage, speed lines.
- Glitch displacement, pixel tear, scanline drift, window offset.
- Suspended instant: object or character caught between motion and stillness.

### Post-processing and Digital Traces

Use post-processing as a design layer:

- Pixel sorting, RGB shift, chromatic aberration, datamoshing.
- JPEG blocks, CRT scanlines, analog TV distortion, VHS noise.
- Film grain, dust, scratches, light leak, overexposure bloom.
- Poster wear, ink misregistration, halftone rosette, rough screen print.
- UI overlays, barcode labels, coordinate grids, warning marks.

### Symbolic Features

Use symbols sparingly and purposefully:

- Barcode, serial number, warning label, arrows, industrial marks.
- Stamp, ticket, map line, coordinate grid, measuring marks.
- Halo, spotlight circle, geometric arch, flag, starburst.
- Transparent window, torn paper edge, rectangular slices, data panels.
- Typography as image: large sans-serif title, vertical type, grid labels, tiny technical annotation.

## Creative Selection Rules

- Pick a dominant axis first: calm vs explosive, clean vs textured, flat vs dimensional, nostalgic vs futuristic, commercial vs experimental.
- Use contrast intentionally: flat subject + realistic background, minimal color + rich texture, calm mood + sharp geometry.
- Avoid stacking too many style names. Three well-chosen style signals usually beat ten unrelated tags.
- If mixing styles, assign each one a job:
  - Structure: Swiss grid, Constructivism, diagonal composition.
  - Surface: Riso, halftone, paper wear, film grain.
  - Mood: blue hour, lo-fi, cyberpunk, wabi-sabi.
  - Subject rendering: cel shading, line art, vector, photography.
- Preserve subject recognizability before aesthetic complexity.

## Common Need Signals

- Tech, intelligence, AI, precision: Swiss grid, minimalism, Constructivism, cold duotone, technical labels, hard edges.
- Summer, clarity, solitude: Klein blue, pure white, hard noon light, negative space, low-angle sky, cel shading.
- Digital melancholy: window overlay, glitch art, pixel sorting, RGB shift, blue sky/cloud contrast, clean background.
- Rebellion, underground, pressure: punk zine, brutalism, halftone, black/white/orange, torn collage, wide-angle distortion.
- Luxury, ritual, premium: symmetry, low density, Art Deco or minimal luxury, black/gold/cream, soft spotlight, refined material.
- Nostalgia, memory, dream: film grain, Polaroid, lo-fi photography, golden hour, soft focus, worn paper.
- Product clarity: centered composition, controlled studio light, clean surface material, minimal background, exact object silhouette.
