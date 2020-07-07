import pytesseract
import math
import re
import imutils
import cv2
import numpy as np
from scipy import ndimage


from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
from keras_retinanet import models

def img_inference_direct(img_infer):
    img_infer = read_image_bgr(img_infer)
    img = img_infer.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    config = ("-l eng --oem 1 --psm 6")
    text = pytesseract.image_to_string(img, config=config)
    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    return text




def img_inference(img_infer, model):

    THRES_SCORE = 0.95
    draw = img_infer
    image = img_infer
    ##################################################

    src_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    Threshold = 100
    canny_output = cv2.Canny(src_gray, 100, 100, apertureSize=3)

    lines = cv2.HoughLinesP(canny_output, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[0]:
            cv2.line(src_gray, (x1, y1), (x2, y2), (255, 0, 0), 3)
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) - 180
            angles.append(angle)

        median_angle = np.median(angles)
        if (median_angle % 90) - 90 > 5:
            image = ndimage.rotate(image, median_angle, reshape=True)
            draw = ndimage.rotate(draw, median_angle, reshape=True)
    ##################################################

    # preprocess image for network
    image = preprocess_image(image)
    image, scale = resize_image(image)
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

    # correct for image scale
    boxes /= scale

    output_dict = {}
    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < THRES_SCORE:
            break

        color = label_color(label)

        b = box.astype(int)
        draw_box(draw, b, color=color)

    return b, draw

def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated

def Image_Crop(b,img):
    crop_img_initial = img[b[1]:b[3], b[0]:b[2]]
    angle = 0
    ratio = 1
    if crop_img_initial.shape[1] < crop_img_initial.shape[0]:
        osd_data = pytesseract.image_to_osd(crop_img_initial)
        angle = int(re.search('(?<=Rotate: )\d+', osd_data).group(0))

    crop_img = rotate(crop_img_initial, angle)

    (H1, W1) = crop_img.shape[:2]
    ratio = crop_img.shape[0] / 420.0
    crop_img = imutils.resize(crop_img, height=420)

    (H1, W1) = crop_img.shape[:2]

    startX = 0
    endX = int(W1 * .7)
    startY = 0
    endY = H1
    crop_img = crop_img[startY:endY, startX:endX]
    return crop_img
