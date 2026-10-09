# Tabugattas.github.io
Tarek & Elen's Wedding Website — live at https://tabugattas.github.io


Plain HTML/CSS/JS, no build step. Open `index.html` through any static host (GitHub Pages, Netlify, etc.).

- Page 1 (envelope): Clicking the **wax seal** (T&E) opens page 2 and starts the music.
- Page 2: music autoplays (no visible player), live countdown, mailing-address button, **< GO BACK** returns to page 1 and stops the music.

## Things to edit

| What | Where |
|---|---|
| Google Sheet link, YouTube/MP3 music, wedding date | `js/config.js` |
| Song file (if using MP3) | replace `audio/song.mp3` (current file is a placeholder tone) |
| Photos | replace the files in `images/` and keep the same names |

### Images (replace with your originals, same file names)

| File | Used for | Suggested size |
|---|---|---|
| `hero-photo.jpg` | couple photo in Save the Date row | portrait, ~3:5 (e.g. 1200×2000) |
| `hero-background.jpg` | full-width background behind it (blue door) | wide, 2400px+ |
| `passport-background.jpg` | linen background behind the passport card | 1600 wide |
| `strip-1.jpg`, `strip-2.jpg`, `strip-3.jpg` | the three photos in the photo strip (top → bottom), auto-centered & cropped | ~1:1 (e.g. 1000×920) |
| `countdown-background.jpg` / `countdown-card.jpg` | rings background (blurred) / lace card | 1600 wide / 1080×2070 |
| `final-background.jpg` / `final-photo.jpg` | faded background / Santorini photo card | 1600 wide / 1080×2070 |

Section backgrounds get a white wash in CSS (`--fade` in `css/style.css`), so use the normal, un-faded photos.

The current placeholders were cut from the reference screenshots (`tools/make_placeholders.py`), so they are low resolution.

### Music notes
Browsers only allow sound after a click/tap. Because the visitor clicks the wax seal, music starts right away. If someone opens the `#invitation` link directly, the music starts on their first tap. MP3 works more reliably than YouTube, especially on iPhone.

### Passport card
The passport card (passport, envelope, seal, heart, flowers, ribbon) is drawn in the editable SVG at `partials/passport-art.svg` and exported to `images/passport-art.webp`. The three strip photos are shown in black & white; to show them in colour, remove `filter="url(#pp-bw)"` from the three `<image>` tags in the source and regenerate the export.

### Delivery assets
The live page uses `images/*.webp` for smaller downloads; the JPEG originals are retained. When replacing a photo, regenerate its matching WebP file as well. Typography is served from local Latin-subset WOFF2 files in `fonts/`; their licenses are included in `fonts/LICENSES.txt`.

CSS and JavaScript links in `index.html` carry content-hash version queries. Refresh the corresponding version when editing those files so returning visitors receive the current revision. Mobile sections retain their natural artwork proportions; desktop sections fill one viewport.

The envelope layers and passport illustration are pre-rendered from the editable SVG files in `partials/` so mobile browsers do not calculate noise, lighting, and shadows during the opening. After editing these SVG sources or the strip photos, regenerate the delivery images with `node tools/render_static_art.cjs` (requires Playwright/Chromium and Python/Pillow; an optional Chromium executable path can be passed as the first argument). These are developer tools, not a website build requirement.
