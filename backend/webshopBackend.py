from datetime import datetime

import boto3
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import base64
from werkzeug.utils import secure_filename


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
    image = db.Column(db.LargeBinary, nullable=False)  #Store image as binary data
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, unique=True)  # Foreign key to Product table
    quantity = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to Product
    product = db.relationship('Product', backref=db.backref('inventory', uselist=False))

class Cart(db.Model):
    __tablename__ = 'cart'  # Specify the table name explicitly

    # Primary Key: Unique ID for each cart item
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Key: Relates to the product table
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Quantity: The number of items of the product in the cart
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationship with Product: Each cart item is associated with one product
    product = db.relationship('Product', backref=db.backref('cart', uselist=False))

    # Timestamp to record when the cart item was added or modified
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



@app.route('/products', methods=['POST'])
def create_product():
    data = request.form  # Use form data to handle both text and file inputs
    file = request.files.get('image')  # Get the image file from the request

    if not file:
        return jsonify({"error": "Image file is required"}), 400

    try:
        # Read the file's binary data
        image_data = file.read()

        # Create a new product record
        new_product = Product(
            category=data['category'],
            image=image_data,  # Store binary data in the database
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            id=int(data['id'])
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": "Product created successfully", "product": {
            "category": data['category'],
            "name": data['name'],
            "description": data['description'],
            "price": data['price'],
            "id": data['id']
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

import base64
from flask import Flask, request, jsonify
from io import BytesIO

@app.route('/products', methods=['GET'])
def get_products():
    def check_inventory(product_id):
        # Query the Inventory table for the specified product ID
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        return inventory.quantity if inventory else 0

    # Get all products
    products = Product.query.all()

    # Filter products based on inventory quantity
    product_list = []
    for product in products:
        if check_inventory(product.id) > 0:
            # Convert the binary image data to base64 string
            image_base64 = base64.b64encode(product.image).decode('utf-8')  # Convert to base64 and decode as UTF-8

            product_data = {
                "id": product.id,
                "category": product.category,
                "image": image_base64,  # Return image as base64 string
                "name": product.name,
                "description": product.description,
                "price": product.price
            }
            product_list.append(product_data)

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

@app.route('/inventory', methods=['GET'])
def get_inventory():
    inventories = Inventory.query.all()
    inventory_list = [
        {
            "product_id": inventory.product_id,
            "product_name": inventory.product.name,
            "quantity": inventory.quantity
        } for inventory in inventories
    ]

    return jsonify(inventory_list), 200

@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.json  # Receive product_id and quantity in the request body
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)  # Default quantity is 1 if not provided

    # Check if the product already exists in the cart
    existing_cart_item = Cart.query.filter_by(product_id=product_id).first()

    if existing_cart_item:
        # If product is already in the cart, update the quantity
        existing_cart_item.quantity += quantity
    else:
        # If product is not in the cart, add it
        new_cart_item = Cart(
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(new_cart_item)

    try:
        db.session.commit()
        return jsonify({"message": "Item added to cart"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/cart', methods=['GET'])
def get_cart_items():
    try:
        # Fetch all cart items (with product details)
        cart_items = Cart.query.all()

        # Prepare the response
        cart_list = []
        for cart_item in cart_items:
            product = cart_item.product  # Get the associated product details

            # Convert image (BLOB) to base64 string if it's stored as BLOB
            if product.image:
                image_base64 = base64.b64encode(product.image).decode('utf-8')
            else:
                image_base64 = None  # In case there's no image stored

            cart_list.append({
                "id": cart_item.id,
                "product_id": cart_item.product_id,
                "name": product.name,
                "category": product.category,
                "image": image_base64,  # Return base64-encoded image
                "description": product.description,
                "price": product.price,
                "quantity": cart_item.quantity
            })

        return jsonify(cart_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


#Utility methods for checkInventory()

#This method is  not used at present can be used in future probably by order management
#For chekcing inventory status before placing order.
def check_inventory(product_id):
    try:
        # Query the Inventory table for the specified product ID
        inventory = Inventory.query.filter_by(product_id=product_id).first()

        if not inventory:
            raise ValueError(f"Product with ID {product_id} not found in inventory")

        # Return the quantity of the product
        return inventory.quantity
    except Exception as e:
        # Handle exceptions (e.g., product not found or database errors)
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)