import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text

# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool (useful for PostgreSQL)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)

# =============================================================================
# MODEL
# =============================================================================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Product {self.name}>'

# =============================================================================
# DATABASE CONNECTION CHECK
# =============================================================================
def check_db_connection():
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        print("✅ Database connection successful")
        return True
    except OperationalError as e:
        print("❌ Database connection failed:", e)
        return False

# =============================================================================
# ROUTES
# =============================================================================
@app.route('/')
def index():
    try:
        products = Product.query.all()
    except SQLAlchemyError:
        flash("Database connection error. Please try again later.", "danger")
        products = []

    return render_template(
        'index.html',
        products=products,
        db_url=DATABASE_URL
    )


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            new_product = Product(
                name=request.form['name'],
                price=float(request.form['price']),
                stock=int(request.form.get('stock', 0)),
                description=request.form.get('description', '')
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Failed to add product (DB error)', 'danger')

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete_product(id):
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Failed to delete product (DB error)', 'danger')

    return redirect(url_for('index'))

# =============================================================================
# INITIALIZE DATABASE
# =============================================================================
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print(f'📦 Database initialized! Using: {DATABASE_URL}')

            if Product.query.count() == 0:
                sample_products = [
                    Product(name='Laptop', price=999.99, stock=10, description='High-performance laptop'),
                    Product(name='Mouse', price=29.99, stock=50, description='Wireless mouse'),
                    Product(name='Keyboard', price=79.99, stock=30, description='Mechanical keyboard'),
                ]
                db.session.add_all(sample_products)
                db.session.commit()
                print('🧪 Sample products added!')
    except SQLAlchemyError as e:
        print("❌ Database initialization failed:", e)

# =============================================================================
# RUN APPLICATION
# =============================================================================
if __name__ == '__main__':
    check_db_connection()
    init_db()
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')
