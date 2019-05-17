from flask import jsonify, Blueprint, abort, url_for
from flask_restful import Resource, Api, reqparse,inputs, fields,marshal, marshal_with
import models

attraction_field = {
	'id':fields.Integer,
	'name':fields.String,
	'detail': fields.String,
	'price':fields.String,
    'location':fields.String,
    'longtude':fields.Integer,
    'latitude':fields.Integer,
    'distance':fields.Integer,
    'category':fields.String
}

def attraction_or_404(attraction_id):
	try:
		attraction= models.Place.get(models.Place.id == attraction_id)
	except models.Place.DoesNotExist:
		abort(404)
	else:
		return attraction

class AttractionList(Resource):
	
	def get(self):
		attractions = [marshal(attraction, attraction_field)for attraction in models.Place.select()]
		return jsonify(attractions)
		
class Attraction(Resource):
	
	@marshal_with(attraction_field)
	def get(self, id):
		return attraction_or_404(id)



attraction_api = Blueprint('resources.attractions',__name__)

api = Api(attraction_api)
api.add_resource(
	AttractionList,
	'/api/attractions',
	endpoint='attractions'
	)
api.add_resource(
	Attraction,
	'/api/attraction/<int:id>',
	endpoint='attraction'
	)