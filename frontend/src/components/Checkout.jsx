import { useState } from 'react';
import { checkout } from '../services/api';

export default function Checkout({ cart, onClose, onCheckoutSuccess }) {
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [dineOption, setDineOption] = useState('dine_in');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await checkout(paymentMethod, dineOption);
      onCheckoutSuccess(response.data);
    } catch (error) {
      alert(error.response?.data?.detail || '结算失败');
    } finally {
      setSubmitting(false);
    }
  };

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
          <h2 className="text-2xl font-bold text-gray-800">💳 确认订单</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {/* 订单摘要 */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">订单摘要</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              {cart && cart.items && cart.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-700">
                    {item.product_name} x{item.quantity}
                  </span>
                  <span className="text-gray-900 font-medium">
                    ¥{(parseFloat(item.product_price) * item.quantity).toFixed(2)}
                  </span>
                </div>
              ))}
              <div className="border-t pt-2 mt-2 flex justify-between font-bold text-lg">
                <span>总计</span>
                <span className="text-primary">¥{cart?.total_price}</span>
              </div>
            </div>
          </div>

          {/* 用餐方式 */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">用餐方式</h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setDineOption('dine_in')}
                className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
                  dineOption === 'dine_in'
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                🍽️ 堂食
              </button>
              <button
                onClick={() => setDineOption('takeaway')}
                className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
                  dineOption === 'takeaway'
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                📦 外带
              </button>
            </div>
          </div>

          {/* 支付方式 */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">支付方式</h3>
            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => setPaymentMethod('cash')}
                className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
                  paymentMethod === 'cash'
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                💵 现金
              </button>
              <button
                onClick={() => setPaymentMethod('card')}
                className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
                  paymentMethod === 'card'
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                💳 刷卡
              </button>
              <button
                onClick={() => setPaymentMethod('wechat')}
                className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
                  paymentMethod === 'wechat'
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                💚 微信
              </button>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              返回购物车
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400"
            >
              {submitting ? '提交中...' : '确认下单'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
