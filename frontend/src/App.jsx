import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import AdminSetup from './pages/AdminSetup';
import PurchaseOrder from './pages/PurchaseOrder';
import Inventory from './pages/Inventory';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <h1>甜品店管理系统</h1>
        </div>
        <div className="nav-links">
          <Link
            to="/admin-setup"
            className={location.pathname === '/admin-setup' ? 'active' : ''}
          >
            基础设置
          </Link>
          <Link
            to="/purchase-order"
            className={location.pathname === '/purchase-order' ? 'active' : ''}
          >
            采购管理
          </Link>
          <Link
            to="/inventory"
            className={location.pathname === '/inventory' ? 'active' : ''}
          >
            库存管理
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<AdminSetup />} />
            <Route path="/admin-setup" element={<AdminSetup />} />
            <Route path="/purchase-order" element={<PurchaseOrder />} />
            <Route path="/inventory" element={<Inventory />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
