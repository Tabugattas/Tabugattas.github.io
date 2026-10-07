"""Generates partials/passport-card.svg (the coded passport collage) and the three strip placeholder photos."""
import math, cv2

W, H = 882, 1800  # card is u wide, 2.04u tall

# ---------- heart scallops ----------
def heart_pt(t, s, cx, cy):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return cx + x * s, cy - y * s

def heart_path(s, cx, cy, n=120):
    pts = [heart_pt(2 * math.pi * i / n, s, cx, cy) for i in range(n)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def scallops(s, cx, cy, r, step):
    # evenly spaced circles along the heart outline
    pts, n = [], 2000
    raw = [heart_pt(2 * math.pi * i / n, s, cx, cy) for i in range(n)]
    acc, last = 0, raw[0]
    pts.append(last)
    for p in raw[1:]:
        acc += math.dist(p, last); last = p
        if acc >= step:
            pts.append(p); acc = 0
    return "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>' for x, y in pts), pts

HCX, HCY = 572, 1165
outer_s, inner_s = 12.6, 9.4
sc_circles, sc_pts = scallops(outer_s, HCX, HCY, 30, 34)
ruffle_lines = "".join(
    f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{HCX + (x - HCX) * .78:.1f}" y2="{HCY - 20 + (y - HCY + 20) * .78:.1f}"/>'
    for x, y in sc_pts)

PLANE = "M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"

def petal(cx, cy, rx, ry, rot, fill="url(#petal)"):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" fill="{fill}" stroke="#e6dccb" stroke-width="1.2"/>'

rose = "".join([
    petal(116, 500, 52, 30, -12), petal(156, 482, 42, 28, 38), petal(80, 478, 40, 26, -58),
    petal(150, 506, 40, 22, -18), petal(92, 508, 38, 22, 16),
    petal(134, 456, 38, 28, 12), petal(100, 458, 34, 26, -30), petal(122, 446, 28, 22, 0),
    petal(124, 478, 34, 26, 20, "url(#petalIn)"), petal(112, 484, 24, 18, -35, "url(#petalIn)"),
    petal(132, 470, 18, 14, 50, "url(#petalIn)"),
    '<circle cx="121" cy="478" r="8" fill="#ead8a0" opacity=".85"/>',
    '<path d="M100 470 C110 462 128 462 140 470" fill="none" stroke="#e2d6bf" stroke-width="1.5"/>',
])

def lily(x, y, rot, s=1):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            '<path d="M0 0 C-30 -10 -48 -42 -40 -70 C-22 -60 -8 -60 0 -78 C8 -60 22 -60 40 -70 C48 -42 30 -10 0 0Z" fill="url(#petal)" stroke="#e2d8c6" stroke-width="1.2"/>'
            '<path d="M0 -6 C-14 -20 -18 -44 -12 -60 M0 -6 C14 -20 18 -44 12 -60" fill="none" stroke="#e8dfcf" stroke-width="1.2"/>'
            '<path d="M0 -4 L2 -40" stroke="#e8cf6a" stroke-width="4" stroke-linecap="round"/>'
            '<path d="M0 0 C2 10 0 22 -4 30" fill="none" stroke="#8fa77a" stroke-width="7" stroke-linecap="round"/>'
            '</g>')

