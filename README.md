# ocr
Usage:
1.copy the pre-trained model from https://drive.google.com/file/d/1-xjWwbSH79ZZApdAyhTATuiPRCooEK2o/view?usp=sharing to ocr/ocr_app/model folder

2.cd ocr
  python manage.py runserver

3.cd ocr/ocr_app
python subscribe.py
  
4.API - http://x.y.z.q/pan_ocr/
  parameter:
  {
  "fileUrl":"image url",
  "type":"pan",
  "callbackUrl":"callback url"
  }
  
5.API - http://x.y.z.q/getprocesseddoc/
  parameter:
  {
  "transactionId":"transaction id"
  }
  
