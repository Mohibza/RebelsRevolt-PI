from flask_restful import Resource
from flask import request
from .. import db
from ..models import ImportedNumber, EyeconResult, FacebookResult

class NumberList(Resource):
    def get(self):
        nums = ImportedNumber.query.order_by(ImportedNumber.id).all()
        result = []
        for n in nums:
            er = EyeconResult.query.filter_by(number=n.number).first()
            fr = FacebookResult.query.filter_by(number=n.number).first()
            result.append({
                'id': n.id,
                'number': n.number,
                'searched': n.searched,
                'names': er.name if er else None,
                'fb_id': fr.fb_id if fr else None,
                'fb_link': fr.fb_link if fr else None,
            })
        return result

    def delete(self):
        ImportedNumber.query.delete()
        EyeconResult.query.delete()
        FacebookResult.query.delete()
        db.session.commit()
        return {'cleared': True}

class NumberDetail(Resource):
    def delete(self, num_id):
        n = ImportedNumber.query.get_or_404(num_id)
        EyeconResult.query.filter_by(number=n.number).delete()
        FacebookResult.query.filter_by(number=n.number).delete()
        db.session.delete(n)
        db.session.commit()
        return {'deleted': True}
