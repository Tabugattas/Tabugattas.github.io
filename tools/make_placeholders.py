import cv2, numpy as np
A = cv2.imread('/home/ubuntu/attachments/1c7d5645-67a9-452f-b24a-870968c5d8fb/image.png')
B = cv2.imread('/home/ubuntu/attachments/6693eeea-6a76-44e1-aa8c-57a58dae5cc3/image.png')
S = 1920/1568
OUT = '/home/ubuntu/wedding-site/images/'

def crop(img, x0, y0, x1, y1):
    return img[int(y0*S):int(y1*S), int(x0*S):int(x1*S)].copy()

def text_mask(img, thresh=28, dil=3):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bl = cv2.GaussianBlur(g, (0, 0), 6)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = (np.abs(g - bl) > thresh).astype(np.uint8)
    return cv2.dilate(m, np.ones((dil, dil), np.uint8), iterations=2)

def rect_mask(img, rects):
    m = np.zeros(img.shape[:2], np.uint8)
    for (x0, y0, x1, y1) in rects:
        m[int(y0):int(y1), int(x0):int(x1)] = 1
    return m

def unfade(img, a):
    # screenshots show backgrounds behind a white veil of opacity a; undo it so CSS can re-apply
    f = (img.astype(np.float32) - 255*a) / (1 - a)
    return np.clip(f, 0, 255).astype(np.uint8)

def up(img, w):
    h = int(img.shape[0] * w / img.shape[1])
    r = cv2.resize(img, (w, h), interpolation=cv2.INTER_LANCZOS4)
    bl = cv2.GaussianBlur(r, (0, 0), 1.2)
    return cv2.addWeighted(r, 1.4, bl, -0.4, 0)

def save(name, img, q=88):
    cv2.imwrite(OUT + name, img, [cv2.IMWRITE_JPEG_QUALITY, q])
    print(name, img.shape[1], 'x', img.shape[0])

# Hero: couple photo
save('hero-photo.jpg', up(crop(A, 684, 67, 815, 287), 640))

# Hero background: whole strip, photo area replaced with door texture, text inpainted
hb = crop(A, 3, 67, 1552, 287)
ox = lambda x: int((x - 3) * S)
pw = ox(816) - ox(683)
src = hb[:, ox(683) - pw:ox(683)].copy()
hb[:, ox(683):ox(683) + pw] = src
m = rect_mask(hb, [(ox(812), 0, ox(925), hb.shape[0])]) & text_mask(hb, 14, 3)
m |= rect_mask(hb, [(ox(680), 0, ox(688), hb.shape[0]), (ox(812), 0, ox(820), hb.shape[0])])
hb = cv2.inpaint(hb, m * 255, 9, cv2.INPAINT_TELEA)
hb = cv2.GaussianBlur(hb, (0, 0), 2)
save('hero-background.jpg', up(hb, 2400))

# Music strip background
mb = crop(A, 3, 289, 1552, 347)
mm = rect_mask(mb, [(ox(722), 0, ox(834), mb.shape[0])])
mb = cv2.inpaint(mb, mm * 255, 15, cv2.INPAINT_TELEA)
mb = cv2.GaussianBlur(mb, (0, 0), 1.5)
save('music-background.jpg', up(mb, 2400))

# Passport section
save('passport-background.jpg', up(unfade(crop(A, 3, 350, 716, 592), 0.35), 1600))
pc = crop(A, 718, 349, 838, 592)
cy = lambda y: int((y - 349) * S)
pm = rect_mask(pc, [(0, cy(546), pc.shape[1], pc.shape[0])]) & text_mask(pc, 10, 3)
pc = cv2.inpaint(pc, pm * 255, 7, cv2.INPAINT_TELEA)
save('passport-card.jpg', up(pc, 720))

# Countdown section
save('countdown-background.jpg', up(unfade(crop(A, 840, 594, 1552, 822), 0.35), 1600))
cc = crop(A, 718, 594, 838, 823)
cm = text_mask(cc, 9, 3)
cc = cv2.inpaint(cc, cm * 255, 9, cv2.INPAINT_TELEA)
cc = cv2.GaussianBlur(cc, (0, 0), 1.2)
save('countdown-card.jpg', up(cc, 720))

# Final section
save('final-background.jpg', up(unfade(crop(B, 3, 602, 716, 831), 0.45), 1600))
fc = crop(B, 718, 601, 838, 831)
fy = lambda y: int((y - 601) * S)
fm = rect_mask(fc, [(0, 0, fc.shape[1], fy(660)), (0, fy(800), fc.shape[1], fy(822))]) & text_mask(fc, 8, 3)
fc = cv2.inpaint(fc, fm * 255, 9, cv2.INPAINT_TELEA)
save('final-photo.jpg', up(fc, 720))
