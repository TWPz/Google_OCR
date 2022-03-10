# ********************* Package Part **********************************
from google.cloud import vision
import io
import os
from collections import Counter
import re
import pandas as pd
import datetime

#----------------------
#| runs in python 3.8 |
#----------------------

# USING GOOGLE VISION API TO READ TEXT FROM RECEIPTS PART *********************
# ********************* API Part **********************************

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/zp_macmini/Desktop/Google_OCR/ocrbackup-0da0a5fa15d7.json"


client = vision.ImageAnnotatorClient()

with io.open('tests/demo1.JPG', 'rb') as image_file:
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
# ---------------------walmart-------------------------------
re_walmart = 'Walmart|walmart|WALMART'
# ---------------------TNT-------------------------------
re_tnt = 'T&T|t&t|tnt'
re_tnt_start_alert_1 = 'ONLINE'
re_tnt_start_alert_6 = 'DELIVERY'
re_tnt_slice_1= 'GROCERY|Grocery|grocery|GR0CERY'
re_tnt_slice_2= 'FOOD|F000|F00d|F00D|food|Food'
re_tnt_slice_3= 'MEAT|meat|Meat|HEAT|Heat'
re_tnt_slice_4= 'SEAFOOD|seafood|SEAF000|SEAF00D'
re_tnt_slice_5= 'PRODUCE|produce|PR0DUCE'
re_tnt_slice_6= 'DELI|DELl|deli'
re_tnt_slice_7= 'SERVICE COUNTER|service counter|Service Counter|SERVICECOUNTER'

# re_tnt_remove_item = '\$|FOOD|PRODUCE|DELI|SEAFOOD|MEAT'
# #-------order-----
# GROCERY
# FOOD
# MEAT
# SEAFOOD
# PRODUCE
# DELI
# SERVICE COUNTER

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
            if len(re.findall(re_tnt_slice_1, source[index])) != 0 and start == -1 and len(re.findall(re_tnt_start_alert_1, source[index])) == 0:
                start = index
            elif len(re.findall(re_tnt_slice_2, source[index])) != 0  and start == -1:
                start = index
            elif len(re.findall(re_tnt_slice_3, source[index])) != 0  and start == -1:
                start = index
            elif len(re.findall(re_tnt_slice_4, source[index])) != 0  and start == -1:
                start = index
            elif len(re.findall(re_tnt_slice_5, source[index])) != 0  and start == -1:
                start = index
            elif len(re.findall(re_tnt_slice_6, source[index])) != 0  and start == -1 and len(re.findall(re_tnt_start_alert_6, source[index])) == 0:
                start = index
            if len(re.findall(re_tnt_slice_7, source[index])) != 0 and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_6, source[index])) != 0  and len(re.findall(re_tnt_start_alert_6, source[index])) == 0 and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_5, source[index])) != 0  and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_4, source[index])) != 0  and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_3, source[index])) != 0  and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_2, source[index])) != 0  and index != start:
                end = index
            elif len(re.findall(re_tnt_slice_1, source[index])) != 0  and len(re.findall(re_tnt_start_alert_1, source[index])) == 0 and index != start:
                end = index
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
            # #-------order-----
            # GROCERY
            # FOOD
            # MEAT
            # SEAFOOD
            # PRODUCE
            # DELI
            if line.find('FOOD') == 0  or line.find('DELI') == 0 or line.find('PRODUCE') == 0 or line.find('MEAT') == 0 or line.find('SEAFOOD') == 0 or line.find('GROCERY') == 0:
                continue
            else:
                newlist.append(line.replace('(SALE) ','').lower())
    for i in newlist:
        print("-------------", i)
    return newlist,store


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

