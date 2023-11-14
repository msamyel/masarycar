import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import argparse

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO


def get_webcam_image(url, image_alt_text):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the image tag with the specified alt text
        img_tags = soup.find_all('img', alt=image_alt_text)

        # Check if the image tag was found
        if len(img_tags)>0:
            # the first few results are a small icon of a webcam, a fake
            # only get the last one
            img_tag = img_tags[-1]

            # Get the source (src) attribute of the image tag
            img_src = img_tag.get('src')

            # Join the image URL with the base URL of the page to get the absolute URL
            absolute_img_url = urljoin(url, img_src)

            # Download the image
            img_response = requests.get(absolute_img_url)

            # Check if the image download was successful
            if img_response.status_code == 200:
                # Save the image to a file
                return img_response.content
                return Image.open(BytesIO(img_response.content))
                # with open('downloaded_image.jpg', 'wb') as img_file:
                #     img_file.write(img_response.content)
                # print(f"Image downloaded successfully: {absolute_img_url}")
            else:
                print(f"Failed to download image. Status code: {img_response.status_code}")
        else:
            print(f"Image with alt text '{image_alt_text}' not found on the page.")
    else:
        print(f"Failed to fetch URL. Status code: {response.status_code}")
    return None


def get_image(filename):
    return Image.open(filename)


def crop_image(image, crop_rect):
    left, top, right, bottom = (int(x) for x in crop_rect.split(','))
    return image.crop((left, top, right, bottom))


def apply_mask(image, mask_filename):
    image_to_apply_mask = image.copy()
    mask = Image.open(mask_filename)
    image_to_apply_mask.paste(mask, (0, 0), mask)
    return image_to_apply_mask


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


def detect_cars(original_image, corrected_image, detection_xml, is_apply_corrections):
    original_image_arr = np.array(original_image)
    corrected_image_arr = np.array(corrected_image)

    if int(is_apply_corrections):
        corrected_image_arr = apply_image_corrections(corrected_image_arr)

    car_cascade = cv2.CascadeClassifier(detection_xml)

    cars = car_cascade.detectMultiScale(corrected_image_arr, 1.1, 1)
    cnt = 0
    for (x, y, w, h) in cars:
        cv2.rectangle(original_image_arr, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cnt += 1
    print(cnt, "cars found")

    return original_image_arr


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-f", "--file", help="path to image to use", default="__none")
    arg_parser.add_argument("-c", "--croprect", help="left,top,right,bottom", default="193,440,529,954")
    arg_parser.add_argument("-m", "--mask", help="path to mask file", required=True)
    arg_parser.add_argument("-u", "--scaleup", help="scale of original picture magnify", default=1)
    arg_parser.add_argument("-a", "--apply-corrections", help="1/0 to apply corrections to original image", default=1)
    arg_parser.add_argument("-d", "--detection", help="path to detection XML", required=True)
    args = arg_parser.parse_args()

    if args.file == "__none":
        image_content = get_webcam_image("https://www.masarycka.com/cs/online-kamera/", "Online kamera")
        if image_content is None:
            return
        image = Image.open(BytesIO(image_content))
    else:
        image = get_image(args.file)

    cropped_image = crop_image(image, args.croprect)
    masked_image = apply_mask(cropped_image, args.mask)
    resized_image = resize_image(masked_image, args.scaleup)
    original_resized_image = resize_image(cropped_image, args.scaleup)
    detection_img = detect_cars(original_resized_image, resized_image, args.detection, args.apply_corrections)

    plt.imshow(detection_img, interpolation='nearest')
    plt.show()


if __name__ == '__main__':
    main()
