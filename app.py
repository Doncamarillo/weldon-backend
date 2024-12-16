from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import jwt
import os
import logging
import bcrypt
from functools import wraps
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://doncamarillo:megatron@localhost/welldon_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403
        try:
            token = token.split(" ")[1]
            decoded_token = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
            current_user = User.query.get(decoded_token['id'])
            if not current_user:
                return jsonify({'error': 'User not found!'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 403
        return f(current_user, *args, **kwargs)
    return wrap


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    projects = db.relationship('Project', back_populates='user', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete-orphan")
    twitter = db.Column(db.String(120), nullable=True)
    linkedin = db.Column(db.String(120), nullable=True)
    youtube = db.Column(db.String(120), nullable=True)
    github = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)  
    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    deployed_url = db.Column(db.String(500), nullable=True)
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

@app.route('/sign-token', methods=['GET'])
def sign_token():
    user = {
        "id": 1,
        "username": "test",
        "password": "test"
    }
    token = jwt.encode(user, os.getenv('JWT_SECRET'), algorithm="HS256")
    return jsonify({"token": token})

@app.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        return jsonify({"user": decoded_token})
    except Exception as error:
        return jsonify({"error": str(error)})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "twitter": user.twitter,
        "linkedin": user.linkedin,
        "youtube": user.youtube,
        "github": user.github,
        "profile_picture": user.profile_picture  
    }
    return jsonify(user_data), 200


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json

        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400

        
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password.decode('utf-8') 
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500



@app.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.json
        user = User.query.filter_by(username=data['username']).first()

      
        if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"error": "Invalid credentials"}), 401
        
       
        token = jwt.encode({"id": user.id, "username": user.username}, os.getenv('JWT_SECRET'), algorithm="HS256")
        
        return jsonify({"token": token, "id": user.id})

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500



@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = data['password']
        if hasattr(user, 'first_name') and 'first_name' in data:
            user.first_name = data['first_name']
        if hasattr(user, 'last_name') and 'last_name' in data:
            user.last_name = data['last_name']
        if hasattr(user, 'bio') and 'bio' in data:
            user.bio = data['bio']
        
        if 'twitter' in data:
            user.twitter = data['twitter']
        if 'linkedin' in data:
            user.linkedin = data['linkedin']
        if 'youtube' in data:
            user.youtube = data['youtube']
        if 'github' in data:
            user.github = data['github']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500






@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/users/<int:user_id>/projects', methods=['GET'])
def get_user_projects(user_id):
    try:
        user = User.query.get_or_404(user_id)
        projects = Project.query.filter_by(user_id=user.id).all()
        projects_list = [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "image_url": project.image_url,
                "user_id": project.user_id
            } for project in projects
        ]
        return jsonify(projects_list), 200
    except Exception as e:
        app.logger.error('Error fetching user projects: %s', e)
        return jsonify({"error": str(e)}), 500


@app.route('/projects', methods=['GET'])
def get_projects():
    try:
        projects = Project.query.join(User).all()
        project_list = [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "image_url": project.image_url,
                "deployed_url": project.deployed_url,
                "user_id": project.user_id,
                "username": project.user.username 
            }
            for project in projects
        ]
        return jsonify(project_list), 200
    except Exception as e:
        app.logger.error('Error fetching projects: %s', e)
        return jsonify({"error": str(e)}), 500

@app.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    try:
        project = Project.query.get_or_404(id)
        project_data = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "image_url": project.image_url,
            "deployed_url": project.deployed_url,
            "user_id": project.user_id,
            "username": project.user.username 
        }
        return jsonify(project_data), 200
    except Exception as e:
        app.logger.error('Error fetching project details: %s', e)
        return jsonify({"error": str(e)}), 500

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.json
        app.logger.debug('Request data: %s', data)
        if not data.get('title') or not data.get('user_id'):
            return jsonify({"error": "Missing required fields: 'title' or 'user_id'"}), 400
        
        project = Project(
            title=data['title'],
            description=data.get('description'), 
            image_url=data.get('image_url'),
            deployed_url=data.get('deployed_url'),
            user_id=data['user_id']
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({"id": project.id, "title": project.title, "description": project.description, "image_url": project.image_url, "deployed_url": project.deployed_url, "user_id": project.user_id}), 201
    except Exception as e:
        app.logger.error('Error: %s', e)
        return jsonify({"error": str(e)}), 500


    
@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        data = request.json
        if 'title' in data:
            project.title = data['title']
        if hasattr(project, 'description') and 'description' in data:
            project.description = data['description']

        db.session.commit()
        return jsonify({"message": "Project updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


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

@app.route('/comments', methods=['POST'])
def create_comment():
    try:
        data = request.json
        if not data.get('content') or not data.get('user_id') or not data.get('project_id'):
            return jsonify({"error": "Missing required fields: 'content', 'user_id', or 'project_id'"}), 400
        
        comment = Comment(
            content=data['content'],
            user_id=data['user_id'],
            project_id=data['project_id']
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({"id": comment.id, "content": comment.content, "user_id": comment.user_id, "project_id": comment.project_id}), 201

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

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
