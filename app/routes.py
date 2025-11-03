from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from .models import User, Post
from . import db
from sqlalchemy import text
from datetime import datetime, timezone

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get username and password
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # if not submitted
        if not username or not password:
            flash('Please enter both username and password.')
            return redirect(url_for('main.login'))

        # query with username
        user = User.query.filter_by(username=username).first()

        # if username is found and password is correct
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            current_app.logger.info(f"Login validated successfully: IP {request.remote_addr} - Username: {username}")
            return redirect(url_for('main.dashboard'))
        else:
            current_app.logger.warning(f"Login failed: Invalid username or password from IP {request.remote_addr} - Username: {username}")
            flash('Invalid username or password.')

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if not session.get('user_id'): # if user is not logged in
        flash('You are not logged in, please log in first.')
        return redirect(url_for('main.login'))

    role = session.get('role')
    username = session.get('username')

    all_posts = []

    if role == 'admin': # dashboard view based on if the user's role is 'admin'
        posts = db.session.query(Post).join(User, Post.author_id == User.id).all()
        all_posts = [ # attributes that display, given in spec
            {
                'id': p.id,
                'title': p.title,
                'content': p.content,
                'author': p.author.username,
                'email': p.author.email,
                'role': p.author.role
            }
            for p in posts
        ]

    elif role == 'moderator': # dashboard view based on if the user's role is 'moderator'
        posts = db.session.query(Post).join(User, Post.author_id == User.id).all()
        all_posts = [ # attributes that display, given in spec
            {
                'title': p.title,
                'author': p.author.username,
                'id': p.id
            }
            for p in posts
        ]

    elif role == 'user': # dashboard view based on if the user's role is 'user'
        user_id = session.get('user_id')
        posts = Post.query.filter_by(author_id=user_id).all()
        all_posts = [ # attributes that display, given in spec
            {
                'id': p.id,
                'title': p.title,
                'content': p.content,
                'author': p.author.username,
                'email': p.author.email,
                'role': p.author.role
            }
            for p in posts
        ]

    else: # if no user role
        flash('No role selected.')
        return redirect(url_for('main.login'))

    return render_template('dashboard.html', posts=all_posts, username=username, role=role)

@main.route('/search')
def search():
    # if user is logged in
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('main.login'))

    # get search term from query
    term = request.args.get('term', '').strip()
    if not term:
        current_app.logger.warning(f"Empty search term: IP {request.remote_addr} - Username: {session.get('username')}")
        flash("Please enter a search term.")
        return redirect(url_for('main.dashboard'))

    # define SQL query using sqlalchemy
    stmt = text("""
        SELECT p.id, p.title, p.content, u.username
        FROM posts AS p
        JOIN users AS u ON p.author_id = u.id
        WHERE p.title LIKE :term OR p.content LIKE :term
    """)

    # bind parameters
    params = {"term": f"%{term}%"}
    # execute query
    result = db.session.execute(stmt, params).fetchall()

    # audit log
    current_app.logger.info("Executed SQL: %s | Params: %s", stmt, params)

    # results
    posts = [
        {"id": r.id, "title": r.title, "content": r.content, "author": r.username}
        for r in result
    ]

    # flash for user showing results
    flash(f"{len(posts)} post(s) found for '{term}'.")
    return render_template('dashboard.html', posts=posts, search_term=term)

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('main.login'))