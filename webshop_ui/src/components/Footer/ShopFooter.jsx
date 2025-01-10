import React from "react";
import "./ShopFooter.css";

const ShopFooter = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Logo Section */}
        <div className="footer-logo">
          <span role="img" aria-label="logo">
            🪑
          </span>
          LowTech GmbH
        </div>

        {/* Contact Details */}
        <div className="footer-contact">
          <p>Contact Us:</p>
          <p>Email: <a href="mailto:support@lowtechgmbh.com">support@furnitureshop.com</a></p>
          <p>Phone: +49  123-4567</p>
        </div>
      </div>
    </footer>
  );
};

export default ShopFooter;
