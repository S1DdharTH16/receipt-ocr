from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from .models import db, ReceiptFile
from datetime import datetime
import fitz
from .ocr import extract_receipt_fields
from .models import Receipt
from sqlalchemy import desc
from .models import Receipt


receipt_routes = Blueprint('receipt_routes', __name__)


ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@receipt_routes.route('/upload', methods=['POST'])
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)

        receipt_file = ReceiptFile(
            file_name=filename,
            file_path=file_path,
            is_valid=False,
            is_processed=False,
        )

        db.session.add(receipt_file)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully', 'file_id': receipt_file.id}), 201

    return jsonify({'error': 'Only PDF files are allowed'}), 400


@receipt_routes.route('/validate', methods=['POST'])
def validate_receipt():
    data = request.get_json()

    if not data or 'file_id' not in data:
        return jsonify({'error': 'Missing file_id in request'}), 400

    file_id = data['file_id']
    receipt_file = ReceiptFile.query.get(file_id)

    if not receipt_file:
        return jsonify({'error': 'File not found'}), 404

    try:
        with fitz.open(receipt_file.file_path) as doc:
            if doc.page_count == 0:
                raise ValueError("Empty PDF")

        receipt_file.is_valid = True
        receipt_file.invalid_reason = None

    except Exception as e:
        receipt_file.is_valid = False
        receipt_file.invalid_reason = str(e)

    db.session.commit()

    return jsonify({
        'file_id': receipt_file.id,
        'is_valid': receipt_file.is_valid,
        'invalid_reason': receipt_file.invalid_reason
    }), 200


@receipt_routes.route('/process', methods=['POST'])
def process_receipt():
    data = request.get_json()
    if not data or 'file_id' not in data:
        return jsonify({'error': 'Missing file_id in request'}), 400

    file_id = data['file_id']
    receipt_file = ReceiptFile.query.get(file_id)
    if not receipt_file:
        return jsonify({'error': 'File not found'}), 404

    if not receipt_file.is_valid:
        return jsonify({'error': 'File has not passed validation'}), 400
    if receipt_file.is_processed:
        return jsonify({'error': 'File already processed'}), 409

    try:
        fields = extract_receipt_fields(receipt_file.file_path)
    except Exception as e:
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500

    receipt = Receipt(
        purchased_at = fields["purchased_at"],
        merchant_name = fields["merchant_name"],
        total_amount  = fields["total_amount"],
        file_path     = receipt_file.file_path,
    )
    db.session.add(receipt)

    # mark source file processed
    receipt_file.is_processed = True
    db.session.commit()

    return jsonify({
        "receipt_id": receipt.id,
        "purchased_at": receipt.purchased_at.isoformat() if receipt.purchased_at else None,
        "merchant_name": receipt.merchant_name,
        "total_amount": receipt.total_amount,
    }), 201


@receipt_routes.route('/receipts', methods=['GET'])
def list_receipts():
    receipts = Receipt.query.order_by(desc(Receipt.created_at)).all()

    result = []
    for r in receipts:
        result.append({
            "id": r.id,
            "purchased_at": r.purchased_at.isoformat() if r.purchased_at else None,
            "merchant_name": r.merchant_name,
            "total_amount": r.total_amount,
            "file_path": r.file_path,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        })

    return jsonify(result), 200


@receipt_routes.route('/receipts/<int:receipt_id>', methods=['GET'])
def get_receipt(receipt_id):
    r = Receipt.query.get(receipt_id)
    if not r:
        return jsonify({'error': 'Receipt not found'}), 404

    return jsonify({
        "id": r.id,
        "purchased_at": r.purchased_at.isoformat() if r.purchased_at else None,
        "merchant_name": r.merchant_name,
        "total_amount": r.total_amount,
        "file_path": r.file_path,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat(),
    }), 200
