# ocr

Usage:

1. copy the pre-trained model from https://drive.google.com/file/d/1-xjWwbSH79ZZApdAyhTATuiPRCooEK2o/view?usp=sharing to ocr/ocr_app/model folder

2. Install tesseract 4.1.x from https://notesalexp.org/tesseract-ocr/

3. Install ghostscript using sudo apt install ghostscript

4. cd ocr

5. python manage.py runserver

6. cd ocr/ocr_app

7. python subscribe.py

8. curl --location --request POST 'http://xx/ocr/' \
   --header 'Content-Type: application/json' \
   --data-raw '{"fileUrl": "", "type": "pan"}'

9. curl GET 'http://xx/processedDoc/?transactionId=xxxx'
