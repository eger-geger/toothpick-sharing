from flask_restplus import Namespace, Resource, fields
from .users import user_model, get_user_or_abort
from ..dal import Toothpick, User, Owner, db

ns = Namespace('toothpicks', description='CRUD operations for toothpicks')

owner_model = ns.model('Owner', {
    'user': fields.Nested(user_model, description='user owning the toothpick'),
    'since': fields.DateTime(description='date and time since user owns toothpick')
})

toothpick_model = ns.model('Toothpick', {
    'id': fields.Integer(description='toothpick unique identifier', example='42'),
    'owners': fields.List(fields.Nested(owner_model), description='toothpick owners in reverse chronological order (current owner goes first)')
})

@ns.route('/toothpicks/<int:toothpick_id>')
class ToothpickResource(Resource):

    @ns.marshal_with(toothpick_model)
    def get(self, toothpick_id):
        """Retreives toothpick by ID"""
        return get_toothpick_or_abort(id)

@ns.route('/toothpicks')
class ToohtpickCollectionResource(Resource):

    @ns.marshal_with(toothpick_model, as_list=True)
    def get(self):
        """Retreives all known toothpicks"""
        return Toothpick.query.all()

    @ns.marshal_with(toothpick_model)
    def post(self):
        """Creates toothpick with autogenerated ID"""
        toothpick = Toothpick()
        db.session.add(toothpick)
        db.session.commit()
        return toothpick

@ns.route('/toothpicks/<int:toothpick_id>/owners/<int:user_id>')
class ToothpickOwnersResource(Resource):

    @ns.marshal_with(toothpick_model)
    def post(self, toothpick_id, user_id):
        """Makes user own toothick"""
        user = get_user_or_abort(user_id, ns)
        toothpick = get_toothpick_or_abort(toothpick_id)

        owner = next(iter(toothpick.owners))

        if not owner or owner.user_id != user_id:
            db.session.add(Owner(user_id=user_id, toothpick_id=toothpick_id))
            db.session.commit()

        return toothpick
        
def get_toothpick_or_abort(id, api=ns):
    toothpick = Toothpick.query.filter_by(id=id).first()

    if not toothpick:
        api.abort(404, 'Toothpick with id=<%d> not found' % id)

    return toothpick