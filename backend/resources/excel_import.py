import io
from flask_restful import Resource
from flask import request
from .. import db
from ..models import ImportedNumber
import openpyxl

class ExcelImport(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file uploaded'}, 400
        f = request.files['file']
        if not f.filename.endswith(('.xlsx', '.xls')):
            return {'error': 'Only .xlsx or .xls files allowed'}, 400

        try:
            wb = openpyxl.load_workbook(io.BytesIO(f.read()))
            ws = wb.active
            added = 0
            duplicates = 0
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell is not None:
                        num = str(cell).strip().replace(' ', '').replace('+', '').replace('-', '')
                        if num.isdigit() and len(num) >= 7:
                            exists = ImportedNumber.query.filter_by(number=num).first()
                            if not exists:
                                db.session.add(ImportedNumber(number=num))
                                added += 1
                            else:
                                duplicates += 1
            db.session.commit()
            return {'added': added, 'duplicates': duplicates}
        except Exception as e:
            return {'error': str(e)}, 500
