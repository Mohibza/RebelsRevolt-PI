from flask_restful import Resource
from flask import request, jsonify
from .. import db
from ..models import ApiCredential

class CredentialList(Resource):
    def get(self):
        creds = ApiCredential.query.order_by(ApiCredential.id).all()
        return [{
            'id': c.id,
            'api_id': c.api_id,
            'country_code': c.country_code,
            'label': c.label,
            'is_default': c.is_default
        } for c in creds]

    def post(self):
        data = request.get_json()
        if not data or not data.get('api_id') or not data.get('country_code'):
            return {'error': 'api_id and country_code required'}, 400
        cred = ApiCredential(
            api_id=data['api_id'],
            country_code=data['country_code'],
            label=data.get('label', 'Custom Key'),
            is_default=False
        )
        db.session.add(cred)
        db.session.commit()
        return {'id': cred.id, 'label': cred.label, 'api_id': cred.api_id,
                'country_code': cred.country_code, 'is_default': cred.is_default}, 201

class CredentialDetail(Resource):
    def put(self, cred_id):
        cred = ApiCredential.query.get_or_404(cred_id)
        data = request.get_json()
        if data.get('api_id'): cred.api_id = data['api_id']
        if data.get('country_code'): cred.country_code = data['country_code']
        if data.get('label'): cred.label = data['label']
        db.session.commit()
        return {'id': cred.id, 'label': cred.label}

    def delete(self, cred_id):
        cred = ApiCredential.query.get_or_404(cred_id)
        db.session.delete(cred)
        db.session.commit()
        return {'deleted': True}
