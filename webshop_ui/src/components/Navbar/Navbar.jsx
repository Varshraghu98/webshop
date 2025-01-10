import React, { useState } from "react";
import { Link } from "react-router-dom";
import Hamburger from "hamburger-react";
import "./NavBar.css";
import { FaSearch } from "react-icons/fa"; 

const NavBar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="navbar">
      <div className="navbar-content">
        {/* Logo */}
        <div className="navbar-logo">
          <Link to="/" className="logo">
            🪑 LowTech GmbH
          </Link>
        </div>

         {/* Search Bar */}
         <div className="navbar-search">
          <div className="search-container">
            <FaSearch className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search for furniture..."
            />
          </div>
        </div>

        {/* Hamburger Menu */}
        <div className="hamburger-menu">
          <Hamburger toggled={isOpen} toggle={setIsOpen} />
        </div>

        {/* Navigation Links */}
        <nav className={`nav-links ${isOpen ? "show" : ""}`}>
          <Link to="/shop" className="nav-item" onClick={() => setIsOpen(false)}>
            Shop
          </Link>
          <Link
            to="/categories"
            className="nav-item"
            onClick={() => setIsOpen(false)}
          >
            Categories
          </Link>
          <Link
            to="/about"
            className="nav-item"
            onClick={() => setIsOpen(false)}
          >
            About Us
          </Link>
          <Link
            to="/contact"
            className="nav-item"
            onClick={() => setIsOpen(false)}
          >
            Contact
          </Link>
          <Link
            to="/cart"
            className="nav-item"
            onClick={() => setIsOpen(false)}
          >
            Cart 🛒
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default NavBar;
