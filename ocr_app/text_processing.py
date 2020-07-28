#from dateutil.parser import parse
import pytesseract
from PIL import Image
import re
import cv2
 

def OCR(img):
    print("Inside OCR")
#    print(img_path) 
#    try:
#        img = cv2.imread(img_path)
##        img = Image.open(img_path) 
#        print(img)
#        config = ("-l eng --oem 1 --psm 6")
#        text = pytesseract.image_to_string(img, config=config)
#    except Exception as e:
#        print("can not open image: ", e)
    config = ("-l eng --oem 1 --psm 6")
    text = pytesseract.image_to_string(img, config=config)
    print("text:",text)
    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    return text 
    
def lines(crop_img, crop=True):
    print("Inside lines")
    if(crop):
        (H1, W1) = crop_img.shape[:2]
        startX = 0
        endX = int(W1 * .7)
        startY = 0  # int(H1*.2)
        endY = H1
        roi = crop_img[startY:endY, startX:endX]
#    config = ("-l eng --oem 1 --psm 6")
#    text = pytesseract.image_to_string(roi, config=config)
#    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
#    print(text)
        text = OCR(roi)
    else:
        text = OCR(crop_img)
    print(text)

#    text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    
    #print(text)
    text = text.splitlines()
    
    text2 = []
    for i in range(len(text)):
        line = text[i]
        line = "".join([c if ord(c) < 128 else "" for c in line]).strip()
        text[i] = line
        temp = line.split()
        text2.append(temp)
    print("Reached end of lines")
    return text, text2



#def is_date1(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
#    try:
#        parse(string, fuzzy=fuzzy)
#        return True

#    except ValueError:
#        return False

def is_pan(string):
    PAN = re.search('[A-Z0125789]{5}[0-9ABIJOQSTUYZ]{4}[A-Z0125789]',string)
    if(PAN and len(PAN.group()) ==10):
        PAN = PAN.group()
        x = PAN[:5]
        y = PAN[5:9]
        z = PAN[9:]
        
        x = x.replace("0", "O")
        x = x.replace("1", "I")
        x = x.replace("2", "Z")
        x = x.replace("5", "S")
        x = x.replace("7", "T")
        x = x.replace("8", "A")
        x = x.replace("9", "P")
        
        y = y.replace("A", "4")
        y = y.replace("B", "8")
        y = y.replace("I", "1")
        y = y.replace("J", "7")
        y = y.replace("O", "0")
        y = y.replace("Q", "0")
        y = y.replace("S", "3")
        y = y.replace("T", "7")
        y = y.replace("U", "0")
        y = y.replace("Y", "7")
        y = y.replace("Z", "7")
        
        x = x.replace("0", "O")
        x = x.replace("1", "I")
        x = x.replace("2", "Z")
        x = x.replace("5", "S")
        x = x.replace("7", "T")
        x = x.replace("8", "A")
        x = x.replace("9", "P")
        
        Pan = x + y + z
        return True, Pan
    else:
        return False, string
    

def is_date(string):
    if(string[0:2].isnumeric() and string[3:5].isnumeric() and string[6:10].isnumeric()): 
        return True
    else:
        return False

def date_cleanup(date):  
    print("inside cleanup: ",date)
    x = date[:1]
    y = date[1:3]
    z = date[3:4]
    w = date[4:]
    x = x.replace("4", "1")
    x = x.replace("5", "3")
    x = x.replace("7", "1")
    x = x.replace("8", "3")
    x = x.replace("9", "0")
    
    z = z.replace("4", "1")
    z = z.replace("6", "0")
    z = z.replace("7", "1")
    z = z.replace("8", "0")
    z = z.replace("9", "0")
    DATE =x + y + z + w
    return DATE
    
def check_date_pan(text2):
    count = 0
    idx_date = -1
    date = None
    idx_pan = -1
    pan = ''
    for line in text2:
        for word in line:  
            if(is_date(word)):
                date = word
                idx_date = count
                print(date)
                
            isPan, PAN = is_pan(word)
            if isPan:
                pan = PAN
                idx_pan = count
        count += 1
    
    if date is None:
        date = ''
    
    elif date is not None:
        date = date_cleanup(date)
    print("DATE: ",date)
    if(idx_date<idx_pan):
        return 1,idx_date,date,idx_pan,pan
    else:
        return 2,idx_date,date,idx_pan,pan

def text_clean(line):
    print("inside text_clean")
    if line is not None:
        print("inside if")
        line = line.strip()
        line = re.sub(' +', ' ', line)
    return line

#def clean_gibberish_text (text):
#    # Cleaning all the gibberish text
#    text = ftfy.fix_text(text)
#    text = ftfy.fix_encoding(text)
#    '''for god_damn in text:
#        if nonsense(god_damn):
#            text.remove(god_damn)
#        else:
#            print(text)'''
#    # print(text)
#    return text
