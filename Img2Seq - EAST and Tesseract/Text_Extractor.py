# import the necessary packages
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import argparse
import cv2
import os
import numpy as np
import json

def text_extractor(mode, filename):
    # Load the example image and convert it to grayscale
    image = cv2.imread(filename)
    gray_tot = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = ""

    if(mode == "tot"):
        height, width = gray_tot.shape
        gray = gray_tot[0:height, 0:width]

    # If mode "title" is choosen, the text detector will create a crop box
    # at the top of the input image. The width will constantly be the width of the image,
    # and the height will increase gradually until text have been found.
    elif(mode == "title"):
        slides_start = 25
        while(text == "" and slides_start > 0):
            # Cropping the input image
            height_tot, width = gray_tot.shape
            height = round (height_tot / slides_start)
            gray = gray_tot[0:height, 0:width]

            # Saving the current cropped image in the right path
            filename_temp = mode + "_" + str(slides_start) + "_" + filename
            path_to_save = mode + "/" + filename_temp
            if not os.path.exists(mode + "/"):
                os.makedirs(mode + "/")
            cv2.imwrite(path_to_save, gray)

            # Applying the OCR algorithm on the current crop and return the text
            text = pytesseract.image_to_string(Image.open(path_to_save))

            # If text is still empty, next iteration the crop box will increase the dimension
            slides_start = slides_start - (slides_start/50)

        # The return will be the 1st string that has been found in the crop box        
        text = text.split("\n")[0]

    elif(mode == "full_text"):
        ######## ######## ######## ######## ######## ######## ########
        # Documentation: https://pypi.org/project/pytesseract/       #
        ######## ######## ######## ######## ######## ######## ########
        # Applying the OCR algorithm on the whole image and return the text
        text = pytesseract.image_to_string(Image.open(filename))
        coords = pytesseract.image_to_boxes(Image.open(filename))
        coords = coords.split("\n")
        
        ##### IT'S A PROBLEM WITH THE WITH SPACES BETWEEN THE WORDS. 
        ##### HAVE TO FIX...
        ##### CHECK THE DOCUMENTATION FOR ANOTHER METHOD
        
        # Finding the bounding box closest to the top of the data chart image
        temp_max = 0
        for bb in coords:
            bb = bb.split(" ")
            if(int(bb[4]) > temp_max):
                temp_max = int(bb[4])

        # Building the title based on all the BB that are close to the top
        temp_title = ""
        for bb in coords:
            bb = bb.split(" ")
            if(abs(temp_max - int(bb[4])) < 5):
                temp_title = temp_title + bb[0]
        print(temp_title)

    ##########################################################################################            
    # If mode "y_annotation" is choosen, the text detector will create a crop box
    # at the left of the input image. The height will constantly be the height of the image,
    # and the width will increase gradually until text have been found.
    elif(mode == "y_annotation"):
        slides_start = 50
        while(text == "" and slides_start > 0):
            # Cropping the input image
            height, width_tot = gray_tot.shape
            width = round(width_tot * 1 / slides_start)
            gray = gray_tot[0 : height, 0: width]
            gray = np.rot90(gray, 3)

            # Saving the current cropped image in the right path
            filename_temp = mode + "_" + str(slides_start) + "_" + filename
            path_to_save = mode + "/" + filename_temp
            if not os.path.exists(mode + "/"):
                os.makedirs(mode + "/")
            cv2.imwrite(path_to_save, gray)

            # Applying the OCR algorithm on the current crop and return the text
            text = pytesseract.image_to_string(Image.open(filename))

            # If text is still empty, next iteration the crop box will increase the dimension
            slides_start = slides_start - 5

        # The return will be the 1st string that has been found in the crop box        
        text = text.split("\n")[0]

    ##########################################################################################

    # If mode "x_annotation" is choosen, the text detector will create a crop box
    # at the bottom of the input image. The width will constantly be the width of the image,
    # and the height will increase gradually until text have been found.
    elif(mode == "x_annotation"):
        slides_start = 45
        # load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
        while(text == "" and slides_start > 0):
            # Cropping the input image
            height_tot, width = gray_tot.shape
            height = round(height_tot * slides_start / 50)
            gray = gray_tot[height : height_tot, 0:width]
            
            # Saving the current cropped image in the right path
            filename_temp = mode + "_" + str(slides_start) + "_" + filename
            path_to_save = mode + "/" + filename_temp
            if not os.path.exists(mode + "/"):
                os.makedirs(mode + "/")
            cv2.imwrite(path_to_save, gray)

            # Applying the OCR algorithm on the current crop and return the text
            text = pytesseract.image_to_string(Image.open(path_to_save))
        
            # If text is still empty, next iteration the crop box will increase the dimension
            slides_start = slides_start - 5

        # The return will be the 1st string that has been found in the crop box        
        text = text.split("\n")[-1]

    ##########################################################################################

    return text

def formal_description(input_image, title, x_annotation, y_annotation):
    # Generating the formal description through the JSON object
    formal_description = {
        "filename" : input_image,
        "title" : title,
        "x_annotation" : x_annotation,
        "y_annotation" : y_annotation
    }

    # Saving the JSON Object in the right path
    formal_description_name = input_image.split(".")[0] + ".json"
    if(not(os.path.isfile(formal_description_name))):
        file = open(formal_description_name, 'w+')
    with open(formal_description_name, 'w') as outfile:
        json.dump(formal_description, outfile)

#############
# DASHBOARD #
#############

path_to_images = "./../shared_data/"
images_list = [path_to_images + "test_line_asc.png", path_to_images + "test_weather.jpg"]

for input_image in images_list:

    # Extracting all the text from an input image
    full_text = text_extractor("full_text", input_image)

    # Detecting the title of the input image
    title = text_extractor("title", input_image)

    # Detecting the X axis annotation of the input image
    x_annotation = text_extractor("x_annotation", input_image)

    # Detecting the Y axis annotation of the input image
    y_annotation = text_extractor("y_annotation", input_image)

    # Saving the generated formal description in a JSON file
    formal_description(input_image, title, x_annotation, y_annotation)


