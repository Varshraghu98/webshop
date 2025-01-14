import boto3
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


# Initialize Flask app and SQLAlchemy
def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db:3306/webshop'
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

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, unique=True)  # Foreign key to Product table
    quantity = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to Product
    product = db.relationship('Product', backref=db.backref('inventory', uselist=False))


# AWS S3 Configuration
S3_BUCKET = 'your-s3-bucket-name'
S3_REGION = 'your-region'  # e.g., 'us-east-1'
S3_ACCESS_KEY = 'your-access-key'
S3_SECRET_KEY = 'your-secret-key'

# Initialize boto3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

@app.route('/products', methods=['POST'])
def create_product():
    data = request.form  # Use form data to handle both text and file inputs
    file = request.files.get('image')  # Get the image file from the request

    if not file:
        return jsonify({"error": "Image file is required"}), 400

    try:
        # Generate a unique filename and upload to S3
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={"ContentType": file.content_type, "ACL": "public-read"}  # Make the file publicly readable
        )

        # Construct the file URL
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

        # Create a new product record
        new_product = Product(
            category=data['category'],
            image=file_url,  # Store only the S3 URL in the database
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            id=int(data['id'])
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": "Product created successfully", "product": {
            "category": data['category'],
            "image": file_url,
            "name": data['name'],
            "description": data['description'],
            "price": data['price'],
            "id": data['id']
        }}), 201
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
    product_list = [
        {
            "id": product.id,
            "category": product.category,
            "image": product.image,
            "name": product.name,
            "description": product.description,
            "price": product.price
        }
        for product in products if check_inventory(product.id) > 0
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
