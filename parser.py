# ********************* Package Part **********************************
from google.cloud import vision
import io
import os
from collections import Counter
import re 
import pandas as pd

#----------------------
#| runs in python 3.8 |
#----------------------

# USING GOOGLE VISION API TO READ TEXT FROM RECEIPTS PART *********************
# ********************* API Part **********************************

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/zp_macmini/Desktop/Google_OCR/custom-utility-341701-330efe16ea40.json"

  
client = vision.ImageAnnotatorClient()

with io.open('tests/costco.JPG', 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)


response = client.document_text_detection(image=image)
labels = response.label_annotations

# print('Start:')
# print(response.text_annotations[0].description)
case = response.text_annotations[0].description.split("\n")




# this parser is used independently for both google api and google ocr cloud server request
# in case of using only one of the above in the future
# ********************* REGEX Part **********************************
# ---------------------Costco---------------------------
re_costco = 'Costco|COSTCO|costco|TPD'
re_costco_start_slice = 'TN Member'
re_costco_end_slice = 'SUBTOTAL'
re_costco_item = '\d{3,}\s[0-9A-Z/%.]+ *[ *0-9A-Z/%]*'
re_costco_prefix = '[\d{3,}]+ '
# ---------------------TNT-------------------------------
re_walmart = 'Walmart|walmart|WALMART'
re_tnt = 'T&T|t&t|tnt'
re_tnt_start_slice = 'GROCERY|Grocery|grocery'
re_tnt_end_slice = 'SERVICE COUNTER|service counter|Service Counter'
re_tnt_remove_item = '\$|FOOD|PRODUCE|DELI'


# ********************* Code Part **********************************

def store_name(source):
    for i in source:
        if re.findall(re_tnt, i):
            return "T&T"
        # if re.findall(re_walmart, i):
        #     return "Walmart"
        if re.findall(re_costco, i):
            return "Costco"
    return "store_name_not_detected"
    # currently not reading other receipts 


def text_clean_up(source,store):
    # locate specific words for clean up with items left only
    start = -1 
    end = -1
    cleaned_source = []
    poplist = []
    
    if store == "T&T":
        source = isEnglish(source)
        for index in range(len(source)):
            if re.findall(re_tnt_start_slice, source[index]):
                start = index   
            if re.findall(re_tnt_end_slice, source[index]):
                end = index
        #print(start,end,"<---")
        cleaned_source = source[start+1:end-len(poplist)]
        
    elif store == 'Costco':
        for index in range(len(source)):
            #print(index,"   :  " ,source[index])
            if re.findall(re_costco_start_slice, source[index]):
                start = index   
            if re.findall(re_costco_end_slice, source[index]):
                end = index
            if 'TPD' in source[index]:
                poplist.append(index)
        poplist.reverse()
        #print(start,end,"<---")
        for ind in poplist:
            del source[ind]
        cleaned_source = source[start+1:end-len(poplist)]
            
    return cleaned_source


def regex_parser(source):
    store = store_name(source)
    res = text_clean_up(source,store)
    if store == 'Costco':
        r = re.compile(re_costco_item)
        newlist = list(filter(r.match, res))
        newlist = [re.sub(re_costco_prefix,'',i.rstrip('1234567890.')).lower() for i in newlist]
    if store == 'T&T':
        # not using regex, simply iterate again
        newlist =[]
        for line in res:
            if line.find('$') != -1 or line.find('FOOD') != -1  or line.find('DELI') != -1 or line.find('PRODUCE') != -1 :
                continue
            else:
                newlist.append(line.replace('(SALE) ','').lower())
    return newlist


# we need : {item_name, item_quantity, unit of measurement, best_before_date}

def isEnglish(source):
    # for TNT especially
    # input source is the entire list format
    # output the s is the english or not
    en_only = []
    for s in source:
        if s.isascii():
            en_only.append(s)
    return en_only
  

def list_dataframe_json(uncounted_item_list):
    newlist = uncounted_item_list
    ct = Counter(newlist)
    ctdf = pd.DataFrame.from_records(list(dict(ct).items()), columns=['Item','Quantity'])
    ctdf['Measure'] = ['piece'] * ctdf.shape[0]
    ctdf['Best_Before'] = ['1 week'] * ctdf.shape[0]
    return ctdf

def df_json(df):
    # directly return json body
    json = df.to_json(orient='records')[1:-1].replace('},{', '} {')


    # in case of obtain the json file
    # use:

    # with open('json.txt', 'w') as f:
    #     f.write(out)
    # df.to_json('temp.json', orient='records', lines=True)
    return json

def flow(source):
    # entire process flow for examples:
    ####-----  FLOW  -----####
    '''
    1: fetch images into GOOGLE vision API
    2: obtain the results for store matchup
    3: if TNT then
        3.1 remove all non-english words
        3.2 determine start-end point
        3.3 parse by removing extra useless information 
        3.4 construct item-quantity table and fill in pre-determined information 
        3.5 convert to JSON format
       if Costco then
        3.6 determine start-end point
        3.7 remove discounts information
        3.8 remove item numbers in parsing process
        3.9 construct item-quantity table and fill in pre-determined information 
        3.10 convert to JSON format
    4: send JSON body to mongodb remote via api calls (to do)

    extra: match item name with the ingredients info (to do)

    '''
    ####-----  FLOW  -----####
    item = regex_parser(source)
    df = list_dataframe_json(item)
    json = df_json(df)
    return json


print(type(case))

print(flow(case))

