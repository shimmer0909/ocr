# ocr
Usage:
1.copy the pre-trained model from https://drive.google.com/file/d/1-xjWwbSH79ZZApdAyhTATuiPRCooEK2o/view?usp=sharing to ocr/ocr_app/model folder

2.Install tesseract 4.1.x from https://notesalexp.org/tesseract-ocr/
  Install ghostscript using sudo apt install ghostscript 

3.cd ocr
  python manage.py runserver

4.cd ocr/ocr_app
python subscribe.py
  
5.API - http://x.y.z.q/pan_ocr/
  parameter:
  {
  "fileUrl":"image url",
  "type":"pan",
  "callbackUrl":"callback url"
  }
  
6.API - http://x.y.z.q/getprocesseddoc/
  parameter:
  {
  "transactionId":"transaction id"
  }
  
