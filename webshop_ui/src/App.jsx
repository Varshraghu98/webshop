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
        <footer>
          <ShopFooter></ShopFooter>
        </footer>
        
      </BrowserRouter>
    </div>
  )
}

export default App
