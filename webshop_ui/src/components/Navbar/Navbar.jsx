import React, { useState } from "react";
import { Link } from "react-router-dom";
import Hamburger from "hamburger-react";
import "./NavBar.css";
import { FaSearch } from "react-icons/fa"; 

const NavBar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  // Sample category list
  const categories = [
    "Chairs",
    "Tables",
    "Sofas",
    "Beds",
    "Wardrobes",
    "Bookshelves",
    "Outdoor Furniture",
    "Dining Sets",
    "Office Furniture",
    "Kids' Furniture",
  ];

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
          <div
            className="nav-item dropdown"
            onMouseEnter={() => setShowDropdown(true)}
            onMouseLeave={() => setShowDropdown(false)}
          >
            <span className="dropdown-label">Categories</span>
            {showDropdown && (
              <ul className="dropdown-menu">
                {categories.map((category, index) => (
                  <li key={index} className="dropdown-item">
                    <Link
                      to={`/categories/${category.toLowerCase().replace(/ /g, "-")}`}
                      className="nav-item"
                      onClick={() => setIsOpen(false)}
                    >
                      {category}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
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
