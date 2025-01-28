from datetime import datetime

import boto3
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from botocore.exceptions import NoCredentialsError
import base64
from flask import Flask, request, jsonify


# Initialize Flask app and SQLAlchemy
def create_app():
    app = Flask(__name__)
    CORS(app)
    # Database configuration


    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db:3306/webshop'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/webshop'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

app = create_app()
db = SQLAlchemy(app)

# AWS S3 Configuration
S3_BUCKET = "webshopbackendimagestorage"
S3_REGION = "eu-north-1"  # e.g., "us-east-1"
S3_ACCESS_KEY = "test"
S3_SECRET_KEY = "test"


s3_client = boto3.client('s3',
                         aws_access_key_id=S3_ACCESS_KEY,
                         aws_secret_access_key=S3_SECRET_KEY,
                         region_name=S3_REGION)

# Define the Product model
class Product(db.Model):
    __tablename__ = 'product'  # Explicitly specify the existing table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)  # Store image URL
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
    data = request.form
    file = request.files.get('image')

    if not file:
        return jsonify({"error": "Image file is required"}), 400

    try:
        # Upload the image to S3
        file_name = f"products/{file.filename}"
        s3_client.upload_fileobj(file, S3_BUCKET, file_name, ExtraArgs={"ContentType": file.content_type})

        # Construct the S3 URL
        image_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"

        # Create a new product record
        new_product = Product(
            category=data['category'],
            image_url=image_url,  # Store the image URL in the database
            name=data['name'],
            description=data['description'],
            price=float(data['price'])
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product": {
                "category": data['category'],
                "name": data['name'],
                "description": data['description'],
                "price": data['price'],
                "image_url": image_url
            }
        }), 201
    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not found"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

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
            product_data = {
                "id": product.id,
                "category": product.category,
                "image_url": product.image_url,  # Return image URL
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


from flask import jsonify

@app.route('/cart', methods=['GET'])
def get_cart_items():
    try:
        # Fetch all cart items (with product details)
        cart_items = Cart.query.all()

        # Prepare the response
        cart_list = []
        for cart_item in cart_items:
            product = cart_item.product  # Get the associated product details

            cart_list.append({
                "id": cart_item.id,
                "product_id": cart_item.product_id,
                "name": product.name,
                "category": product.category,
                "image_url": product.image_url,  # Use the image_url directly
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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "lowtechwebshop@gmail.com"  # Your Gmail address
PASSWORD = "csou eagd kiah tevi"  # Your Gmail App Password
SENDER = "Webshop <lowtechwebshop@gmail.com>"


def send_email(subject, body, recipient_email):
    """Function to send emails using Gmail SMTP"""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)

        # Create a multipart message
        message = MIMEMultipart()
        message['Subject'] = subject
        message['To'] = recipient_email
        message['From'] = SENDER

        # Attach the HTML body to the message
        message.attach(MIMEText(body, 'html'))

        server.sendmail(USERNAME, recipient_email, message.as_string())
        server.quit()
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


#orders
class Order(db.Model):
   __tablename__ = 'orders'  # Explicitly specify the table name
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   name = db.Column(db.String(255), nullable=False)
   email = db.Column(db.String(255), nullable=False)
   street = db.Column(db.String(255), nullable=False)
   city = db.Column(db.String(255), nullable=False)
   pincode = db.Column(db.String(10), nullable=False)
   payment_successful = db.Column(db.Boolean, nullable=False)
   payment_method = db.Column(db.String(50), nullable=False)
   total_price = db.Column(db.Float, nullable=False)

class OrderDetails(db.Model):
   __tablename__ = 'order_details'
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
   product_id = db.Column(db.Integer, nullable=False)
   product_name = db.Column(db.String(255), nullable=False)
   quantity = db.Column(db.Integer, nullable=False)
   price_per_unit = db.Column(db.Float, nullable=False)

   order = db.relationship('Order', backref=db.backref('details', lazy=True))
@app.route('/createorder', methods=['POST'])
def create_order():
    data = request.json

    try:
        # Create the main order
        new_order = Order(
            name=data['name'],
            email=data['email'],
            street=data['street'],
            city=data['city'],
            pincode=data['pincode'],
            payment_successful=data['paymentSuccessful'],
            payment_method=data['paymentMethod'],
            total_price=data['totalPrice']
        )
        db.session.add(new_order)
        db.session.commit()

        # Add products to OrderDetails
        products = data['products']
        product_details = []
        for product in products:
            order_detail = OrderDetails(
                order_id=new_order.id,
                product_id=product['id'],
                product_name=product['name'],
                quantity=product['quantity'],
                price_per_unit=product['price']
            )
            db.session.add(order_detail)

            # Collect product details for the email
            product_details.append(f"{product['name']} (x{product['quantity']})")

        db.session.commit()

        # Sending email notification for order placement
        # Sending email notification for order placement
        product_list = "<br>".join(product_details)  # Use <br> for line breaks in HTML
        subject = "Order Confirmation - Webshop"
        body = f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; background-color: #f8f9fa; color: #333; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background: #fff; }}
                h1 {{ color: #28a745; }} /* Green color for confirmation */
                h3 {{ color: #333; }}
                p {{ margin: 10px 0; }}
                .total-price {{ font-weight: bold; font-size: 1.2em; color: #d9534f; }}
                .thank-you {{ margin-top: 20px; font-style: italic; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #666; text-align: center; }}
                .product-list {{ background: #f1f1f1; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Order Confirmation</h1>
                <p>Hello {data['name']},</p>
                <p>Your order has been placed successfully!</p>
                <h3>Items Ordered:</h3>
                <div class="product-list"><pre>{product_list}</pre></div>
                <p class="total-price">Total Price: {data['totalPrice']} EUR</p>
                <p>Thank you for shopping with us!</p>
                <p class="thank-you">- Team Webshop</p>
            </div>
            <div class="footer">If you have any questions, feel free to contact our support team.</div>
        </body>
        </html>
        """

        send_email(subject, body, data['email'])

        return jsonify({"message": "Yay!!! Your Order placed successfully", "order_id": new_order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
# Read all orders
@app.route('/orders', methods=['GET'])
def get_orders():
   orders = Order.query.all()
   order_list = [
       {
           "id": order.id,
           "name": order.name,
           "email": order.email,
           "street": order.street,
           "city": order.city,
           "pincode": order.pincode,
           "payment_successful": order.payment_successful,
           "payment_method": order.payment_method,
           "total_price": order.total_price,
           "details": [
               {
                   "product_id": detail.product_id,
                   "product_name": detail.product_name,
                   "quantity": detail.quantity,
                   "price_per_unit": detail.price_per_unit
               } for detail in order.details
           ]
       } for order in orders
   ]

   return jsonify(order_list), 200

# View an Order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)

    order_data = {
        "id": order.id,
        "name": order.name,
        "email": order.email,
        "street": order.street,
        "city": order.city,
        "pincode": order.pincode,
        "payment_successful": order.payment_successful,
        "payment_method": order.payment_method,
        "total_price": order.total_price,
        "details": [
            {
                "product_id": detail.product_id,
                "product_name": detail.product_name,
                "quantity": detail.quantity,
                "price_per_unit": detail.price_per_unit
            } for detail in order.details
        ]
    }

    return jsonify(order_data), 200

# Update Order
@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.json
    order = Order.query.get_or_404(id)

    try:
        # Update order fields
        order.name = data.get('name', order.name)
        order.email = data.get('email', order.email)
        order.street = data.get('street', order.street)
        order.city = data.get('city', order.city)
        order.pincode = data.get('pincode', order.pincode)
        order.payment_successful = data.get('paymentSuccessful', order.payment_successful)
        order.payment_method = data.get('paymentMethod', order.payment_method)
        order.total_price = data.get('totalPrice', order.total_price)

        # Update order details (optional)
        updated_products = []
        if 'products' in data:
            # Clear existing order details
            for detail in order.details:
                db.session.delete(detail)

            # Add new order details
            for product in data['products']:
                order_detail = OrderDetails(
                    order_id=order.id,
                    product_id=product['id'],
                    product_name=product['name'],
                    quantity=product['quantity'],
                    price_per_unit=product['price']
                )
                db.session.add(order_detail)

                # Collect product details for email
                updated_products.append(f"{product['name']} (x{product['quantity']})")

        db.session.commit()

        return jsonify({"message": "Order updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete / Cancel Order
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)

    try:
        email = order.email
        # Delete all order details
        for detail in order.details:
            db.session.delete(detail)

        # Delete the order itself
        db.session.delete(order)
        db.session.commit()

        # Send email notification for order cancellation
        subject = "Order Cancellation - Webshop"
        body = f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; background-color: #f8f9fa; color: #333; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background: #fff; }}
                h1 {{ color: #d9534f; }} /* Red color for cancellation */
                p {{ margin: 10px 0; }}
                .support {{ font-weight: bold; }}
                .thank-you {{ margin-top: 20px; font-style: italic; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Order Canceled</h1>
                <p>Hello {order.name},</p>
                <p>Your order <strong>#{id}</strong> has been successfully canceled.</p>
                <p>If this was a mistake, please contact our support team.</p>
                <p class="support">Thank you for shopping with us!</p>
                <p class="thank-you">- Team Webshop</p>
            </div>
            <div class="footer">If you have any questions, feel free to contact our support team.</div>
        </body>
        </html>
        """

        send_email(subject, body, email)

        return jsonify({"message": "Order Cancelled successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/mock-payment', methods=['POST'])
def mock_payment():
    data = request.json
    card_number = data.get('cardNumber')
    expiry = data.get('expiry')
    cvv = data.get('cvv')

    # Mock validation logic
    if not card_number or not expiry or not cvv:
        return jsonify({"success": False, "message": "Invalid payment details"}), 400

    # Mock payment success
    return jsonify({"success": True, "message": "Payment processed successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
