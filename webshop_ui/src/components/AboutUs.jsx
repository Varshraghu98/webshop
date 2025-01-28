import React from "react";
import { Container, Typography, Box } from "@mui/material";


const AboutUs = () => {
  return (
    <Container
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",   // Full height of the viewport
        width: "100vh",     // Full width of the viewport
        padding: 3,        // Padding around the content
        margin: 0,         // Ensure no margin around the container
        backgroundColor: "#f0f0f0",
        //backgroundColor: "transparent", // Remove any background color from container
      }}
    >
      {/* Main Content Box */}
      <Box sx={{ textAlign: "center", zIndex: 1 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{
            fontFamily: "'Roboto', sans-serif", // Attractive font family
            fontWeight: "bold",
            color: "#333", // Dark text color for readability
          }}
        >
          Welcome to LowTech GmbH,
        </Typography>
        <Typography
          variant="body1"
          paragraph
          sx={{
            fontFamily: "'Roboto', sans-serif",
            color: "#333",
            lineHeight: 1.8,
            textAlign: "center",
          }}
        >
          Where tradition meets innovation. As a proud SME with 45 dedicated employees, we
          specialize in crafting high-quality wooden furniture.
        </Typography>
        <Typography
          variant="body1"
          paragraph
          sx={{
            fontFamily: "'Roboto', sans-serif",
            color: "#333",
            lineHeight: 1.8,
            textAlign: "center",
          }}
        >
          For decades, we built our reputation through direct customer connections, but with
          changing times, we are now ready to embrace the digital era. Our online store brings
          our craftsmanship to your fingertips, making it easier than ever to find timeless
          furniture for your home.
        </Typography>
        <Typography
          variant="body1"
          paragraph
          sx={{
            fontFamily: "'Roboto', sans-serif",
            color: "#333",
            lineHeight: 1.8,
            textAlign: "center",
          }}
        >
          At LowTech GmbH, we blend passion, precision, and sustainability to create furniture
          that lasts a lifetime. Explore our collection and experience the art of fine woodworking.
        </Typography>
      </Box>
    </Container>
  );
};


export default AboutUs;
