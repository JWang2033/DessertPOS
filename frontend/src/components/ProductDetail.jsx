import { useState, useEffect } from 'react';
import { getProductDetail, addToCart } from '../services/api';

export default function ProductDetail({ product, onClose, onAddSuccess }) {
  const [productDetail, setProductDetail] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedModifiers, setSelectedModifiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadProductDetail();
  }, [product.id]);

  const loadProductDetail = async () => {
    try {
      const response = await getProductDetail(product.id);
      setProductDetail(response.data);
    } catch (error) {
      console.error('加载商品详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = (delta) => {
    const newQuantity = quantity + delta;
    if (newQuantity >= 1) {
      setQuantity(newQuantity);
    }
  };

  const toggleModifier = (modifierId) => {
    setSelectedModifiers((prev) =>
      prev.includes(modifierId)
        ? prev.filter((id) => id !== modifierId)
        : [...prev, modifierId]
    );
  };

  const calculateTotal = () => {
    if (!productDetail) return 0;

    let total = parseFloat(productDetail.price);

    if (productDetail.modifiers && selectedModifiers.length > 0) {
      const modifierTotal = productDetail.modifiers
        .filter((mod) => selectedModifiers.includes(mod.id))
        .reduce((sum, mod) => sum + parseFloat(mod.price), 0);
      total += modifierTotal;
    }

    return (total * quantity).toFixed(2);
  };

  const handleAddToCart = async () => {
    setAdding(true);
    try {
      await addToCart(product.id, quantity, selectedModifiers);
      alert('已添加到购物车！');
      if (onAddSuccess) {
        onAddSuccess(); // 更新购物车数量
      }
      onClose(); // 关闭商品详情弹窗
    } catch (error) {
      alert(error.response?.data?.detail || '添加失败');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {loading ? (
          <div className="p-8 text-center">加载中...</div>
        ) : productDetail ? (
          <>
            {/* 商品图片 */}
            <div className="h-64 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
              <span className="text-9xl">🧁</span>
            </div>

            {/* 商品信息 */}
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                {productDetail.name}
              </h2>
              <div className="text-3xl font-bold text-primary mb-6">
                ¥{parseFloat(productDetail.price).toFixed(2)}
              </div>

              {/* Modifiers */}
              {productDetail.modifiers && productDetail.modifiers.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">
                    可选配料
                  </h3>
                  <div className="space-y-2">
                    {productDetail.modifiers.map((modifier) => (
                      <button
                        key={modifier.id}
                        onClick={() => toggleModifier(modifier.id)}
                        className={`w-full flex justify-between items-center p-3 rounded-lg border-2 transition-colors ${
                          selectedModifiers.includes(modifier.id)
                            ? 'border-primary bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <span className="font-medium">{modifier.name}</span>
                        <span className="text-gray-600">
                          +¥{parseFloat(modifier.price).toFixed(2)}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* 数量选择 */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  数量
                </h3>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => handleQuantityChange(-1)}
                    className="w-10 h-10 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xl font-bold"
                  >
                    -
                  </button>
                  <span className="text-2xl font-semibold w-12 text-center">
                    {quantity}
                  </span>
                  <button
                    onClick={() => handleQuantityChange(1)}
                    className="w-10 h-10 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xl font-bold"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* 底部按钮 */}
              <div className="flex gap-3">
                <button
                  onClick={onClose}
                  className="flex-1 bg-gray-200 text-gray-800 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleAddToCart}
                  disabled={adding}
                  className="flex-1 bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400"
                >
                  {adding ? '添加中...' : `加入购物车 ¥${calculateTotal()}`}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="p-8 text-center text-red-600">加载失败</div>
        )}
      </div>
    </div>
  );
}
