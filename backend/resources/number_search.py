from flask_restful import Resource
from flask import request
from .. import db
from ..models import ImportedNumber, EyeconResult, FacebookResult, ApiCredential
from ..search import search_number


class NumberSearch(Resource):
    def post(self):
        data = request.get_json()
        number = str(data.get('number', '')).strip()
        cred_index = int(data.get('cred_index', 0))

        if not number:
            return {'error': 'number required'}, 400

        creds = ApiCredential.query.order_by(ApiCredential.id).all()
        if not creds:
            return {'error': 'No API credentials configured'}, 400

        creds_list = [
            {'api_id': c.api_id, 'country_code': c.country_code, 'label': c.label}
            for c in creds
        ]

        # search_number tries all credentials starting at cred_index
        result = search_number(number, creds_list, start_index=cred_index)

        # Update DB
        num_rec = ImportedNumber.query.filter_by(number=number).first()
        if num_rec:
            num_rec.searched = True

        # Upsert eyecon
        er = EyeconResult.query.filter_by(number=number).first()
        if er:
            er.name = result['names_str']
            er.credential_used = result['credential_used']
        else:
            er = EyeconResult(
                number=number,
                name=result['names_str'],
                credential_used=result['credential_used']
            )
            db.session.add(er)

        # Upsert facebook
        fr = FacebookResult.query.filter_by(number=number).first()
        if fr:
            fr.fb_id = result['fb_id']
            fr.fb_link = result['fb_link']
        else:
            fr = FacebookResult(
                number=number,
                fb_id=result['fb_id'],
                fb_link=result['fb_link']
            )
            db.session.add(fr)

        db.session.commit()

        return {
            'number': number,
            'names': result['names'],
            'names_str': result['names_str'],
            'fb_id': result['fb_id'],
            'fb_link': result['fb_link'],
            'credential_used': result['credential_used'],
            'attempts': result['attempts'],
            'raw_response': result['raw_response']
        }
