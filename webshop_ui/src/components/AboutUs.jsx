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
        width: "100vw",     // Full width of the viewport
        padding: 3,        // Padding around the content
        margin: 0,         // Ensure no margin around the container
        backgroundColor: "#f0f0f0",
      }}
    >
      {/* Main Content Box */}
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", maxWidth: "1200px" }}>
        {/* Text Content */}
        <Box sx={{ flex: 1, textAlign: "center" }}>
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{
              fontFamily: "'Roboto', sans-serif", // Attractive font family
              fontWeight: "bold",
              color: "#333", // Dark text color for readability
              padding: 3,
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
              //textAlign: "left",
            }}
          >
            where tradition meets innovation. As a proud SME with 45 dedicated employees, we
            specialize in crafting high-quality wooden furniture.
          </Typography>
          <Typography
            variant="body1"
            paragraph
            sx={{
              fontFamily: "'Roboto', sans-serif",
              color: "#333",
              lineHeight: 1.8,
              //textAlign: "left",
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
              //textAlign: "left",
            }}
          >
            At LowTech GmbH, we blend passion, precision, and sustainability to create furniture
            that lasts a lifetime. Explore our collection and experience the art of fine woodworking!
          </Typography>
        </Box>


        {/* Image on the Right */}
        <Box
          sx={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <img
            src="/images/AboutUs.jpg"  // Image path in the public folder
            alt="Wooden Furniture"
            style={{
              maxWidth: "60%",  // Ensures the image is responsive
              height: "auto",
              borderRadius: "8px", // Optional: to add rounded corners
            }}
          />
        </Box>
      </Box>
    </Container>
  );
};


export default AboutUs;
