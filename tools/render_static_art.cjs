// Render the existing vector artwork once, so phones animate cached images.
// Requires Playwright with Chromium and Python 3 with Pillow.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const os = require('node:os');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const artwork = [
  { name: 'envelope-back', width: 1568, height: 788, scale: 2, quality: 85 },
  { name: 'envelope-front', width: 1568, height: 788, scale: 2, quality: 85 },
  { name: 'envelope-flap', width: 1568, height: 788, scale: 2, quality: 85 },
  { name: 'passport-art', width: 882, height: 1800, scale: 1, quality: 88 },
];
(async () => {
  const server = http.createServer((req, res) => {
    const file = path.resolve(root, '.' + new URL(req.url, 'http://localhost').pathname);
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      res.writeHead(404).end();
      return;
    }
    const mime = { '.css': 'text/css', '.woff2': 'font/woff2', '.webp': 'image/webp' };
    res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'wedding-art-'));
  let browser;
  try {
    browser = await chromium.launch({ executablePath: process.argv[2] || undefined });
    for (const art of artwork) {
      const page = await browser.newPage({ viewport: { width: art.width, height: art.height }, deviceScaleFactor: art.scale });
      const svg = fs.readFileSync(path.join(root, 'partials', art.name + '.svg'), 'utf8');
      await page.setContent(`<base href="${base}"><link rel="stylesheet" href="css/fonts.css"><style>*{margin:0}svg{display:block;width:${art.width}px;height:${art.height}px;overflow:visible}</style>${svg}`, { waitUntil: 'networkidle' });
      await page.evaluate(() => document.fonts.ready);
      const png = path.join(temp, art.name + '.png');
      await page.screenshot({ path: png, omitBackground: true });
      execFileSync('python3', ['-c', 'from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2],"WEBP",quality=int(sys.argv[3]),method=6)', png, path.join(root, 'images', art.name + '.webp'), String(art.quality)]);
      await page.close();
    }
  } finally {
    if (browser) await browser.close();
    server.close();
    fs.rmSync(temp, { recursive: true, force: true });
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
