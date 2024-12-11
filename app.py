from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://default_user:default_password@localhost/welldon_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    projects = db.relationship('Project', back_populates='user', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete-orphan")

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='projects')
    comments = db.relationship('Comment', back_populates='project', cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user = db.relationship('User', back_populates='comments')
    project = db.relationship('Project', back_populates='comments')



@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.bio = data.get('bio', user.bio)
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{"id": project.id, "title": project.title, "user_id": project.user_id} for project in projects]), 200

@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"id": project.id, "title": project.title, "user_id": project.user_id}), 200

@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    data = request.json
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    db.session.commit()
    return jsonify({"message": "Project updated successfully"}), 200

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted successfully"}), 200

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify([{"id": comment.id, "content": comment.content, "user_id": comment.user_id, "project_id": comment.project_id} for comment in comments]), 200

@app.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    return jsonify({"id": comment.id, "content": comment.content, "user_id": comment.user_id, "project_id": comment.project_id}), 200

@app.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    data = request.json
    comment.content = data.get('content', comment.content)
    db.session.commit()
    return jsonify({"message": "Comment updated successfully"}), 200

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
