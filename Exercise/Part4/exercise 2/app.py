from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# -----------------------------------------------------------------------------
# APP CONFIG
# -----------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # allow frontend from anywhere

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# MODELS
# -----------------------------------------------------------------------------

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))

    books = db.relationship('Book', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'city': self.city
        }


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(
        db.Integer,
        db.ForeignKey('authors.id'),
        nullable=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'isbn': self.isbn,
            'author': {
                'id': self.author.id,
                'name': self.author.name
            },
            'created_at': self.created_at.isoformat()
        }

# -----------------------------------------------------------------------------
# AUTHOR CRUD ROUTES
# -----------------------------------------------------------------------------

@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify({
        'success': True,
        'count': len(authors),
        'authors': [a.to_dict() for a in authors]
    })


@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({
            'success': False,
            'error': 'Author name is required'
        }), 400

    author = Author(
        name=data['name'],
        bio=data.get('bio'),
        city=data.get('city')
    )

    db.session.add(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'author': author.to_dict()
    }), 201


@app.route('/api/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({
            'success': False,
            'error': 'Author not found'
        }), 404

    return jsonify({
        'success': True,
        'author': author.to_dict()
    })


@app.route('/api/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({
            'success': False,
            'error': 'Author not found'
        }), 404

    data = request.get_json()

    if 'name' in data:
        author.name = data['name']
    if 'bio' in data:
        author.bio = data['bio']
    if 'city' in data:
        author.city = data['city']

    db.session.commit()

    return jsonify({
        'success': True,
        'author': author.to_dict()
    })


@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({
            'success': False,
            'error': 'Author not found'
        }), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Author deleted successfully'
    })

# -----------------------------------------------------------------------------
# BOOK CRUD ROUTES
# -----------------------------------------------------------------------------

@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [b.to_dict() for b in books]
    })


@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()

    if not data or not data.get('title') or not data.get('author_id'):
        return jsonify({
            'success': False,
            'error': 'Title and author_id are required'
        }), 400

    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({
            'success': False,
            'error': 'Author not found'
        }), 404

    book = Book(
        title=data['title'],
        year=data.get('year'),
        isbn=data.get('isbn'),
        author_id=data['author_id']
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'book': book.to_dict()
    }), 201


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({
            'success': False,
            'error': 'Book not found'
        }), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })

# -----------------------------------------------------------------------------
# RUN SERVER
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
