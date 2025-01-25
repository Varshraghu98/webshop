from datetime import datetime

#import boto3
import uuid
from flask import Flask, request, jsonify, logging
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import base64
from werkzeug.utils import secure_filename


# Initialize Flask app and SQLAlchemy
def create_app():
    app = Flask(__name__)
    CORS(app)
    # Database configuration

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db:3306/webshop'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Apobangpo_2769@localhost:3306/webshop'
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

@app.route('/cart/<int:id>', methods=['PUT'])
def update_cart_item(id):
    data = request.json  # Expecting a JSON payload with 'quantity'
    cart_item = Cart.query.get_or_404(id)

    try:
        # Update quantity if provided
        new_quantity = data.get('quantity')
        if new_quantity is not None:
            if new_quantity <= 0:
                # Remove the cart item if quantity is zero or less
                db.session.delete(cart_item)
            else:
                cart_item.quantity = new_quantity

        db.session.commit()
        return jsonify({"message": "Cart item updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/cart', methods=['DELETE'])
def delete_cart_contents():
    try:
        cart_item_id = request.args.get('id')  # Optional query parameter to delete a specific item

        if cart_item_id:
            # Delete a specific cart item
            cart_item = Cart.query.get_or_404(cart_item_id)
            db.session.delete(cart_item)
        else:
            # Clear the entire cart
            Cart.query.delete()

        db.session.commit()
        return jsonify({"message": "Cart cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/cart/<int:id>', methods=['DELETE'])
def delete_cart_item(id):
    try:
        # Fetch the cart item by ID
        cart_item = Cart.query.get_or_404(id)

        # Delete the cart item
        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({"message": f"Cart item with ID {id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
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

#Mail Alerts
import smtplib

# Mailtrap configuration
MAILTRAP_USERNAME = "a738c74b91fd48"
MAILTRAP_PASSWORD = "e045f2b6d77ed1"
MAILTRAP_SERVER = "sandbox.smtp.mailtrap.io"
MAILTRAP_PORT = 2525
SENDER = "Test Sender <info@webshop.com>"
RECEIVER = "Test Receiver <testwebshop123@gmail.com>"


# Function to send email
def send_email(subject, body):
    message = f"Subject: {subject}\nTo: {RECEIVER}\nFrom: {SENDER}\n\n{body}"
    try:
        with smtplib.SMTP(MAILTRAP_SERVER, MAILTRAP_PORT) as server:
            server.starttls()
            server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
            server.sendmail(SENDER, RECEIVER, message)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

#orders
class Order(db.Model):
   __tablename__ = 'orders'  # Explicitly specify the table name
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   status = db.Column(db.String(50), nullable=False)
   payment_method = db.Column(db.String(50), nullable=False)
   total_price = db.Column(db.Float, nullable=False)


class OrderDetails(db.Model):
   __tablename__ = 'order_details'
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
   product_id = db.Column(db.Integer, nullable=False)
   quantity = db.Column(db.Integer, nullable=False)
   price_per_unit = db.Column(db.Float, nullable=False)


   order = db.relationship('Order', backref=db.backref('details', lazy=True))


@app.route('/createorder', methods=['POST'])
def create_order():
    data = request.json

    # Validate input data
    required_fields = ["status", "payment_method", "total_price", "products"] #"customer_details",
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields in the request"}), 400

    try:
        # Create the main order
        #customer_details = data['customer_details']
        new_order = Order(
            status=data['status'],
            payment_method=data['payment_method'],
            total_price=data['total_price'],
            #customer_name=customer_details['name'],
            #customer_email=customer_details['email'],
            #customer_street=customer_details['street'],
            #customer_city=customer_details['city'],
            #customer_pincode=customer_details['pincode']
        )
        db.session.add(new_order)
        db.session.commit()

        # Add products to OrderDetails
        products = data['products']
        product_details = []
        for product_id, quantity in products.items():
            # Fetch product details
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404

            product_price = product.price
            product_name = product.name

            order_detail = OrderDetails(
                order_id=new_order.id,
                product_id=product_id,
                quantity=quantity,
                price_per_unit=product_price
            )
            db.session.add(order_detail)

            # Collect product details for the email
            product_details.append(f"{product_name} (x{quantity})")

        db.session.commit()

        # Send email notification
        product_list = "\n".join(product_details)
        subject = "Order Created Successfully"
        body = f"""Hello,\n\nYour order has been successfully created with the following products:\n\n{product_list}\n\nThank you for shopping with us!\n\nWEBSHOP:)"""
        try:
            send_email(subject, body)
        except Exception as email_error:
            logging.error(f"Email sending failed: {email_error}")
            return jsonify({
                "message": "Order created but failed to send email",
                "order_id": new_order.id,
                "email_error": str(email_error)
            }), 201

        return jsonify({
            "message": "Order created successfully",
            "order_id": new_order.id,
            "products": product_details,
            "total_price": new_order.total_price,
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating order: {str(e)}")
        return jsonify({"error": str(e)}), 400


# Read all orders
@app.route('/orders', methods=['GET'])
def get_orders():
   orders = Order.query.all()
   order_list = [
       {
           "id": order.id,
           "status": order.status,
           "payment_method": order.payment_method,
           "total_price": order.total_price,
           "details": [
               {
                   "product_id": detail.product_id,
                   "quantity": detail.quantity,
                   "price_per_unit": detail.price_per_unit
               } for detail in order.details
           ]
       } for order in orders
   ]


   return jsonify(order_list), 200

#view an Order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)

    order_data = {
        "id": order.id,
        "status": order.status,
        "payment_method": order.payment_method,
        "total_price": order.total_price,
        "details": [
            {
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "price_per_unit": detail.price_per_unit
            } for detail in order.details
        ]
    }

    # Send email notification
    subject = "Order Viewed Notification"
    body = f"Hello,\n\nOrder #{order.id} has been viewed.\n\nStatus: {order.status}\nTotal Price: {order.total_price}\n\nThank you!"
    send_email(subject, body)

    return jsonify(order_data), 200

#Update Order
@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.json
    order = Order.query.get_or_404(id)

    try:
        # Update order fields
        order.status = data.get('status', order.status)
        order.payment_method = data.get('payment_method', order.payment_method)
        order.total_price = data.get('total_price', order.total_price)

        # Update order details (optional)
        updated_products = []
        if 'details' in data:
            # Clear existing order details
            for detail in order.details:
                db.session.delete(detail)

            # Add new order details
            for product_id, quantity in data['details'].items():
                product = Product.query.get(product_id)

                # Validate product existence
                if not product:
                    raise ValueError(f"Product with ID {product_id} does not exist.")

                order_detail = OrderDetails(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_per_unit=product.price
                )
                db.session.add(order_detail)

                # Collect product details for email
                updated_products.append(f"{product.name} (x{quantity})")

        db.session.commit()

        # Send email notification
        subject = "Order Updated Notification"
        product_list = "\n".join(updated_products)
        body = (
            f"Hello,\n\nOrder #{order.id} has been updated.\n\n"
            f"Status: {order.status}\n"
            f"Payment Method: {order.payment_method}\n"
            f"Total Price: {order.total_price}\n\n"
            f"Updated Products:\n{product_list}\n\n"
            "Thank you for shopping with us!"
        )
        send_email(subject, body)

        return jsonify({"message": "Order updated successfully"}), 200
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


#Delete / Cancel Order
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)

    try:
        # Delete all order details
        for detail in order.details:
            db.session.delete(detail)

        # Delete the order itself
        db.session.delete(order)
        db.session.commit()

        # Send email notification
        subject = "Alert Order Cancelled !!!"
        body = f"Hello,\n\nOrder #{order.id} has been cancelled.\n\nThank you!"
        send_email(subject, body)

        return jsonify({"message": "Order Cancelled successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
