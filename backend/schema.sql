CREATE DATABASE webshop;

USE webshop;

CREATE TABLE product ( id INT AUTO_INCREMENT PRIMARY KEY,
category VARCHAR(100) NOT NULL,
 image VARCHAR(255) NOT NULL,
name VARCHAR(100) NOT NULL,
description TEXT NOT NULL,
price FLOAT NOT NULL );


CREATE TABLE Inventory (
 id INT AUTO_INCREMENT PRIMARY KEY,
 product_id INT NOT NULL UNIQUE,
 quantity INT NOT NULL DEFAULT 0,
 FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE ON UPDATE CASCADE);


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
