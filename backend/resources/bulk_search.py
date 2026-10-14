from flask_restful import Resource
from flask import request
from .. import db
from ..models import ImportedNumber, EyeconResult, FacebookResult, ApiCredential
from ..search import search_number

class BulkSearch(Resource):
    def post(self):
        """
        Returns the list of pending numbers so the frontend can search them
        one by one using /api/search with sequential API rotation.
        """
        pending = ImportedNumber.query.filter_by(searched=False).order_by(ImportedNumber.id).all()
        creds = ApiCredential.query.order_by(ApiCredential.id).all()

        return {
            'pending_count': len(pending),
            'pending_numbers': [{'id': n.id, 'number': n.number} for n in pending],
            'credential_count': len(creds)
        }
