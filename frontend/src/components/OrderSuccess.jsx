export default function OrderSuccess({ order, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 text-center">
        {/* 成功图标 */}
        <div className="mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-5xl">✓</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            订单创建成功！
          </h2>
          <p className="text-gray-600">
            您的订单已提交，请耐心等待
          </p>
        </div>

        {/* 订单信息 */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">订单号:</span>
            <span className="font-semibold">{order.order_number}</span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">订单状态:</span>
            <span className="font-semibold text-primary">
              {order.order_status === 'IP' ? '处理中' : order.order_status}
            </span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600">商品数量:</span>
            <span className="font-semibold">{order.items.length} 件</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">总金额:</span>
            <span className="text-2xl font-bold text-primary">
              ¥{parseFloat(order.total_price).toFixed(2)}
            </span>
          </div>
        </div>

        {/* 商品列表 */}
        <div className="mb-6 text-left">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">订单详情:</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between text-sm">
                <span className="text-gray-700">
                  {item.product_name} × {item.quantity}
                </span>
                <span className="text-gray-600">
                  ¥{parseFloat(item.price).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 按钮 */}
        <button
          onClick={onClose}
          className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
        >
          完成
        </button>
      </div>
    </div>
  );
}
