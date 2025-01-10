from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:newpassword@localhost:3306/webshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Inventory model
class Inventory(db.Model):
    __tablename__ = 'inventory'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

# Create all tables in the database
with app.app_context():
    db.create_all()  # This will create the 'inventory' table if it doesn't already exist
    print("Tables created successfully!")

# Route to add inventory items
@app.route('/add-inventory', methods=['POST'])
def add_inventory():
    data = request.json  # Get data from the request body

    try:
        # Create a new Inventory item
        new_item = Inventory(
            product_id=data['product_id'],
            stock_quantity=data['stock_quantity']
        )
        db.session.add(new_item)  # Add the item to the session
        db.session.commit()  # Commit to the database

        return {"message": "Inventory item added successfully!"}, 201
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        return {"error": str(e)}, 400

# Get all inventory items
@app.route('/inventory', methods=['GET'])
def get_all_inventory():
    items = Inventory.query.all()
    result = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "stock_quantity": item.stock_quantity
        }
        for item in items
    ]
    return jsonify(result), 200

# Get inventory item by ID
@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = Inventory.query.get(item_id)
    if not item:
        return {"message": "Inventory item not found"}, 404
    result = {
        "id": item.id,
        "product_id": item.product_id,
        "stock_quantity": item.stock_quantity
    }
    return jsonify(result), 200

# Get all inventory items
@app.route('/inventory', methods=['GET'])
def get_all_inventory():
    items = Inventory.query.all()
    result = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "stock_quantity": item.stock_quantity
        }
        for item in items
    ]
    return jsonify(result), 200

# Get inventory item by ID
@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = Inventory.query.get(item_id)
    if not item:
        return {"message": "Inventory item not found"}, 404
    result = {
        "id": item.id,
        "product_id": item.product_id,
        "stock_quantity": item.stock_quantity
    }
    return jsonify(result), 200

@app.route('/inventory/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    item = Inventory.query.get(item_id)
    if not item:
        return {"message": "Inventory item not found"}, 404
    try:
        item.product_id = data.get('product_id', item.product_id)
        item.stock_quantity = data.get('stock_quantity', item.stock_quantity)
        db.session.commit()
        return {"message": "Inventory item updated successfully!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400

@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    item = Inventory.query.get(item_id)
    if not item:
        return {"message": "Inventory item not found"}, 404
    try:
        db.session.delete(item)
        db.session.commit()
        return {"message": "Inventory item deleted successfully!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400


# Route to test the connection
@app.route('/')
def home():
    return "Flask is connected to MySQL successfully!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
