import React, { useEffect, useState } from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import { Button } from "@mui/material";
import axios from "axios";

const MySwal = withReactContent(Swal);

const CheckoutForm = () => {
  const [isCartLoaded, setIsCartLoaded] = useState(false);

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
    // Fetch cart details to check if it's empty
    axios
      .get("http://127.0.0.1:5000/cart")
      .then((response) => {
        const cartItems = response.data;

        if (cartItems.length === 0) {
          // If the cart is empty, show a message and stop the process
          MySwal.fire({
            title: "Cart is Empty",
            text: "Your cart is empty. Please add items to proceed.",
            icon: "warning",
            confirmButtonText: "OK",
          });
        } else {
          // Proceed with the checkout process
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
              const name = Swal.getPopup().querySelector("#name").value.trim();
              const email = Swal.getPopup().querySelector("#email").value.trim();
              const street = Swal.getPopup().querySelector("#street").value.trim();
              const city = Swal.getPopup().querySelector("#city").value.trim();
              const pincode = Swal.getPopup().querySelector("#pincode").value.trim();

              // Perform validations
              if (!name || !email || !street || !city || !pincode) {
                Swal.showValidationMessage(`All fields are required.`);
                return false;
              }

              if (!email.includes("@")) {
                Swal.showValidationMessage(`Please enter a valid email address.`);
                return false;
              }

              if (!/^[0-9]{5}$/.test(pincode)) {
                Swal.showValidationMessage(`Pincode must be a 5-digit number.`);
                return false;
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
                showCancelButton: true,
                confirmButtonText: "Proceed to Payment",
                cancelButtonText: "Cancel",
              }).then((summaryResult) => {
                if (summaryResult.isConfirmed) {
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
                              placeOrder(
                                checkoutData,
                                cartItems,
                                "PayPal",
                                totalPrice
                              );
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
                } else if (summaryResult.isDismissed) {
                  MySwal.fire(
                    "Cancelled",
                    "Your checkout process has been cancelled.",
                    "info"
                  );
                }
              });
            }
          });
        }
      })
      .catch((error) => {
        console.error("Error fetching cart data:", error);
      });
  };

  const placeOrder = (checkoutData, cartItems, paymentMethod, totalPrice) => {
    const orderData = {
      name: checkoutData.name,
      email: checkoutData.email,
      street: checkoutData.street,
      city: checkoutData.city,
      pincode: checkoutData.pincode,
      paymentSuccessful: true,
      paymentMethod: paymentMethod,
      totalPrice: totalPrice,
      products: cartItems.map((item) => ({
        id: item.id,
        name: item.name,
        quantity: item.quantity,
        price: item.price,
      })),
    };

    axios
      .post("http://127.0.0.1:5000/createorder", orderData)
      .then((response) => {
        return axios.delete("http://127.0.0.1:5000/cart");
      })
      .then(() => {
        MySwal.fire(
          "Success",
          "Order placed successfully. An email is sent to your registered email id!",
          "success"
        ).then(() => {
          window.location.reload();
        });
      })
      .catch((error) => {
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
