from flask import Blueprint, request, jsonify
from .models import db, User, Project, Comment

bp = Blueprint('main', __name__)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], password_hash=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username}), 201

@bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(title=data['title'], description=data['description'], user_id=data['user_id'])
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"id": new_project.id, "title": new_project.title}), 201

@bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    new_comment = Comment(content=data['content'], user_id=data['user_id'], project_id=data['project_id'])
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"id": new_comment.id, "content": new_comment.content}), 201

@bp.route('/projects/<int:project_id>/comments', methods=['GET'])
def get_comments(project_id):
    comments = Comment.query.filter_by(project_id=project_id).all()
    return jsonify([comment.to_dict() for comment in comments])
