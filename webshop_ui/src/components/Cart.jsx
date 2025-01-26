import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  Card,
  CardContent,
  Typography,
  CardMedia,
  Grid,
  Button,
} from "@mui/material";
import CheckoutForm from "./CheckoutForm"; // Import the separate CheckoutForm component

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/cart");
        setCartItems(response.data);
        setLoading(false);
      } catch (err) {
        setError("Failed to load cart data");
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  const removeItem = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/cart/${id}`);
      setCartItems(cartItems.filter((item) => item.id !== id));
    } catch (err) {
      setError("Failed to remove item");
    }
  };

  const updateQuantity = async (id, newQuantity) => {
    try {
      await axios.put(`http://127.0.0.1:5000/cart/${id}`, {
        quantity: newQuantity,
      });
      setCartItems((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, quantity: newQuantity } : item
        )
      );
    } catch (err) {
      setError("Failed to update quantity");
    }
  };

  const totalPrice = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  if (loading) {
    return <Typography>Loading cart...</Typography>;
  }

  if (error) {
    return <Typography>Error: {error}</Typography>;
  }

  return (
    <Box sx={{ padding: 2, marginTop: 8, color: "black" }}>
      <Typography variant="h4" gutterBottom>
        Your Cart
      </Typography>
      <Grid container spacing={3}>
        {cartItems.map((item) => (
          <Grid item 
          xs={12} // Full-width for single row
          sm={cartItems.length === 1 ? 12 : 6} // Adjust width for one or more items
          md={cartItems.length === 1 ? 12 : 6} // Adjust width for one or more items
          key={item.id}
          >
            <Card>
              <CardMedia
                component="img"
                height="200"
                image={`data:image/jpeg;base64,${item.image}`}
                alt={item.name}
              />
              <CardContent>
                <Typography variant="h6">{item.name}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {item.description}
                </Typography>
                <Typography variant="body1">Price: €{item.price}</Typography>
                <Typography variant="body1">Quantity: {item.quantity}</Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 2 }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() =>
                      updateQuantity(item.id, Math.max(1, item.quantity - 1))
                    }
                    disabled={item.quantity === 1}
                  >
                    -
                  </Button>
                  <Typography>{item.quantity}</Typography>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  >
                    +
                  </Button>
                </Box>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => removeItem(item.id)}
                  sx={{ mt: 2 }}
                >
                  Remove
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Box sx={{ marginTop: 4 }}>
        <Typography variant="h5">Total Price: €{totalPrice.toFixed(2)}</Typography>
        {/* Use the CheckoutForm component */}
        <CheckoutForm />
      </Box>
    </Box>
  );
};

export default Cart;
