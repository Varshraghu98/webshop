from datetime import datetime

import boto3
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from botocore.exceptions import NoCredentialsError
import base64
from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText


# Initialize Flask app and SQLAlchemy
def create_app():
    app = Flask(__name__)
    CORS(app)
    # Database configuration


    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db:3306/webshop'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:newpassword@localhost:3306/webshop'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app

app = create_app()
db = SQLAlchemy(app)

# AWS S3 Configuration
S3_BUCKET = "webshopbackendimagestorage"
S3_REGION = "eu-north-1"  # e.g., "us-east-1"
S3_ACCESS_KEY = "Test"
S3_SECRET_KEY = "Test"

s3_client = boto3.client('s3',
                         aws_access_key_id=S3_ACCESS_KEY,
                         aws_secret_access_key=S3_SECRET_KEY,
                         region_name=S3_REGION)

# SMTP Configuration (Modify these based on your SMTP server)
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
SMTP_USERNAME = 'lowtechwebshop@gmail.com'  # Replace with your email
SMTP_PASSWORD = 'miju hizq waiq bxzx'  # Replace with app password
SMTP_DEFAULT_SENDER = 'lowtechwebshop@gmail.com'

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


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

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

# API Routes
@app.route('/inventory', methods=['POST'])
def create_inventory():
    """Create inventory entry for a product."""
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 0)

    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Check if inventory entry already exists
    existing_inventory = Inventory.query.filter_by(product_id=product_id).first()
    if existing_inventory:
        return jsonify({'error': 'Inventory entry already exists'}), 400

    # Create new inventory entry
    new_inventory = Inventory(product_id=product_id, quantity=quantity)
    db.session.add(new_inventory)
    db.session.commit()

    return jsonify({'message': 'Inventory entry created successfully', 'inventory_id': new_inventory.id}), 201

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



# Function to send email using smtplib
def send_email(to_email, subject, body):
    try:
        # Create email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_DEFAULT_SENDER
        msg['To'] = to_email

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)  # Log in to the SMTP server
            server.send_message(msg)  # Send the email

        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

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
   product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False,unique=True)
   product_name = db.Column(db.String(255), nullable=False)
   quantity = db.Column(db.Integer, nullable=False)
   price_per_unit = db.Column(db.Float, nullable=False)

   order = db.relationship('Order', backref=db.backref('details', lazy=True))


@app.route('/createorder', methods=['POST'])
def create_order():
    data = request.json
    try:
        # Step 1: Create the order
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

        # Step 2: Add products to OrderDetails and decrement inventory
        product_details = []
        low_inventory_products = []  # List to track products with low inventory

        for product in data['products']:
            # Deduct inventory
            inventory = Inventory.query.filter_by(product_id=product['id']).first()
            if inventory:
                inventory.quantity -= product['quantity']

                # Check for low inventory (less than 3)
                if inventory.quantity < 3:
                    low_inventory_products.append(
                        f"Product ID: {product['id']}, Name: {product['name']}, Remaining: {inventory.quantity}"
                    )

            # Create order details
            order_detail = OrderDetails(
                order_id=new_order.id,
                product_id=product['id'],
                product_name=product['name'],
                quantity=product['quantity'],
                price_per_unit=product['price']
            )
            db.session.add(order_detail)

            product_details.append(f"{product['name']} (x{product['quantity']}) - €{product['price']}")

        db.session.commit()

        # Step 3: Send confirmation email to the customer
        product_list = "\n".join(product_details)
        subject = "Order Confirmation"
        body = f"""
            Hello {data['name']},

            Thank you for your order! Here are your order details:

            {product_list}

            Total Price: €{data['totalPrice']}

            We appreciate your business!

            Regards,
            Webshop Team
            """
        send_email(data['email'], subject, body)

        # Step 4: Send low inventory alert email
        if low_inventory_products:
            low_inventory_list = "\n".join(low_inventory_products)
            low_inventory_subject = "Low Inventory Alert"
            low_inventory_body = f"""
                Alert! The following products are running low in inventory:

                {low_inventory_list}

                Please restock these items to avoid stockouts.

                Regards,
                Inventory Management Team
                """
            send_email("testscs829@gmail.com", low_inventory_subject, low_inventory_body)

        return jsonify({"message": "Order placed successfully", "order_id": new_order.id}), 201

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

    # Send email notification
    subject = "Order Viewed Notification"
    body = f"Hello,\n\nOrder #{order.id} has been viewed.\n\nName: {order.name}\nTotal Price: {order.total_price}\n\nThank you!"
    send_email(subject, body)

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

        # Send email notification
        subject = "Order Updated Notification"
        product_list = "\n".join(updated_products)
        body = (
            f"Hello,\n\nOrder #{order.id} has been updated.\n\n"
            f"Name: {order.name}\n"
            f"Email: {order.email}\n"
            f"Payment Method: {order.payment_method}\n"
            f"Total Price: {order.total_price}\n\n"
            f"Updated Products:\n{product_list}\n\n"
            "Thank you for shopping with us!"
        )
        send_email(subject, body)

        return jsonify({"message": "Order updated successfully"}), 200
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