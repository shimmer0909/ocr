#from dateutil.parser import parse
import pytesseract
import re
 

def OCR(img):
    print("Inside OCR")
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
    #print("Inside is_pan")
    PAN = re.search('[A-Z0]{5}[0-9O]{4}[A-Z]',string)
    if(PAN and len(PAN.group()) ==10):
        return True, PAN.group()
    else:
        return False, string
        
    #return string.isupper() and len(string)>=10 and string[5:9].isnumeric() and string[0:5].isalpha() and string[9:10].isalpha()
    

def is_date(string):
    if(string[0:2].isnumeric() and string[3:5].isnumeric() and string[6:10].isnumeric()): #and len(string)==10):
    #if(string[0:2].isnumeric() and string[3:5].isnumeric() and string[6:8].isnumeric() and len(string)>7):    
        return True
    else:
        return False

def check_date_pan(text2):
  count = 0
  idx_date = -1
  date = ''
  idx_pan = -1
  pan = ''
  for line in text2:
    for word in line:
      if(is_date(word)):
        date = word
        idx_date = count
      isPan, PAN = is_pan(word)
      if isPan:
        pan = PAN
        idx_pan = count
    count += 1

  if(idx_date<idx_pan):
    return 1,idx_date,date,idx_pan,pan
  else:
    return 2,idx_date,date,idx_pan,pan

def text_clean(line):
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
