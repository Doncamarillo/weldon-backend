from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://default_user:default_password@localhost/welldon_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    twitter = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(50), default='user')

    projects = db.relationship('Project', back_populates='user', cascade="all, delete")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete")

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='projects')
    comments = db.relationship('Comment', back_populates='project', cascade="all, delete")

    def __repr__(self):
        return f'<Project {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    project = db.relationship('Project', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'


@app.route('/users', methods=['POST'])
def create_user():
    try:
        new_user = request.json
        user = User(
            username=new_user['username'],
            email=new_user['email'],
            password_hash=new_user['password']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "username": user.username}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        new_project = request.json
        project = Project(
            title=new_project['title'],
            description=new_project['description'],
            user_id=new_project['user_id']
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({"id": project.id, "title": project.title}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route('/comments', methods=['POST'])
def create_comment():
    try:
        new_comment = request.json
        comment = Comment(
            content=new_comment['content'],
            user_id=new_comment['user_id'],
            project_id=new_comment['project_id']
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({"id": comment.id, "content": comment.content[:20]}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)