import React, { useState, useEffect } from "react";
import {
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  CircularProgress,
  TextField,
  Slider,
  MenuItem,
  Select,
  Checkbox,
  ListItemText,
  FormControl,
  InputLabel,
  Paper,
} from "@mui/material";
import { toast } from "react-toastify";

const ProductDetail = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [priceRange, setPriceRange] = useState([0, 100]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(import.meta.env.VITE_APP_API_GET_PRODUCTS_URL);
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setProducts(data);
        setFilteredProducts(data);

        const uniqueCategories = [...new Set(data.map((product) => product.category))];
        setCategories(uniqueCategories);

        const prices = data.map((product) => product.price);
        setPriceRange([Math.min(...prices), Math.max(...prices)]);
      } catch (err) {
        toast.error(`Failed to fetch products: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const handleAddToCart = async (productId) => {
    try {
      const response = await fetch(import.meta.env.VITE_APP_API_POST_CART_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
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

  const handleSearch = (event) => setSearchTerm(event.target.value);

  const handleCategoryChange = (event) => setSelectedCategories(event.target.value);

  const handlePriceRangeChange = (event, newValue) => setPriceRange(newValue);

  useEffect(() => {
    const filtered = products.filter((product) => {
      const matchesSearchTerm = product.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory =
        selectedCategories.length === 0 || selectedCategories.includes(product.category);
      const matchesPrice = product.price >= priceRange[0] && product.price <= priceRange[1];

      return matchesSearchTerm && matchesCategory && matchesPrice;
    });

    setFilteredProducts(filtered);
  }, [products, searchTerm, selectedCategories, priceRange]);

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: "32px" }}>
      <Typography variant="h4" textAlign="center" gutterBottom>
        Explore Our Products
      </Typography>

      {/* Filters and Search */}
      <Paper sx={{ padding: "16px", marginBottom: "32px" }}>
        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            gap: "16px",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Search Field */}
          <TextField
            label="Search Products"
            variant="outlined"
            value={searchTerm}
            onChange={handleSearch}
            sx={{ width: "300px" }}
          />

          {/* Category Dropdown Filter */}
          <FormControl sx={{ width: "300px" }}>
            <InputLabel>Filter by Category</InputLabel>
            <Select
              multiple
              value={selectedCategories}
              onChange={handleCategoryChange}
              renderValue={(selected) => selected.join(", ")}
            >
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  <Checkbox checked={selectedCategories.includes(category)} />
                  <ListItemText primary={category} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Price Range Slider */}
          <Box sx={{ width: "300px" }}>
            <Typography variant="subtitle1" gutterBottom>
              Filter by Price
            </Typography>
            <Slider
              value={priceRange}
              onChange={handlePriceRangeChange}
              valueLabelDisplay="auto"
              min={Math.min(...products.map((product) => product.price))}
              max={Math.max(...products.map((product) => product.price))}
            />
            <Typography>
              Price Range: €{priceRange[0].toFixed(2)} - €{priceRange[1].toFixed(2)}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Product Grid */}
      <Grid container spacing={4}>
        {filteredProducts.length > 0 ? (
          filteredProducts.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <Card
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  height: "100%",
                  boxShadow: 3,
                  "&:hover": { boxShadow: 6 },
                }}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={`data:image/jpeg;base64,${product.image}`}
                  alt={product.name}
                  sx={{ objectFit: "cover" }}
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {product.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {product.description}
                  </Typography>
                  <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                    €{product.price.toFixed(2)}
                  </Typography>
                </CardContent>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleAddToCart(product.id)}
                >
                  Add to Cart
                </Button>
              </Card>
            </Grid>
          ))
        ) : (
          <Typography variant="h6" sx={{ textAlign: "center", width: "100%", mt: 4 }}>
            No products found
          </Typography>
        )}
      </Grid>
    </Box>
  );
};

export default ProductDetail;
