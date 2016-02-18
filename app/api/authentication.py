"""
    This files handles the authentication logic.
"""
from flask import flash
from flask.ext.restful import reqparse, Resource
from flask.ext.login import logout_user

from app.models import User
from app.db import session

parser = reqparse.RequestParser()


class UserRegistration(Resource):
    """Resource to handle '/auth/register/' endpoint."""

    def post(self):
        """Allow a user to register."""
        parser.add_argument('username')
        parser.add_argument('password')

        args = parser.parse_args()
        username = args['username']
        password = args['password']
        exists = session.query(User).filter_by(username=username).first()
        if exists and exists.username == username:
            return {'message': 'User already exists!'}
        user = User(username=username)
        user.hash_password(password)
        session.add(user)
        session.commit()
        return {'message': 'User {} has been successfully registered'
                           .format(username)}


class UserLogin(Resource):
    """Resource to handle '/auth/login/' endpoint."""

    def post(self):
        """Log in a user."""
        parser.add_argument('username')
        parser.add_argument('password')
        args = parser.parse_args()
        username = args['username']
        password_hash = args['password']

        userlogged = session.query(User).filter_by(username=username).first()

        if not userlogged:
            return {'message': "User doesn't exist"}
        if userlogged.verify_password(password_hash):
            token = userlogged.generate_confirmation_token()
            flash("user successfully logged in")
            return {'token': token}
        # if password not verified
        return {'message': 'Incorrect password.'}


class UserLogout(Resource):
    """Resource to handle '/auth/logout/' endpoint."""

    def post(self):
        logout_user()
        return {'message': 'user successfully logged out.'}