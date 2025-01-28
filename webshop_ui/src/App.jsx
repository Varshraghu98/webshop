import { useState } from 'react';
import NavBar from './components/Navbar/Navbar';
import ShopFooter from './components/Footer/ShopFooter';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import ProductDetail from './components/ProductDetail';
import Cart from './components/Cart';
import AboutUs from "./components/AboutUs";
import './App.css';

function App() {
  return (
    <div >
      <Router>
        <header>
          <NavBar />
        </header>
        <Routes>
            <Route path="/" element={<ProductDetail />} /> {/* Landing Page */}
            <Route path="/shop" element={<ProductDetail />} /> {/* Shop Route */}
            <Route path="/cart" element={<Cart />} /> 
            <Route path="/about" element={<AboutUs />} /> {/* About Us Page */}
        </Routes>
        
        
        {/*<footer>
          <ShopFooter />
        </footer>*/}
      </Router>
    </div>
  );
}

export default App;
