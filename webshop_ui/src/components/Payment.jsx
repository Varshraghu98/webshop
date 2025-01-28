import React, { useEffect } from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import { Button } from "@mui/material";
import axios from "axios";

const MySwal = withReactContent(Swal);

const CheckoutForm = () => {
  useEffect(() => {
    // Load PayPal SDK (sandbox environment)
    const script = document.createElement("script");
    script.src =
      "https://www.paypal.com/sdk/js?client-id=AVCPlT1ELF9LLibRxZLcCHgpcoPLpV23mp7GJj07racxpnxQRZAWzJJesOOm-W3UseEXbpYJiq1lkn91&currency=EUR"; // Replace 'your-client-id' with your sandbox client ID
    script.addEventListener("load", () => {
      console.log("PayPal SDK loaded");
    });
    document.body.appendChild(script);
  }, []);

  const handleCheckout = () => {
    MySwal.fire({
      title: "Checkout Form",
      html: `
        <div style="text-align: left;">
          <label for="name">Name:</label>
          <input type="text" id="name" class="swal2-input" placeholder="Enter your name"><br/>
          <label for="email">Email:</label>
          <input type="email" id="email" class="swal2-input" placeholder="Enter your email"><br/>
          <label for="street">Street:</label>
          <input type="text" id="street" class="swal2-input" placeholder="Enter your street address"><br/>
          <label for="city">City:</label>
          <input type="text" id="city" class="swal2-input" placeholder="Enter your city"><br/>
          <label for="pincode">Pincode:</label>
          <input type="text" id="pincode" class="swal2-input" placeholder="Enter your pincode"><br/>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: "Proceed",
      cancelButtonText: "Cancel",
      preConfirm: () => {
        const name = Swal.getPopup().querySelector("#name").value;
        const email = Swal.getPopup().querySelector("#email").value;
        const street = Swal.getPopup().querySelector("#street").value;
        const city = Swal.getPopup().querySelector("#city").value;
        const pincode = Swal.getPopup().querySelector("#pincode").value;

        if (!name || !email || !street || !city || !pincode) {
          Swal.showValidationMessage(`Please fill out all fields`);
        }

        return {
          name,
          email,
          street,
          city,
          pincode,
        };
      },
    }).then((result) => {
      if (result.isConfirmed) {
        const checkoutData = result.value;

        // Fetch cart details from the API
        axios.get("http://127.0.0.1:5000/cart").then((response) => {
          const cartItems = response.data;

          // Display the summary
          const productDetails = cartItems
            .map(
              (item) =>
                `<li>${item.name} (x${item.quantity}) - €${item.price.toFixed(2)}</li>`
            )
            .join("");

          const totalPrice = cartItems.reduce(
            (sum, item) => sum + item.price * item.quantity,
            0
          );

          MySwal.fire({
            title: "Order Summary",
            html: `
              <h4>Checkout Details:</h4>
              <p><strong>Name:</strong> ${checkoutData.name}</p>
              <p><strong>Email:</strong> ${checkoutData.email}</p>
              <p><strong>Street:</strong> ${checkoutData.street}</p>
              <p><strong>City:</strong> ${checkoutData.city}</p>
              <p><strong>Pincode:</strong> ${checkoutData.pincode}</p>
              <h4>Product Summary:</h4>
              <ul>${productDetails}</ul>
              <h4>Total Price: €${totalPrice.toFixed(2)}</h4>
            `,
            confirmButtonText: "Proceed to Payment",
          }).then(() => {
            // Display Payment button
            MySwal.fire({
              title: "Choose Payment Method",
              html: `<div id="paypal-btn-container"></div>`,
              didRender: () => {
                // Load the PayPal button when rendered
                window.paypal.Buttons({
                  createOrder: (data, actions) => {
                    return actions.order.create({
                      purchase_units: [
                        {
                          amount: {
                            value: totalPrice.toFixed(2),
                          },
                        },
                      ],
                    });
                  },
                  onApprove: (data, actions) => {
                    return actions.order.capture().then((details) => {
                      MySwal.fire({
                        title: "Payment Successful",
                        text: `Payment completed successfully with PayPal!`,
                        icon: "success",
                      }).then(() => {
                        placeOrder(checkoutData, cartItems, "PayPal", totalPrice);
                      });
                    });
                  },
                  onError: (err) => {
                    MySwal.fire({
                      title: "Payment Failed",
                      text: "Something went wrong with your PayPal payment. Please try again.",
                      icon: "error",
                    });
                  },
                }).render("#paypal-btn-container");
              },
            });
          });
        });
      }
    });
  };

  const placeOrder = (checkoutData, cartItems, paymentMethod, totalPrice) => {
    // Construct the payload with checkout details and cart items
    const orderData = {
      name: checkoutData.name,
      email: checkoutData.email,
      street: checkoutData.street,
      city: checkoutData.city,
      pincode: checkoutData.pincode,
      paymentSuccessful: true,
      paymentMethod: paymentMethod, // Use the dynamic payment method variable
      totalPrice: totalPrice, // Use the dynamic total price variable
      products: cartItems.map((item) => ({
        id: item.id,
        name: item.name,
        quantity: item.quantity,
        price: item.price,
      })),
    };
    

    // Make the API call to create the order
    axios
      .post("http://127.0.0.1:5000/createorder", orderData)
      .then((response) => {
        console.log("Order API Response:", response.data);
        // Clear the cart after placing the order
        return axios.delete("http://127.0.0.1:5000/cart");
      })
      .then(() => {
        // Success: Show success message and refresh page
        MySwal.fire(
          "Success",
          "Order placed successfully. An email is sent to your registered email id!",
          "success"
        ).then(() => {
          window.location.reload();
        });
      })
      .catch((error) => {
        console.error("Error Placing Order:", error);
        MySwal.fire("Error", "Failed to place order. Please try again.", "error");
      });
  };

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={handleCheckout}
      sx={{ mt: 2 }}
    >
      Buy
    </Button>
  );
};

export default CheckoutForm;
