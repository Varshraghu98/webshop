import React from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import { Button } from "@mui/material";
import axios from "axios";

const MySwal = withReactContent(Swal);

const CheckoutForm = () => {
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
            // Display payment options
            MySwal.fire({
              title: "Payment Gateway", 
              html: `
                <div>
                  <button id="paypal-btn" style="background-color: #0070ba; color: white; border: none; padding: 10px 20px; margin: 5px; cursor: pointer;"> Pay with PayPal</button>
                  <button id="card-btn" style="background-color: #333; color: white; border: none; padding: 10px 20px; margin: 5px; cursor: pointer;"> Pay with Card</button>
                </div>
              `,
              didRender: () => {
                // PayPal Payment
                document
                  .getElementById("paypal-btn")
                  .addEventListener("click", () => {
                    MySwal.fire("Success", "Payment processed via PayPal!", "success")
                      .then(() => {
                        placeOrder(checkoutData, cartItems, "PayPal", totalPrice);
                      });
                  });

                // Card Payment
                document.getElementById("card-btn").addEventListener("click", () => {
                  MySwal.fire({
                    title: "Enter Card Details",
                    html: `
                      <label for="card-number">Card Number:</label>
                      <input type="text" id="card-number" class="swal2-input" placeholder="1234 5678 9012 3456"><br/>
                      <label for="expiry">Expiry Date:</label>
                      <input type="text" id="expiry" class="swal2-input" placeholder="MM/YY"><br/>
                      <label for="cvv">CVV:</label>
                      <input type="text" id="cvv" class="swal2-input" placeholder="123">
                    `,
                    showCancelButton: true,
                    confirmButtonText: "Submit",
                    cancelButtonText: "Cancel",
                    preConfirm: () => {
                      const cardNumber = Swal.getPopup().querySelector("#card-number").value;
                      const expiry = Swal.getPopup().querySelector("#expiry").value;
                      const cvv = Swal.getPopup().querySelector("#cvv").value;

                      if (!cardNumber || !expiry || !cvv) {
                        Swal.showValidationMessage("Please fill out all fields");
                      }

                      return {
                        cardNumber,
                        expiry,
                        cvv,
                      };
                    },
                  }).then((cardResult) => {
                    if (cardResult.isConfirmed) {
                      // Mock successful card payment
                      axios
                        .post("http://127.0.0.1:5000/mock-payment", cardResult.value)
                        .then(() => {
                          MySwal.fire(
                            "Success",
                            "Payment processed successfully via Card!",
                            "success"
                          ).then(() => {
                            placeOrder(checkoutData, cartItems, "Card", totalPrice);
                          });
                        })
                        .catch(() => {
                          MySwal.fire("Error", "Payment failed!", "error");
                        });
                    }
                  });
                });
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
      status: "Order Placed",
      payment_method: paymentMethod,
      total_price: totalPrice,
      customer_details: {
        name: checkoutData.name,
        email: checkoutData.email,
        street: checkoutData.street,
        city: checkoutData.city,
        pincode: checkoutData.pincode
      },
      products: cartItems.reduce((acc, item) => {
        acc[item.id] = item.quantity;
        return acc;
      }, {}),
    };
  
    // Log the payload to verify
    console.log("Placing Order with Data:", orderData);
  
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
          "Order placed successfully \n An Email is sent to your registered email id!",
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
