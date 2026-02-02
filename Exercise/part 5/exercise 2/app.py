import os
import time
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///performance.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)


# INIT DB

def init_db():
    with app.app_context():
        db.create_all()

        if Product.query.count() == 0:
            products = [
                Product(name=f'Product {i}', price=i * 10)
                for i in range(1, 10001)
            ]
            db.session.bulk_save_objects(products)
            db.session.commit()


# PERFORMANCE TEST

@app.route('/test')
def test_performance():
    start = time.time()

    products = Product.query.filter(Product.price > 500).all()

    end = time.time()
    duration = end - start

    return jsonify({
        "records_fetched": len(products),
        "execution_time_seconds": duration
    })

if __name__ == '__main__':
    init_db()
    app.run()
