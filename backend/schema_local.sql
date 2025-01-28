

DROP TABLE inventory;
DROP TABLE CART;
DROP TABLE product;
DROP TABLE ORDER_DETAILS;
DROP TABLE ORDERS;



CREATE TABLE product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    NAME VARCHAR(100) NOT NULL,
    DESCRIPTION TEXT NOT NULL,
    price FLOAT NOT NULL
);


CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    payment_successful BOOLEAN NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    total_price FLOAT NOT NULL
);

CREATE TABLE order_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);



CREATE TABLE inventory (
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

====================================================INSERT SCRIPTS============================
INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'chair',
    'image',
    'computer chair',
    'description',
    '1'
  );

  INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
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
  `image_url`,
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
  
   INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'comp table',
    'table description',
    '18'
  );
  
   INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'kinder table',
    'table description',
    '25'
  );

   INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'dinning table',
    'table description',
    '25'
  );

 INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'coffee table',
    'table description',
    '25'
  );
  
   INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'tea table',
    'table description',
    '25'
  );
  
    INSERT INTO `webshop`.`product` (

  `category`,
  `image_url`,
  `name`,
  `description`,
  `price`
)VALUES
  (

    'table',
    'image',
    'study table',
    'table description',
    '25'
  );
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (1, 1, 3);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (2, 2, 2);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (3, 3, 8);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (4, 4, 5);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (5, 5, 6);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (6, 6, 6);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (7, 7, 6);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (8, 8, 6);
INSERT INTO `webshop`.`Inventory` (`id`, `product_id`, `quantity`)
VALUES (9, 9, 6);