def item_final_clean_before_df(items,store):
    if store == 'T&T':
    # after parser before df
    # purify data in case of failure in OCR engine for errors
    # case 1: "(" special characters and length smaller than 2 tend to be invalid input source, simply delete would work
    # case 2: special items with keyword that does not look like food, eg: sanitizer,
    # case 3: clean up missing matched words --> food as f000
        # --------- price clean up
        re_tnt_price_quantity_info_1 = '.*\$.*[\d]e[a|d]'
        re_tnt_price_quantity_info_2 = '\/\$[\d]'
        re_tnt_weird_price = '\d*\.\d*'
        addition = []
        del_idx = []
        for idx in range(len(items)):

            if items[idx].find('$') != -1:
                if re.search(re_tnt_price_quantity_info_1, items[idx]) == None and re.search(re_tnt_price_quantity_info_2, items[idx]) == None:
                    del_idx.append(idx)
                if re.search(re_tnt_price_quantity_info_1, items[idx]) != None:
                    # 2 @ $5.99ea. --yes
                    # 2 1a2 @ $2.99ea. --- yes
                    # 12232 @ $2.99ea.  --yes
                    # 1 1 2 @ $2.99ea.  --yes
                    item_no_space = items[idx].replace(' ','')
                    if item_no_space.find('@') != -1:
                        quantity = items[idx][item_no_space.find('@')-1]
                    else:
                        quantity = items[idx][0]
                    if quantity.isnumeric():
                        items[idx] = quantity
                        if  10 > int(quantity) > 1:
                            for i in range(int(quantity)-1):
                                addition.append(items[idx-1])


                if re.search(re_tnt_price_quantity_info_2, items[idx]) != None:
                    quantity = min(items[idx].split(' '), key=len)
                    if quantity.isnumeric():
                        items[idx] = quantity
                        if  10 > int(quantity) > 1:
                            for i in range(int(quantity)-1):
                                addition.append(items[idx-1])
                    elif quantity[0].isnumeric():
                        items[idx] = quantity[0]
                        if  10 > int(quantity[0]) > 1:
                            for i in range(int(quantity[0])-1):
                                addition.append(items[idx-1])
                    # 171330 2 @ga2/$3.29'  --yes
                    # 171330 2 22/$3.29'  --yes
            # The order here matters:
            # '''
            #             we first process the quantity and add the extra items into the bucket list in ADDITION
            #             then we remove the quantity afterwards
            #             at the end we append the addition list into the item list
            # '''
            #if len(items[idx]) <= 2 or len(items[idx].split()) == 1:
            if len(items[idx]) <= 3:
                if idx not in del_idx:
                    del_idx.append(idx)
            # remove any extra wrongly detect words and not food related words
            if items[idx].find('sanitizer') != -1 or items[idx].find('heat') != -1 or items[idx].find('neat') != -1 or items[idx].find('mask') != -1:
                if idx not in del_idx:
                    del_idx.append(idx)
            if items[idx].find('f000') != -1 :
                items[idx] = items[idx].replace('f000','food')
            if re.search(re_tnt_weird_price, items[idx]) != None:
                if idx not in del_idx:
                    del_idx.append(idx)

        print("del", del_idx)
        for idx in del_idx[-1::-1]:
            del items[idx]
        # add the repeated items into items list
        items.extend(addition)

    return items





def list_dataframe_json(uncounted_item_list):
    newlist = uncounted_item_list
    ct = Counter(newlist)
    ctdf = pd.DataFrame.from_records(list(dict(ct).items()), columns=['name','amount'])
    ctdf['unit'] = ['serving'] * ctdf.shape[0]
    ctdf['best_before'] = [datetime.datetime.now()+datetime.timedelta(days=21)] * ctdf.shape[0]
    return ctdf

def df_json(df):
    # directly return json body
    #json = df.to_json(orient='records')[1:-1].replace('},{', '} {')
    json = df.to_dict('records')

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
    0.1 : preprocess images for better vision
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








    '''
    ####-----  FLOW  -----####
    item,store = regex_parser(source)
    df = list_dataframe_json(item_final_clean_before_df(item,store))
    print(df)
    json = df_json(df)
    return json


#print(type(case))

print(flow(case))
