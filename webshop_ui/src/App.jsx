import { useState } from 'react';
import NavBar from './components/Navbar/Navbar';
import ShopFooter from './components/Footer/ShopFooter';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import ProductDetail from './components/Product/ProductDetail';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <Router>
        <header>
          <NavBar />
        </header>
        <Routes>
            <Route path="/" element={<ProductDetail />} /> {/* Landing Page */}
            <Route path="/shop" element={<ProductDetail />} /> {/* Shop Route */}
        </Routes>
        
        
        {/*<footer>
          <ShopFooter />
        </footer>*/}
      </Router>
    </div>
  );
}

export default App;
