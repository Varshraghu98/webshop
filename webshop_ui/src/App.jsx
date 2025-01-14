import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import NavBar from './components/Navbar/Navbar'
import ShopFooter from './components/Footer/ShopFooter'
import { BrowserRouter, Routes, Route } from "react-router-dom";


function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <BrowserRouter>
        <header>
          <NavBar></NavBar>
        </header>
        {/* About Us Section */}
        <main>
          <section className="about-us">
            <div className="about-us-content">
              <h1>Welcome to LowTech GmbH,</h1>
              <p>
                where tradition meets innovation. As a proud SME with 45
                dedicated employees, we specialize in crafting high-quality
                wooden furnitures. For decades, we built our reputation through direct customer
                connections, but with changing times, we are now ready to embrace
                the digital era. Our online store brings our craftsmanship to
                your fingertips, making it easier than ever to find timeless
                furniture for your home that suits your comfort.
              </p>
              <p>
                At LowTech GmbH, we blend passion, precision, and sustainability
                to create furniture that lasts a lifetime. Explore our collection
                and experience the art of fine woodworking.
              </p>
            </div>
          </section>
        </main>

        <footer>
          <ShopFooter></ShopFooter>
        </footer>
        
      </BrowserRouter>
    </div>
  )
}

export default App
