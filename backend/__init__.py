import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api

db = SQLAlchemy()

DEFAULT_CREDENTIALS = [
    ("8161f04e-a08b-4679-b7fc-487f0c86ef35", "37", "Eyecon ID 1"),
    ("fc208707-e1fe-4838-a585-5d26e69134e8", "48", "Eyecon ID 2"),
    ("6bc6a110-b8a7-40bf-9fa6-39b0366923a5", "33", "Eyecon ID 3"),
    ("7c3353bf-8504-4678-b189-668d6fac1b1f", "36", "Eyecon ID 4"),
    ("16513ab6-1b03-4c7c-958f-6b044e35b023", "21", "Eyecon ID 5"),
    ("76308641-0c0e-4636-b80d-be437dec7586", "33", "Eyecon ID 6"),
    ("a6f63f22-12f5-4c8d-b9ba-252ad93ea4af", "28", "Eyecon ID 7"),
]

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, 'frontend')

    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'eyecon.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

    CORS(app)
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        from .models import ApiCredential, ImportedNumber, EyeconResult, FacebookResult
        db.create_all()

        if ApiCredential.query.count() == 0:
            for api_id, country, label in DEFAULT_CREDENTIALS:
                cred = ApiCredential(api_id=api_id, country_code=country, label=label, is_default=True)
                db.session.add(cred)
            db.session.commit()

    from .resources.credentials import CredentialList, CredentialDetail
    from .resources.numbers import NumberList, NumberDetail
    from .resources.excel_import import ExcelImport
    from .resources.excel_export import ExcelExport
    from .resources.number_search import NumberSearch
    from .resources.bulk_search import BulkSearch

    api.add_resource(CredentialList,   '/api/credentials')
    api.add_resource(CredentialDetail, '/api/credentials/<int:cred_id>')
    api.add_resource(NumberList,       '/api/numbers')
    api.add_resource(NumberDetail,     '/api/numbers/<int:num_id>')
    api.add_resource(ExcelImport,      '/api/import')
    api.add_resource(ExcelExport,      '/api/export')
    api.add_resource(NumberSearch,     '/api/search')
    api.add_resource(BulkSearch,       '/api/bulk-search')

    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path='index.html'):
        return send_from_directory(frontend_dir, 'index.html')

    return app
