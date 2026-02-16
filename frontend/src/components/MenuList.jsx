import { useState, useEffect } from 'react';
import { getCategories, getMenu } from '../services/api';
import ProductDetail from './ProductDetail';

export default function MenuList({ onCartClick, cartItemCount, onLogout }) {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [categoriesRes, productsRes] = await Promise.all([
        getCategories(),
        getMenu()
      ]);
      setCategories(categoriesRes.data);
      setProducts(productsRes.data);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProductsByCategory = async (categoryId) => {
    setLoading(true);
    try {
      const response = await getMenu({ categoryId });
      setProducts(response.data);
      setSelectedCategory(categoryId);
    } catch (error) {
      console.error('加载分类商品失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (categoryId) => {
    if (selectedCategory === categoryId) {
      setSelectedCategory(null);
      loadData();
    } else {
      loadProductsByCategory(categoryId);
    }
  };

  if (loading && products.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🍰 DessertPOS</h1>
          <div className="flex items-center gap-3">
            <button
              onClick={onCartClick}
              className="relative bg-primary text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
            >
              🛒 购物车
              {cartItemCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </button>
            <button
              onClick={onLogout}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>

      {/* 分类标签 */}
      <div className="bg-white border-b sticky top-16 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex gap-2 overflow-x-auto">
          <button
            onClick={() => {
              setSelectedCategory(null);
              loadData();
            }}
            className={`px-4 py-2 rounded-full whitespace-nowrap transition-colors ${
              selectedCategory === null
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            全部
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategoryClick(category.id)}
              className={`px-4 py-2 rounded-full whitespace-nowrap transition-colors ${
                selectedCategory === category.id
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>

      {/* 商品列表 */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div
              key={product.id}
              onClick={() => setSelectedProduct(product)}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
            >
              <div className="h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                <span className="text-6xl">🧁</span>
              </div>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  {product.name}
                </h3>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-primary">
                    ¥{parseFloat(product.price).toFixed(2)}
                  </span>
                  <button className="bg-primary text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600 transition-colors">
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {products.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            暂无商品
          </div>
        )}
      </div>

      {/* 商品详情弹窗 */}
      {selectedProduct && (
        <ProductDetail
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onAddSuccess={() => setSelectedProduct(null)}
        />
      )}
    </div>
  );
}
