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

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: '64px 24px' }}>
      {/* Added padding to avoid heading hiding behind navbar */}
      <Typography variant="h4" gutterBottom textAlign="center">
        Our Products
      </Typography>
      <Grid
        container
        spacing={4} // Increased spacing between cards
        justifyContent="space-evenly" // Even spacing across the row
      >
        {products.map((product) => (
          <Grid
            item
            xs={12} // Full-width on very small screens
            sm={6} // 2 cards per row on small screens
            md={4} // 3 cards per row on medium screens
            lg={3} // 4 cards per row on large screens
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
                href={`/product/${product.id}`}
                sx={{ mt: 'auto' }}
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
