from flask_restplus import Namespace, Resource, fields
from .users import user_model, get_user_or_abort
from ..dal import Toothpick, User, Owner, db

ns = Namespace('toothpicks')

owner_model = ns.model('Owner', {
    'user': fields.Nested(user_model, description='user owning the toothpick'),
    'since': fields.DateTime(description='date and time since user owns toothpick')
})

toothpick_model = ns.model('Toothpick', {
    'id': fields.Integer(description='toothpick unique identifier', example=42),
    'owners': fields.List(fields.Nested(owner_model), description='toothpick owners in reverse chronological order (current owner goes first)')
})

@ns.route('/toothpicks/<int:toothpick_id>')
@ns.doc(params = { 'toothpick_id': 'unique toothpick identifier' })
class ToothpickResource(Resource):
    """Resource representing single tothpick"""
    
    @ns.marshal_with(toothpick_model)
    @ns.doc(responses = { 404: 'Unknown <toothpick_id>' })
    def get(self, toothpick_id):
        """Retreives toothpick by ID"""
        return get_toothpick_or_abort(toothpick_id)

@ns.route('/toothpicks')
class ToohtpickCollectionResource(Resource):
    """Manages collection of all toothpicks"""

    @ns.marshal_with(toothpick_model, as_list=True)
    def get(self):
        """Retreives all known toothpicks"""
        return Toothpick.query.all()

    @ns.marshal_with(toothpick_model, code=201, description='Toothpick Created')
    def post(self):
        """Creates toothpick with autogenerated ID"""
        toothpick = Toothpick()
        db.session.add(toothpick)
        db.session.commit()
        return toothpick, 201

@ns.route('/toothpicks/<int:toothpick_id>/owners/<int:user_id>')
@ns.doc(params = { 
    'toothpick_id': 'unique toothpick identifier', 
    'user_id': 'unique user identifier' 
})
class ToothpickOwnersResource(Resource):
    """Resource for managing toothick ownership"""

    @ns.marshal_with(toothpick_model, code=201, description='Created')
    @ns.response(200, 'Not Modified', toothpick_model)
    @ns.response(404, 'Unknown <user_id> or <toothpick_id>')
    def post(self, toothpick_id, user_id):
        """Makes user own a toothick."""
        user = get_user_or_abort(user_id, ns)
        toothpick = get_toothpick_or_abort(toothpick_id)

        owner = next(iter(toothpick.owners))

        if not owner or owner.user_id != user_id:
            db.session.add(Owner(user_id=user_id, toothpick_id=toothpick_id))
            db.session.commit()
            return toothpick, 201

        return toothpick, 200
        
def get_toothpick_or_abort(toothpick_id, api=ns):
    """Retreives toothpick by ID and raises 404 error when such user does not exist"""
    toothpick = Toothpick.query.filter_by(id=toothpick_id).first()

    if not toothpick:
        api.abort(404, 'Toothpick with id=<%d> not found' % toothpick_id)

    return toothpick