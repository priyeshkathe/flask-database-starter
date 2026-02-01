from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ======================
# APP CONFIG
# ======================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ======================
# MODELS
# ======================

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    city = db.Column(db.String(100))

    # One Author -> Many Books
    books = db.relationship('Book', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'city': self.city
        }


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key -> Author
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'isbn': self.isbn,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat()
        }

# ======================
# HOME ROUTE
# ======================

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Book & Author API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            h2 { color: #00d4ff; margin-top: 30px; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; color: white; }
            .get { background: #27ae60; }
            .post { background: #f39c12; }
            .put { background: #3498db; }
            .delete { background: #e74c3c; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>📚 Book & Author API</h1>
        <p>REST API for managing books and authors</p>

        <h2>Author Endpoints:</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/authors</code> - Create author
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/authors</code> - Get all authors
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/authors/&lt;id&gt;</code> - Get author by ID
        </div>
        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/authors/&lt;id&gt;</code> - Update author
        </div>
        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/authors/&lt;id&gt;</code> - Delete author
        </div>

        <h2>Book Endpoints:</h2>
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/books</code> - Create book
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books</code> - Get all books
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/&lt;id&gt;</code> - Get book by ID
        </div>
        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/books/&lt;id&gt;</code> - Update book
        </div>
        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/books/&lt;id&gt;</code> - Delete book
        </div>

        <h2>Quick Test:</h2>
        <a href="/api/authors" style="color: #e94560; font-size: 16px;">Click here to view all authors →</a>
    </body>
    </html>
    '''


# ======================
# AUTHOR CRUD APIs
# ======================

@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': 'Author name required'}), 400

    author = Author(
        name=data['name'],
        bio=data.get('bio'),
        city=data.get('city')
    )

    db.session.add(author)
    db.session.commit()

    return jsonify({'success': True, 'author': author.to_dict()}), 201


@app.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify({
        'success': True,
        'count': len(authors),
        'authors': [a.to_dict() for a in authors]
    })


@app.route('/api/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    return jsonify({'success': True, 'author': author.to_dict()})


@app.route('/api/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    data = request.get_json()

    author.name = data.get('name', author.name)
    author.bio = data.get('bio', author.bio)
    author.city = data.get('city', author.city)

    db.session.commit()

    return jsonify({'success': True, 'author': author.to_dict()})


@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Author deleted'})


# ======================
# BOOK CRUD APIs
# ======================

@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()

    if not data or not data.get('title') or not data.get('author_id'):
        return jsonify({'success': False, 'error': 'Title and Author required'}), 400

    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    book = Book(
        title=data['title'],
        year=data.get('year'),
        isbn=data.get('isbn'),
        author_id=data['author_id']
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({'success': True, 'book': book.to_dict()}), 201


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [b.to_dict() for b in books]
    })


@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    return jsonify({'success': True, 'book': book.to_dict()})


@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    book.title = data.get('title', book.title)
    book.year = data.get('year', book.year)
    book.isbn = data.get('isbn', book.isbn)

    db.session.commit()

    return jsonify({'success': True, 'book': book.to_dict()})


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Book deleted'})


# ======================
# RUN APP
# ======================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
