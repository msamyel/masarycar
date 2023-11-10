import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import argparse


def get_image(filename):
    return Image.open(filename)


def crop_image(image, crop_rect):
    left, top, right, bottom = (int(x) for x in crop_rect.split(','))
    return image.crop((left, top, right, bottom))

def apply_mask(image, mask_filename):
    mask = Image.open(mask_filename)
    image.paste(mask, (0, 0), mask)
    return image

def resize_image(image, scaleup):
    width, height = image.size
    scaleup_int = int(scaleup)
    return image.resize((width * scaleup_int, height * scaleup_int))

def apply_image_corrections(image_as_array):
    grey = cv2.cvtColor(image_as_array, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    dilated = cv2.dilate(blur, np.ones((3, 3)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
    return closing

def detect_cars(image, detection_xml, is_apply_corrections):
    original_image = np.array(image)
    image_arr = original_image.copy()

    if int(is_apply_corrections):
        image_arr = apply_image_corrections(image_arr)

    car_cascade = cv2.CascadeClassifier(detection_xml)

    cars = car_cascade.detectMultiScale(image_arr, 1.1, 1)
    cnt = 0
    for (x, y, w, h) in cars:
        cv2.rectangle(original_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cnt += 1
    print(cnt, "cars found")

    return original_image


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-f", "--file", help="path to image to use")
    arg_parser.add_argument("-c", "--croprect", help="left,top,right,bottom")
    arg_parser.add_argument("-m", "--mask", help="path to mask file")
    arg_parser.add_argument("-u", "--scaleup", help="scale of original picture magnify")
    arg_parser.add_argument("-a", "--apply-corrections", help="1/0 to apply corrections to original image")
    arg_parser.add_argument("-d", "--detection", help="path to detection XML")
    args = arg_parser.parse_args()

    image = get_image(args.file)
    cropped_image = crop_image(image, args.croprect)
    masked_image = apply_mask(cropped_image, args.mask)
    resized_image = resize_image(masked_image, args.scaleup)
    detection_img = detect_cars(resized_image, args.detection, args.apply_corrections)

    plt.imshow(detection_img, interpolation='nearest')
    plt.show()




if __name__ == '__main__':
    main()
