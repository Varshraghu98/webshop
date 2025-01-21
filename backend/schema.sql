CREATE DATABASE webshop;

USE webshop;

CREATE TABLE product ( id INT AUTO_INCREMENT PRIMARY KEY,
category VARCHAR(100) NOT NULL,
 image VARCHAR(255) NOT NULL,
name VARCHAR(100) NOT NULL,
description TEXT NOT NULL,
price FLOAT NOT NULL );

ALTER TABLE product MODIFY COLUMN image LONGBLOB;

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    total_price FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    street VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL
);

CREATE TABLE order_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
);

INSERT INTO orders (name, status, payment_method, total_price, street, city, country, pincode, email)
VALUES
    ('John Doe', 'Pending', 'Credit Card', 399.99, '123 Main St', 'New York', 'USA', '10001', 'johndoe@example.com'),
    ('Jane Smith', 'Shipped', 'PayPal', 149.99, '456 Elm St', 'Los Angeles', 'USA', '90001', 'janesmith@example.com'),
    ('Alice Johnson', 'Delivered', 'Credit Card', 249.99, '789 Oak St', 'Chicago', 'USA', '60601', 'alicejohnson@example.com'),
    ('Bob Brown', 'Cancelled', 'Bank Transfer', 89.99, '321 Pine St', 'Houston', 'USA', '77001', 'bobbrown@example.com');



CREATE TABLE Inventory (
 id INT AUTO_INCREMENT PRIMARY KEY,
 product_id INT NOT NULL UNIQUE,
 quantity INT NOT NULL DEFAULT 0,
 FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE ON UPDATE CASCADE);


CREATE TABLE cart (
id INT AUTO_INCREMENT PRIMARY KEY,
product_id INT,
quantity INT DEFAULT 1,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (product_id) REFERENCES product(id) );


 INSERT INTO `webshop`.`product` (

  `category`,
  `image`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'chair',
    'image',
    'computer chair',
    'description',
    '12'
  );

  INSERT INTO `webshop`.`product` (

  `category`,
  `image`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'chair',
    'image',
    'kinder chair',
    'description',
    '15'
  );

  INSERT INTO `webshop`.`product` (

  `category`,
  `image`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'chair',
    'image',
    'some chair',
    'description',
    '32'
  );


INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (1, 1, 3);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (2, 2, 2);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (3, 3, 8);


