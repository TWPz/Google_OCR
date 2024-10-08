
from google.cloud import vision
import io
import os

import re #regex101.com
## runs in python 3.8
# USING GOOGLE VISION API TO READ TEXT FROM RECEIPTS PART *********************

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/zp_macmini/Desktop/Google_OCR/custom-utility-341701-330efe16ea40.json"

  
client = vision.ImageAnnotatorClient()

with io.open('tests/costco.JPG', 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)


response = client.document_text_detection(image=image)
labels = response.label_annotations

print('Start:')
#print(response.text_annotations[0].description)
print("-------------------")
print("type:", type(response.text_annotations[0].description))




texts = [text.description for text in response.text_annotations]
print(texts)
# print("ssssss")
# USING GOOGLE VISION API TO READ TEXT FROM RECEIPTS PART *********************

# res = '''CARE RITE PHARMACY
# SUNRISE, FL
# Lomita, CA
# **COPY RECEIPT*****
# CLERK
# 1 SWS MILK 1%
# 1 SODA DT 12PK
# i MCNX SVR CLD
# 2 CANDY C2 1.19E
# TAX: $0.00
# $3.29
# $5.79
# $16.49
# $4.76
# $30.00
# $30.00
# 5 TOTAL
# SWIPE
# 9/13/2018 05:30 PM
# 3598426 72617
# **COPY RECEIPT****
# THANK YOU'''

# print(res)


# money = '\$\d+(?:\.\d+)?'
# x = re.findall(money, res)
# print("regex ",x)

# import cv2
# import numpy as np
# from matplotlib import pyplot as plt

# # Read the image
# img = cv2.imread('test1.jpeg',0)
# # Simple thresholding
# ret,thresh1 = cv2.threshold(img,210,255,cv2.THRESH_BINARY)
# cv2.imshow('gray',thresh1)
# cv2.waitKey()

# suggestion 1: match the y coordinate for items with the price as well as the quantity for better matchup

# suggestion 2: look for the confidence for each character and do swap such as "i" to "1" at the lower confidence level

#response.text_annotations gives the description and the xy location on the image
# to do:
'''
    generalizing rules for general receipts data streaming

    clear out edge cases for better results

    parse the results as formulated data format

    upload / export to certain data files for post processing on Full Stack end
     
'''





def get_sorted_lines(response):
    document = response.full_text_annotation
    bounds = []
    for page in document.pages:
      for block in page.blocks:
        for paragraph in block.paragraphs:
           print("para", paragraph)
           for word in paragraph.words:
            for symbol in word.symbols:
              x = symbol.bounding_box.vertices[0].x
              y = symbol.bounding_box.vertices[0].y
              text = symbol.text
              bounds.append([x, y, text, symbol.bounding_box])
    bounds.sort(key=lambda x: x[1])
    old_y = -1
    line = []
    lines = []
    threshold = 1
    for bound in bounds:
      x = bound[0]
      y = bound[1]
      if old_y == -1:
        old_y = y
      elif old_y-threshold <= y <= old_y+threshold:
        old_y = y
      else:
        old_y = -1
        line.sort(key=lambda x: x[0])
        lines.append(line)
        line = []
      line.append(bound)
    line.sort(key=lambda x: x[0])
    lines.append(line)
    return lines

# print("---new -")
# lines = get_sorted_lines(response)
#print(lines)
# print("---new -")


# with open('cc.txt', 'w', encoding='utf-8') as f:
#     f.write(response.text_annotations[0].description)


# for line in lines:
#   texts = [i[2] for i in line]
#   texts = ''.join(texts)
#   bounds = [i[3] for i in line]
#   print(texts)