svg = f'''<svg class="passport-art" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>
    <linearGradient id="pp-bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4eee8"/><stop offset=".55" stop-color="#f1e8de"/><stop offset="1" stop-color="#efe3d4"/>
    </linearGradient>
    <filter id="pp-linen" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9 0.012" numOctaves="2" seed="3" result="a"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.9" numOctaves="2" seed="5" result="b"/>
      <feBlend in="a" in2="b" mode="multiply" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .35  0 0 0 -.9 .62" result="tint"/>
      <feComposite in="tint" in2="SourceGraphic" operator="in" result="t"/>
      <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="t"/></feMerge>
    </filter>
    <filter id="pp-soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="18"/></filter>
    <filter id="pp-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="3" dy="8" stdDeviation="9" flood-color="#6d5b44" flood-opacity=".28"/>
    </filter>
    <filter id="pp-shadow-sm" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#5d4e3a" flood-opacity=".3"/>
    </filter>
    <filter id="pp-emboss" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="-1.2" dy="-1.2" stdDeviation=".5" flood-color="#fff" flood-opacity=".95" result="h"/>
      <feDropShadow dx="1.5" dy="1.8" stdDeviation=".8" flood-color="#8d7a5c" flood-opacity=".65"/>
    </filter>
    <filter id="pp-paper" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="9" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 .4  0 0 0 0 .4  0 0 0 0 .4  0 0 0 -1.2 .75" result="g"/>
      <feComposite in="g" in2="SourceGraphic" operator="in" result="t"/>
      <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="t"/></feMerge>
    </filter>
    <filter id="pp-bw"><feColorMatrix type="saturate" values="0"/></filter>
    <linearGradient id="pp-cover" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#e3e1dd"/><stop offset=".5" stop-color="#d9d6d1"/><stop offset="1" stop-color="#cfccc6"/>
    </linearGradient>
    <linearGradient id="pp-env-back" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#c2c6cc"/><stop offset="1" stop-color="#babfc6"/>
    </linearGradient>
    <linearGradient id="pp-env-front" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d1d4d9"/><stop offset="1" stop-color="#c8ccd2"/>
    </linearGradient>
    <radialGradient id="pp-wax" cx="38%" cy="32%" r="75%">
      <stop offset="0" stop-color="#faf5ea"/><stop offset=".6" stop-color="#ebe0cc"/><stop offset="1" stop-color="#d3c3a6"/>
    </radialGradient>
    <radialGradient id="pp-cushion" cx="45%" cy="40%" r="65%">
      <stop offset="0" stop-color="#fbf6ec"/><stop offset=".7" stop-color="#f1e6d3"/><stop offset="1" stop-color="#e2d2b8"/>
    </radialGradient>
    <radialGradient id="pp-ruffle" cx="50%" cy="45%" r="60%">
      <stop offset=".6" stop-color="#efe3cf"/><stop offset="1" stop-color="#e4d4b9"/>
    </radialGradient>
    <linearGradient id="pp-gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#e8cd94"/><stop offset=".5" stop-color="#b98d4d"/><stop offset="1" stop-color="#ddbf82"/>
    </linearGradient>
    <radialGradient id="petal" cx="40%" cy="35%" r="80%">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#f6f1e7"/><stop offset="1" stop-color="#e3dac8"/>
    </radialGradient>
    <radialGradient id="petalIn" cx="50%" cy="50%" r="70%">
      <stop offset="0" stop-color="#f3ead6"/><stop offset="1" stop-color="#fbf8f1"/>
    </radialGradient>
    <clipPath id="pp-ph1"><rect x="0" y="0" width="212" height="196"/></clipPath>
  </defs>

  <!-- linen background + silk -->
  <rect width="{W}" height="{H}" fill="url(#pp-bg)" filter="url(#pp-linen)"/>
  <g filter="url(#pp-soft)" fill="#fff" opacity=".5" transform="rotate(-8 441 1300)">
    <path d="M-40 1060 C140 1000 300 1090 460 1040 C620 990 760 1060 940 1010 L940 1090 C760 1140 620 1070 460 1120 C300 1170 140 1080 -40 1140Z"/>
    <path d="M-40 1300 C160 1230 330 1330 500 1270 C670 1210 790 1290 940 1240 L940 1320 C790 1370 670 1290 500 1350 C330 1410 160 1310 -40 1380Z" opacity=".8"/>
    <path d="M-40 1560 C160 1500 330 1590 520 1530 C700 1470 800 1550 940 1510 L940 1610 C800 1650 700 1570 520 1630 C330 1690 160 1600 -40 1660Z" opacity=".7"/>
  </g>

  <!-- envelope back -->
  <g filter="url(#pp-shadow)">
    <rect x="158" y="548" width="632" height="502" rx="4" fill="url(#pp-env-back)"/>
  </g>
  <path d="M170 560 L480 790 L778 560Z" fill="#ece3d4"/>

  <!-- photo strip -->
  <g transform="rotate(1.6 665 390)" filter="url(#pp-shadow-sm)">
    <rect x="532" y="62" width="262" height="648" fill="#fbfbfa"/>
    <text x="543" y="98" font-size="11" fill="#555" font-family="Arial">&#x25AA;&#x25AA;</text>
    <text x="772" y="330" font-size="11" fill="#555" font-family="Arial">&#x25AA;&#x25AA;</text>
    <g transform="translate(557 78)"><rect width="212" height="196" fill="#bbb"/>
      <image href="images/strip-1.jpg" width="212" height="196" preserveAspectRatio="xMidYMid slice" clip-path="url(#pp-ph1)" filter="url(#pp-bw)"/></g>
    <g transform="translate(557 288)"><rect width="212" height="196" fill="#bbb"/>
      <image href="images/strip-2.jpg" width="212" height="196" preserveAspectRatio="xMidYMid slice" clip-path="url(#pp-ph1)" filter="url(#pp-bw)"/></g>
    <g transform="translate(557 498)"><rect width="212" height="196" fill="#bbb"/>
      <image href="images/strip-3.jpg" width="212" height="196" preserveAspectRatio="xMidYMid slice" clip-path="url(#pp-ph1)" filter="url(#pp-bw)"/></g>
  </g>

  <!-- passport -->
  <g transform="rotate(-2.5 355 425)" filter="url(#pp-shadow)">
    <rect x="148" y="160" width="412" height="530" rx="24" fill="url(#pp-cover)" filter="url(#pp-paper)"/>
    <rect x="148" y="160" width="26" height="530" rx="12" fill="#fff" opacity=".35"/>
    <rect x="160" y="172" width="388" height="506" rx="16" fill="none" stroke="#f3f1ec" stroke-width="2" stroke-dasharray="7 6" opacity=".9"/>
    <g fill="#4a4846">
      <text x="355" y="268" text-anchor="middle" font-family="Ms Madi, cursive" font-size="92" stroke="#4a4846" stroke-width="1.6">Wedding</text>
      <text x="358" y="330" text-anchor="middle" font-family="Cormorant SC, serif" font-weight="600" font-size="34" letter-spacing="4">PASSPORT</text>
      <ellipse cx="370" cy="455" rx="108" ry="98" fill="none" stroke="#5a5856" stroke-width="1.6"/>
      <path d="M262 515 C300 495 360 520 420 540 C470 556 520 548 548 532" fill="none" stroke="#4a4846" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M392 360 C420 352 452 356 470 340" fill="none" stroke="#4a4846" stroke-width="2.2" stroke-linecap="round"/>
      <text x="338" y="470" text-anchor="middle" font-family="Pinyon Script, cursive" font-size="150">T</text>
      <text x="402" y="532" text-anchor="middle" font-family="Cormorant Garamond, serif" font-weight="500" font-size="132">E</text>
      <g stroke="#4a4846" stroke-width="2" fill="#4a4846">
        <path d="M262 545 C276 530 292 522 308 520" fill="none"/>
        <ellipse cx="274" cy="526" rx="9" ry="4" transform="rotate(-40 274 526)"/>
        <ellipse cx="288" cy="518" rx="9" ry="4" transform="rotate(-50 288 518)"/>
        <ellipse cx="282" cy="540" rx="9" ry="4" transform="rotate(20 282 540)"/>
        <ellipse cx="298" cy="532" rx="9" ry="4" transform="rotate(10 298 532)"/>
      </g>
      <text x="376" y="642" text-anchor="middle" font-family="Cormorant SC, serif" font-weight="700" font-size="28" letter-spacing="4">ARMENIA</text>
    </g>
  </g>

  <!-- rose (behind the front pocket) -->
  <path d="M150 520 C180 560 210 590 240 640" fill="none" stroke="#7f9a6c" stroke-width="5" stroke-linecap="round"/>
  <path d="M168 548 C150 540 128 552 112 590 C140 588 160 572 168 548Z" fill="#8aa576"/>
  <path d="M190 560 C200 534 222 520 240 516 C236 540 214 556 190 560Z" fill="#9ab285"/>
  <g filter="url(#pp-shadow-sm)">{rose}</g>

  <!-- envelope front pocket -->
  <g filter="url(#pp-shadow-sm)">
    <path d="M158 566 L480 800 L790 562 L790 1050 L158 1050Z" fill="url(#pp-env-front)"/>
  </g>
  <path d="M158 1050 L430 830 M790 1050 L530 830" stroke="#dde1e7" stroke-width="2" opacity=".8"/>
  <path d="M480 800 C440 760 400 720 352 690" fill="none" stroke="url(#pp-gold)" stroke-width="2.2"/>

  <!-- wax seal -->
  <g filter="url(#pp-shadow-sm)">
    <path fill="url(#pp-wax)" d="M480 732 C520 730 552 760 553 802 C555 842 524 874 482 875 C440 877 408 846 407 804 C406 762 440 733 480 732Z"/>
  </g>
  <circle cx="480" cy="804" r="50" fill="none" stroke="#e3d6bf" stroke-width="3" filter="url(#pp-emboss)"/>
  <g transform="translate(480 806) scale(2.6) translate(-12 -12)" fill="#ece2d0" filter="url(#pp-emboss)"><path d="{PLANE}"/></g>

  <!-- calla lilies + ribbon -->
  <g fill="none" stroke-linecap="round" filter="url(#pp-shadow-sm)">
    <path d="M110 1440 C170 1400 240 1395 300 1345 C318 1330 330 1350 318 1362 C300 1380 280 1350 300 1345 C350 1385 400 1420 470 1428" stroke="#e7e1d6" stroke-width="9"/>
    <path d="M110 1440 C170 1400 240 1395 300 1345 C318 1330 330 1350 318 1362 C300 1380 280 1350 300 1345 C350 1385 400 1420 470 1428" stroke="#fdfcf9" stroke-width="6"/>
    <path d="M300 1345 C290 1395 268 1430 240 1470" stroke="#e7e1d6" stroke-width="9"/>
    <path d="M300 1345 C290 1395 268 1430 240 1470" stroke="#fdfcf9" stroke-width="6"/>
  </g>
  <path d="M262 1150 C276 1220 290 1280 300 1350 M300 1210 C304 1260 304 1300 300 1350" fill="none" stroke="#8fa77a" stroke-width="7" stroke-linecap="round"/>
  <g filter="url(#pp-shadow-sm)">
    {lily(250, 1150, -25, 1.05)}
    {lily(300, 1225, 15, .95)}
  </g>

  <!-- ruffled heart -->
  <g filter="url(#pp-shadow)">
    <g fill="url(#pp-ruffle)">{sc_circles}<path d="{heart_path(outer_s, HCX, HCY)}"/></g>
  </g>
  <g stroke="#dccbaf" stroke-width="1.5" opacity=".3">{ruffle_lines}</g>
  <g filter="url(#pp-shadow-sm)">
    <path d="{heart_path(inner_s, HCX, HCY - 10)}" fill="url(#pp-cushion)"/>
  </g>
  <g fill="#4d4a46" font-family="Cormorant SC, serif" text-anchor="middle">
    <text x="{HCX}" y="1140" font-size="27" font-weight="600" letter-spacing="5">SAVE OUR DATE</text>
    <text x="{HCX}" y="1196" font-size="40" font-weight="600" letter-spacing="6">07.22.2027</text>
  </g>
  <path d="M492 1236 C540 1262 600 1272 626 1252 C640 1240 630 1222 616 1228 C600 1236 612 1256 628 1248 C650 1238 670 1236 690 1240" fill="none" stroke="url(#pp-gold)" stroke-width="2"/>
  <g transform="translate(478 1228) rotate(-70) scale(1.6) translate(-12 -12)" fill="url(#pp-gold)"><path d="{PLANE}"/></g>
</svg>'''
open('/home/ubuntu/wedding-site/partials/passport-card.svg', 'w').write(svg)

# ---------- strip placeholders (cut from the reference screenshot) ----------
A = cv2.imread('/home/ubuntu/attachments/1c7d5645-67a9-452f-b24a-870968c5d8fb/image.png')
S = 1920 / 1568
ox, oy = 718 * S, 349 * S
for i, (x0, y0, x1, y1) in enumerate([(557, 82, 768, 278), (552, 292, 760, 488), (545, 505, 752, 702)], 1):
    im = A[int(oy + y0 / 6):int(oy + y1 / 6), int(ox + x0 / 6):int(ox + x1 / 6)]
    im = cv2.resize(im, (640, int(640 * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(f'/home/ubuntu/wedding-site/images/strip-{i}.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
print('ok')
