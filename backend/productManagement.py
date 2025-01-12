from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and SQLAlchemy
def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:newpassword@localhost:3306/webshop'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

app = create_app()
db = SQLAlchemy(app)

# Define the Product model
class Product(db.Model):
    __tablename__ = 'product'  # Explicitly specify the existing table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=False)  # Image URL from S3
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Create a product
@app.route('/products', methods=['POST'])
def create_product():
    data = request.json

    try:
        new_product = Product(
            category=data['category'],
            image=data['image'],
            name=data['name'],
            description=data['description'],
            price=data['price'],
            id=data['id']
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": "Product created successfully", "product": data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Read all products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = [
        {
            "id": product.id,
            "category": product.category,
            "image": product.image,
            "name": product.name,
            "description": product.description,
            "price": product.price
        } for product in products
    ]

    return jsonify(product_list), 200

# Read a single product
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)

    product_data = {
        "id": product.id,
        "category": product.category,
        "image": product.image,
        "name": product.name,
        "description": product.description,
        "price": product.price
    }

    return jsonify(product_data), 200

# Update a product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    product = Product.query.get_or_404(id)

    try:
        product.category = data.get('category', product.category)
        product.image = data.get('image', product.image)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)

        db.session.commit()

        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete a product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)

    try:
        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
orders = db.relationship('Order', secondary='order_product', back_populates='products')

# Define the Order model
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), nullable=False, unique=True)  # Unique Order ID
    status = db.Column(db.String(50), nullable=False)  # e.g., 'Pending', 'Shipped', 'Delivered'
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., 'Credit Card', 'PayPal'

    products = db.relationship('Product', secondary='order_product', back_populates='orders')

# Define the association table for many-to-many relationship between orders and products
class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)

# Create an order
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json

    try:
        new_order = Order(
            order_id=data['order_id'],
            status=data['status'],
            payment_method=data['payment_method']
        )

        # Add products to the order
        products = Product.query.filter(Product.id.in_(data['product_ids'])).all()
        new_order.products.extend(products)

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "Order created successfully", "order": data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Read all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    order_list = [
        {
            "order_id": order.order_id,
            "status": order.status,
            "payment_method": order.payment_method,
            "products": [{"id": product.id, "name": product.name} for product in order.products]
        } for order in orders
    ]

    return jsonify(order_list), 200

# Read a single order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)

    order_data = {
        "order_id": order.order_id,
        "status": order.status,
        "payment_method": order.payment_method,
        "products": [{"id": product.id, "name": product.name} for product in order.products]
    }

    return jsonify(order_data), 200

# Update an order
@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.json
    order = Order.query.get_or_404(id)

    try:
        order.status = data.get('status', order.status)
        order.payment_method = data.get('payment_method', order.payment_method)

        # Update products if provided
        if 'product_ids' in data:
            products = Product.query.filter(Product.id.in_(data['product_ids'])).all()
            order.products = products  # Replace products list with the new set of products

        db.session.commit()

        return jsonify({"message": "Order updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete an order
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)

    try:
        db.session.delete(order)
        db.session.commit()

        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
        
if __name__ == '__main__':
    app.run(debug=True)
