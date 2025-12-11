import { useState, useEffect } from 'react';
import { getCart, updateCartItem, removeFromCart } from '../services/api';

export default function Cart({ onClose, onCheckout }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('Cart 组件已挂载');
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const response = await getCart();
      setCart(response.data);
    } catch (error) {
      console.error('加载购物车失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;

    try {
      await updateCartItem(itemId, newQuantity);
      await loadCart();
    } catch (error) {
      alert('更新失败');
    }
  };

  const handleRemove = async (itemId) => {
    if (!confirm('确认删除此商品？')) return;

    try {
      await removeFromCart(itemId);
      await loadCart();
    } catch (error) {
      alert('删除失败');
    }
  };

  const handleCheckout = () => {
    if (!cart || cart.items.length === 0) {
      alert('购物车为空');
      return;
    }
    onCheckout(cart);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8">加载中...</div>
      </div>
    );
  }

  console.log('Cart 正在渲染，购物车数据:', cart);

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-4"
      style={{
        zIndex: 9999,
        backgroundColor: 'rgba(0, 0, 0, 0.3)',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: '#FFFFFF',
          width: '600px',
          maxWidth: '90vw',
          maxHeight: '80vh',
          display: 'block',
          position: 'relative',
          zIndex: 10000
        }}
      >
        {/* 标题 */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">🛒 购物车</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* 购物车列表 */}
        <div className="p-6">
          {cart && cart.items && cart.items.length > 0 ? (
            <>
              <div className="space-y-4 mb-6">
                {cart.items.map((item) => (
                  <div
                    key={item.id}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-800 text-lg">
                          {item.product_name}
                        </h3>
                        <div className="text-primary font-bold text-lg">
                          ¥{parseFloat(item.product_price).toFixed(2)}
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemove(item.id)}
                        className="text-red-500 hover:text-red-700 ml-2"
                      >
                        🗑️
                      </button>
                    </div>

                    {/* Modifiers */}
                    {item.modifiers && item.modifiers.length > 0 && (
                      <div className="bg-gray-50 rounded p-2 mb-3">
                        <div className="text-sm text-gray-600">配料：</div>
                        {item.modifiers.map((mod, index) => (
                          <div
                            key={index}
                            className="text-sm text-gray-700 flex justify-between"
                          >
                            <span>{mod.name}</span>
                            <span>+¥{parseFloat(mod.price).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* 数量和小计 */}
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() =>
                            handleQuantityChange(item.id, item.quantity - 1)
                          }
                          className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center font-bold"
                        >
                          -
                        </button>
                        <span className="font-semibold w-8 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() =>
                            handleQuantityChange(item.id, item.quantity + 1)
                          }
                          className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center font-bold"
                        >
                          +
                        </button>
                      </div>
                      <div className="text-lg font-bold text-gray-800">
                        小计: ¥{parseFloat(item.item_subtotal).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 总价 */}
              <div className="border-t pt-4 mb-6">
                <div className="flex justify-between items-center text-2xl font-bold">
                  <span>总计:</span>
                  <span className="text-primary">
                    ¥{parseFloat(cart.total_price).toFixed(2)}
                  </span>
                </div>
              </div>

              {/* 结算按钮 */}
              <div className="flex gap-3">
                <button
                  onClick={onClose}
                  className="flex-1 bg-gray-200 text-gray-800 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  继续购物
                </button>
                <button
                  onClick={handleCheckout}
                  className="flex-1 bg-secondary text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-colors"
                >
                  结算
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛒</div>
              <div className="text-gray-500 text-lg">购物车是空的</div>
              <button
                onClick={onClose}
                className="mt-6 bg-primary text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
              >
                去购物
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
