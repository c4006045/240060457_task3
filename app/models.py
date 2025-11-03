from flask_login import UserMixin
from . import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

# models will be defined here during implementation.
class User(db.Model): # database for users
    __tablename__ = 'users' # defining attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = Column(String(20), nullable=False, default='user')

    # relationship: one user has many posts
    posts = relationship('Post', back_populates='author')

class Post(db.Model): # database for posts
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationship: many posts belong to one user
    author = relationship('User', back_populates='posts')

def seed_data():
    if User.query.count() == 0:
        # sample users with different roles
        admin = User(username='admin', email='admin@example.com', password='admin123', role='admin')
        moderator = User(username='mod1', email='mod1@example.com', password='mod123', role='moderator')
        user1 = User(username='user1', email='user1@example.com', password='user123', role='user')
        user2 = User(username='user2', email='user2@example.com', password='user456', role='user')

        db.session.add_all([admin, moderator, user1, user2])
        db.session.commit()

    if Post.query.count() == 0:
        # sample posts authored by different users
        post1 = Post(title='Welcome Post', content='This is the first post.', author_id=1)
        post2 = Post(title='Moderator Update', content='Moderator insights here.', author_id=2)
        post3 = Post(title='User Thoughts', content='User1 shares ideas.', author_id=3)
        post4 = Post(title='Another User Post', content='User2 contributes.', author_id=4)

        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()

    print("Database with sample users and posts.")