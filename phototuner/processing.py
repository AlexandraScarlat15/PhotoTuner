import cv2
import numpy as np

def enhance_image(image, mode='standard'):
    image = image.copy()

    if mode == 'natural':
        
        image = cv2.bilateralFilter(image, 5, 50, 50)
        image = cv2.convertScaleAbs(image, alpha=1.05, beta=5)

    elif mode == 'vivid':
        sharpen_kernel = np.array([[0, -1, 0],
                                   [-1, 5.5, -1],
                                   [0, -1, 0]])
        image = cv2.filter2D(image, -1, sharpen_kernel)

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.add(s, 40)
        v = cv2.add(v, 10)
        vivid = cv2.merge([h, s, v])
        image = cv2.cvtColor(vivid, cv2.COLOR_HSV2RGB)

    elif mode == 'pro':
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)
        lab_clahe = cv2.merge((l_clahe, a, b))
        image = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)

        image = cv2.bilateralFilter(image, 9, 75, 75)

        sharpen_kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
        image = cv2.filter2D(image, -1, sharpen_kernel)

    else:
        image = cv2.GaussianBlur(image, (3, 3), 0)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        image = cv2.filter2D(image, -1, kernel)

    return image

def enhance_image_accurate(img, sharpen_strength=1.0, contrast=1.0, color_boost=0):
    import cv2
    import numpy as np

    sharpen_strength = max(0.0, min(sharpen_strength, 5.0))
    contrast = max(0.5, min(contrast, 2.0))
    color_boost = max(0, min(color_boost, 100))

    gamma = 1.0 / contrast
    lut = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
    img = cv2.LUT(img, lut)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s.astype(np.int32) + int(color_boost), 0, 255).astype(np.uint8)
    img = cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2RGB)

    if sharpen_strength > 0:
        kernel = np.array([[0, -1, 0],
                           [-1, 5 + sharpen_strength, -1],
                           [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    return img
