import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, CardMedia, Typography, Button, Box, CircularProgress } from '@mui/material';
import { toast } from 'react-toastify';

const ProductDetail = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(import.meta.env.VITE_APP_API_GET_PRODUCTS_URL);
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setProducts(data);
      } catch (err) {
        toast.error(`Failed to fetch products: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Function to handle adding a product to the cart
  const handleAddToCart = async (productId) => {
    try {
      const response = await fetch(import.meta.env.VITE_APP_API_POST_CART_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: 1,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      toast.success(`Product added to cart: ${data.message}`);
    } catch (err) {
      toast.error(`Failed to add product to cart: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: '64px 24px' }}>
      <Typography variant="h4" gutterBottom textAlign="center">
        Our Products
      </Typography>
      <Grid
        container
        spacing={4}
        justifyContent="space-evenly"
      >
        {products.map((product) => (
          <Grid
            item
            xs={12}
            sm={6}
            md={4}
            lg={3}
            key={product.id}
          >
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: 3,
                transition: 'transform 0.3s',
                '&:hover': { transform: 'scale(1.05)' },
              }}
            >
              <CardMedia
                component="img"
                height="200"
                image={product.image}
                alt={product.name}
                sx={{ objectFit: 'cover' }}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h6" component="div">
                  {product.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {product.description}
                </Typography>
                <Typography variant="subtitle1" sx={{ mt: 1, fontWeight: 'bold', color: 'primary.main' }}>
                  €{product.price.toFixed(2)}
                </Typography>
              </CardContent>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                sx={{ mt: 'auto' }}
                onClick={() => handleAddToCart(product.id)} // Call the function when button is clicked
              >
                Add to Cart
              </Button>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ProductDetail;
