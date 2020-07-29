# ocr
Usage:
1.copy the pre-trained model from https://drive.google.com/file/d/1-xjWwbSH79ZZApdAyhTATuiPRCooEK2o/view?usp=sharing to ocr/ocr_app/model folder

2.Install tesseract 4.1.x from https://notesalexp.org/tesseract-ocr/

3.Install ghostscript using sudo apt install ghostscript 

4.cd ocr
  python manage.py runserver

5.cd ocr/ocr_app
python subscribe.py
  
6.API - http://x.y.z.q/pan_ocr/
  parameter:
  {
  "file_url":"image url",
  "type":"pan",
  "callback_url":"callback url"
  }
  
7.API - http://x.y.z.q/getprocesseddoc/
  parameter:
  {
  "transactionId":"transaction id"
  }
  
