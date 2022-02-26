# Google_OCR
google ocr for FYDP

# usage:
    1. run ```pip install -r requirements.txt```
    2. run ```python3.8 parse.py```

# layout:
    |---- README.md
          requirements.txt
          gg_api.py (used for primitive google api testing --- depreciated)
          google_sheet.py (google's code base for enabling google sheet --- not used for now)
          parser.py (MAINLY file used for OCR processing and data formatting)
          notebook.ipynb (testing case for pre-image processing --- might need in the end)

          custom-utility-341701-330efe16ea40.json ( !!!!!!  JSON FILE for API USAGE !!!!!!!!)
    |---- tests
          images for testing 
          PLEASE use costco.JPG  and 1.JPG for parser.py test  -------- at line 21 for input selection


#response.text_annotations gives the description and the xy location on the image
# to do:
'''
   send JSON body to mongodb remote via api calls (to do)

   extra: match item name with the ingredients info (to do)
     
'''


