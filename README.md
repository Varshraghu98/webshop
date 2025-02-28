# Webshop

This repository hosts the UI and backend components for the Webshop project.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
  - [Backend Setup](#backend-setup)
  - [UI Setup](#ui-setup)
- [Deployment on AWS](#deployment-on-aws)
  - [Backend Deployment](#backend-deployment)
  - [UI Deployment](#ui-deployment)
- [Database Initialization](#database-initialization)
- [Contributing](#contributing)


## Prerequisites

- **Python 3.8+**: Required for the backend service.
- **Node.js 14+ and npm**: Required for the UI.
- **MySQL 5.7+**: Database for the application.
- **AWS Account**: For deployment on AWS.

## Local Setup

### Backend Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Varshraghu98/webshop.git
   cd webshop/backend
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the Database**:

   Ensure MySQL is running and execute the SQL scripts located in the `backend/schema.sql` directory to set up the database schema.

6. **Run the Backend Server**:

   ```bash
   python3 webshopBackend.py
   ```

   The backend server should now be running on `http://localhost:5000/`.

### UI Setup

1. **Navigate to the UI Directory**:

   ```bash
   cd ../webshop_ui
   ```

2. **Install Dependencies**:

   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
    
Navigate to the webshop_ui/.env.development update the backend URLs to be used 
 ```bash
    VITE_APP_API_GET_PRODUCTS_URL=http://127.0.0.1:5000/products
    VITE_APP_API_POST_CART_URL = http://127.0.0.1:5000/cart
   ```


4. **Run the UI Application**:

   ```bash
   npm start
   ```

   The UI should now be running on `http://localhost:5173/`.

## Deployment on AWS

### Backend Deployment

1. **Set Up an EC2 Instance**:

   - Launch an EC2 instance with Amazon Linux 2 AMI.
   - Ensure security groups allow inbound traffic on the necessary ports (e.g., 5000 for the backend API, 5173 for UI ).

2. **Install Dependencies on EC2**:

   - SSH into the EC2 instance.
   - Install Python 3:

     ```bash
     sudo apt update -y
     sudo apt install python3
     ```

   - Install required Python packages:

     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up the Database**:

   - Use Amazon RDS to set up a MySQL database instance.
   - Update the backend's `webshopBackend.py` file with the RDS endpoint and credentials.

4. **Run the Backend Server**:

   - Start the backend server:

     ```bash
      python3 webshopBackend.py
     ```

   - Ensure the server is running and accessible.
5. **Setup UI on EC2 instance**:
- To run the UI on EC2 Node and npm are required. 
- Ensure node and npm are installed and setup on node.
- Replace the config URL with flask backend URL running on EC2.
- On EC2 instance navigate to the `webshop_ui` directory and run:
- Navigate to the src folder and run 
- 

    ```bash
    npm install 
    npm run dev -- --host
    ```
This will start UI.

## Setting Up S3 for Image Storage

   - Create an S3 bucket in AWS specifically for storing images.
   - Upload images through the API, which will store them in the S3 bucket.

1. **Create an S3 Bucket**:

   - Log in to your AWS console.
   - Navigate to **S3** and click **Create bucket**.
   - Enter the bucket name (e.g., `webshop-images-bucket`).
   - Select a region close to your users.
   - Click **Create bucket**.
   - Ensure a new IAM user is created with permissions to access S3 bucket through code. 

2. **Set Up Permissions**:

   - Go to the **Permissions** tab of your bucket.
   - Under **Bucket policy**, add a policy to allow your application to store and retrieve images:

     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Principal": "*",
           "Action": [
             "s3:PutObject",
             "s3:GetObject"
           ],
           "Resource": "arn:aws:s3:::webshop-images-bucket/*"
         }
       ]
     }
     ```

   - Save changes.

## POSTMAN 

All the backend APIs can be easily tested by imported the postman collection located at backend/WebShop postman_collection.json into local postman client.  


## Database Initialization

The database schema isn't automatically created, execute the SQL scripts located in the `backend/schema.sql` directory against your MySQL database to set up the necessary tables and data.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

