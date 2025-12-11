import { useState, useEffect } from 'react';
import Login from './components/Login';
import MenuList from './components/MenuList';
import Cart from './components/Cart';
import Checkout from './components/Checkout';
import OrderSuccess from './components/OrderSuccess';
import { getCart } from './services/api';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutCart, setCheckoutCart] = useState(null);
  const [orderSuccess, setOrderSuccess] = useState(null);
  const [cartItemCount, setCartItemCount] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      loadCartCount();
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      loadCartCount();
      // 每30秒更新一次购物车数量
      const interval = setInterval(loadCartCount, 30000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn]);

  useEffect(() => {
    console.log('showCart 状态改变:', showCart);
  }, [showCart]);

  const loadCartCount = async () => {
    try {
      const response = await getCart();
      setCartItemCount(response.data.items?.length || 0);
    } catch (error) {
      console.error('加载购物车数量失败:', error);
    }
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    loadCartCount();
  };

  const handleCartClick = () => {
    console.log('购物车按钮被点击，设置 showCart 为 true');
    setShowCart(true);
  };

  const handleCartClose = () => {
    console.log('关闭购物车，设置 showCart 为 false');
    setShowCart(false);
    loadCartCount();
  };

  const handleCheckout = (cart) => {
    setCheckoutCart(cart);
    setShowCart(false);
    setShowCheckout(true);
  };

  const handleCheckoutClose = () => {
    setShowCheckout(false);
    setShowCart(true);
  };

  const handleCheckoutSuccess = (order) => {
    setShowCart(false);
    setShowCheckout(false);
    setOrderSuccess(order);
    setCartItemCount(0);
  };

  const handleOrderSuccessClose = () => {
    setOrderSuccess(null);
  };

  const handleLogout = () => {
    // 清除 token 并重置应用状态
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setShowCart(false);
    setShowCheckout(false);
    setCheckoutCart(null);
    setOrderSuccess(null);
    setCartItemCount(0);
  };

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <>
      <MenuList
        onCartClick={handleCartClick}
        cartItemCount={cartItemCount}
        onLogout={handleLogout}
        onCartUpdate={loadCartCount}
      />
      {showCart && (
        <Cart
          onClose={handleCartClose}
          onCheckout={handleCheckout}
        />
      )}
      {showCheckout && (
        <Checkout
          cart={checkoutCart}
          onClose={handleCheckoutClose}
          onCheckoutSuccess={handleCheckoutSuccess}
        />
      )}
      {orderSuccess && (
        <OrderSuccess
          order={orderSuccess}
          onClose={handleOrderSuccessClose}
        />
      )}
    </>
  );
}

export default App;
