# 🧾 Receipt Scanner Web App

## Setup Instructions

### **1. Clone Repository**
git clone https://github.com/S1DdharTH16/receipt-ocr.git

cd receipt_ocr_project


### **2. Create a Virtual Environment**

Windows:

python -m venv venv

source venv/bin/activate


### **3. Install Dependencies**

Windows:

pip install -r requirements.txt


### **4. Install Tesseract OCR**
Make sure Tesseract is installed and accessible via command line

Windows: https://github.com/tesseract-ocr/tesseract/wiki

Check by executed this via command line:

tesseract --version

Make sure to put path in the system varibales

path = "C:\Program Files\Tesseract-OCR"


### **5. Initialize the Database**
Write the following commands to intialize the dataabse

Windows:

flask db init

flask db migrate

flask db upgrade


## API Endpoints

### **1. Upload Receipt**

POST /upload

Upload a receipt (PDF file):

curl -F "file=@path/to/receipt.pdf" http://localhost:5000/upload


### **2. Validate PDF**

POST /validate

Request Body:
{
  "file_id": 1
}

curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": 1}' http://localhost:5000/validate


### **3. Process Receipt**
POST /process

Request Body:
{
  "file_id": 1
}

curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": 1}' http://localhost:5000/process


### **4. Get All Receipts**
GET /receipts

curl http://localhost:5000/receipts


### **5. Get One Receipt by ID**
GET /receipts/<id>

curl http://localhost:5000/receipts/1
