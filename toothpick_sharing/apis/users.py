from flask_restplus import Namespace, Resource, fields
from ..dal import User, db

ns = Namespace('users')

user_model = ns.model('User', {
    'id': fields.Integer(description='user unique identifier', example=42),
    'name': fields.String(description='user full name', example='Jack Daniels', required=True),
})

@ns.route('/users/<int:user_id>')
@ns.doc(params = { 'user_id': 'unique user identifier' })
class UserResource(Resource):
    """Resource for managing single user"""

    @ns.marshal_with(user_model, code=200)
    @ns.response(404, 'Unknown <user_id>')
    def get(self, user_id):
        """Retrieves user by ID"""
        return get_user_or_abort(user_id)

@ns.route('/users')
class UserCollectionResource(Resource):
    """Represents collection of all users"""

    @ns.marshal_with(user_model, as_list=True)
    def get(self):
        """Retreives collection of all known users"""
        return User.query.all()

    @ns.expect(user_model)
    @ns.marshal_with(user_model, code=201, description='Created')
    def post(self):
        """Creates new user"""
        user = User(**self.api.payload)
        db.session.add(user)
        db.session.commit()
        return user, 201

def get_user_or_abort(user_id, api=ns):
    """Finds user by ID. Raises 404 error when such does not exist."""
    user = User.query.filter_by(id=user_id).first()

    if not user:
        api.abort(404, 'User with id=<%s> not found' % user_id)

    return user