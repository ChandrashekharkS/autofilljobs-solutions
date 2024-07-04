from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autofilljobs.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

# Define Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Form validation
def validate_form(data):
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return False, "Missing required fields"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('email')):
        return False, "Invalid email format"
    return True, ""

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    valid, message = validate_form(data)
    if not valid:
        return jsonify({'error': message}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Search functionality
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    results = Job.query.filter(Job.title.like(f"%{query}%") | Job.description.like(f"%{query}%")).all()
    return jsonify([{'title': job.title, 'company': job.company, 'location': job.location} for job in results])

# Ensure HTTPS
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)

# Error handling for broken links
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
