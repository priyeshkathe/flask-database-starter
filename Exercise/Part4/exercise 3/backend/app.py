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
# NORMAL BOOK API (NO PAGINATION)
# ======================

@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [b.to_dict() for b in books]
    })

# ======================
# PAGINATION API (EXERCISE 3)
# ======================

@app.route('/api/books-with-pagination', methods=['GET'])
def get_books_with_pagination():
    # Read query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Paginate query
    pagination = Book.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    books = pagination.items

    return jsonify({
        'success': True,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total_books': pagination.total,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
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

    for i in range(1, 21):
        book = Book(
            title=f"Book {i}",
            year=2000 + i,
            author_id=a1.id if i % 2 == 0 else a2.id
        )
        db.session.add(book)

    db.session.commit()
    return "Sample data added!"

# ======================
# RUN APP
# ======================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
