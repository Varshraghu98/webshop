import React from 'react';
import './ProductDetail.css'; // Import the updated CSS file

const ProductDetail = () => {
  // Sample product data
  const products = [
    {
      id: 1,
      title: "Product 1",
      price: 49.99,
      description: "This is a great product with amazing features.",
      image: "https://via.placeholder.com/300x200",
    },
    {
      id: 2,
      title: "Product 2",
      price: 59.99,
      description: "An outstanding product for daily use.",
      image: "https://via.placeholder.com/300x200",
    },
    {
      id: 3,
      title: "Product 3",
      price: 89.99,
      description: "High-quality product at an affordable price.",
      image: "https://via.placeholder.com/300x200",
    },
    {
      id: 4,
      title: "Product 4",
      price: 29.99,
      description: "Perfect for those who value simplicity.",
      image: "https://via.placeholder.com/300x200",
    },
  ];

  return (
    <div className="product-page">
      <h1>Our Products</h1>
      <div className="product-grid">
        {products.map((product) => (
          <div key={product.id} className="product-tile">
            <img src={product.image} alt={product.title} />
            <h3>{product.title}</h3>
            <p className="price">${product.price.toFixed(2)}</p>
            <p>{product.description}</p>
            <a href={`/product/${product.id}`} className="view-product">
              View Product
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductDetail;
