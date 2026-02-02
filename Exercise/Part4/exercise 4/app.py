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

    books = db.relationship('Book', backref='author', lazy=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'author': self.author.name if self.author else None
        }

# ======================
# HOME ROUTE
# ======================

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Book Sorting API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            h2 { color: #00d4ff; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; color: white; }
            .get { background: #27ae60; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
            a { color: #e94560; }
        </style>
    </head>
    <body>
        <h1>📚 Book Sorting API (Exercise 4)</h1>
        
        <h2>Setup:</h2>
        <div class="endpoint">
            First, <a href="/init">click here to initialize sample data</a>
        </div>

        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books-with-sorting?sort=title&order=asc</code>
            <br>Get books with sorting
            <br><a href="/api/books-with-sorting" target="_blank">Try it →</a>
        </div>

        <h2>Sorting Parameters:</h2>
        <p><strong>sort:</strong> id, title, year, created_at</p>
        <p><strong>order:</strong> asc, desc</p>

        <h2>Examples:</h2>
        <ul>
            <li><a href="/api/books-with-sorting?sort=title&order=asc" target="_blank">/api/books-with-sorting?sort=title&order=asc</a></li>
            <li><a href="/api/books-with-sorting?sort=year&order=desc" target="_blank">/api/books-with-sorting?sort=year&order=desc</a></li>
            <li><a href="/api/books-with-sorting?sort=created_at&order=asc" target="_blank">/api/books-with-sorting?sort=created_at&order=asc</a></li>
        </ul>
    </body>
    </html>
    '''

# ======================
# BOOK SORTING API (EXERCISE 4)
# ======================

@app.route('/api/books-with-sorting', methods=['GET'])
def get_books_with_sorting():
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    # Allowed fields for sorting
    sort_columns = {
        'id': Book.id,
        'title': Book.title,
        'year': Book.year,
        'created_at': Book.created_at
    }

    # Default sort column
    sort_column = sort_columns.get(sort, Book.id)

    # Order handling
    if order == 'desc':
        query = Book.query.order_by(sort_column.desc())
    else:
        query = Book.query.order_by(sort_column.asc())

    books = query.all()

    return jsonify({
        'success': True,
        'sort': sort,
        'order': order,
        'count': len(books),
        'books': [b.to_dict() for b in books]
    })

# ======================
# SAMPLE DATA (OPTIONAL)
# ======================

@app.route('/init')
def init_data():
    a1 = Author(name="Author One")
    a2 = Author(name="Author Two")

    db.session.add_all([a1, a2])
    db.session.commit()

    books = [
        Book(title="Flask Guide", year=2022, author_id=a1.id),
        Book(title="Python Basics", year=2020, author_id=a2.id),
        Book(title="Clean Code", year=2008, author_id=a1.id),
        Book(title="Data Structures", year=2019, author_id=a2.id),
    ]

    db.session.add_all(books)
    db.session.commit()

    return "Sample data added!"

# ======================
# RUN APP
# ======================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
