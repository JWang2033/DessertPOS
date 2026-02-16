import { useState, useEffect } from 'react';
import {
  getPurchaseOrders,
  createPurchaseOrder,
  getPurchaseOrderById,
  getIngredients,
  getUnits,
  getCategories,
  checkUnitCompatibility,
} from '../services/api';
import './PurchaseOrder.css';

function PurchaseOrder() {
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [units, setUnits] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  // 采购单表单
  const [orderForm, setOrderForm] = useState({
    store_id: 1, // 默认门店
    items: [{ ingredient_name: '', unit_name: '', quantity: '', total_amount: '', vendor: '' }],
  });

  useEffect(() => {
    loadPurchaseOrders();
    loadIngredients();
    loadUnits();
    loadCategories();
  }, []);

  const loadPurchaseOrders = async () => {
    try {
      setLoading(true);
      const response = await getPurchaseOrders();
      setPurchaseOrders(response.data);
    } catch (error) {
      alert('加载采购单失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const loadIngredients = async () => {
    try {
      const response = await getIngredients();
      setIngredients(response.data);
    } catch (error) {
      console.error('加载原料失败:', error);
    }
  };

  const loadUnits = async () => {
    try {
      const response = await getUnits();
      setUnits(response.data);
    } catch (error) {
      console.error('加载单位失败:', error);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('加载分类失败:', error);
    }
  };

  const getUnitsForIngredient = (ingredientName) => {
    if (!ingredientName) return [];
    const ingredient = ingredients.find(ing => ing.name === ingredientName);
    if (!ingredient) return [];
    const category = categories.find(cat => cat.name === ingredient.category_name);
    if (!category || !category.units) return [];
    return category.units;
  };

  const handleAddItem = () => {
    setOrderForm({
      ...orderForm,
      items: [...orderForm.items, { ingredient_name: '', unit_name: '', quantity: '', total_amount: '', vendor: '' }],
    });
  };

  const handleRemoveItem = (index) => {
    const newItems = orderForm.items.filter((_, i) => i !== index);
    setOrderForm({ ...orderForm, items: newItems });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...orderForm.items];
    newItems[index][field] = value;
    // Clear unit when ingredient changes
    if (field === 'ingredient_name') {
      newItems[index]['unit_name'] = '';
    }
    setOrderForm({ ...orderForm, items: newItems });
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();

    // 验证表单
    if (orderForm.items.length === 0) {
      alert('请至少添加一个采购项');
      return;
    }

    for (let item of orderForm.items) {
      if (!item.ingredient_name || !item.unit_name || !item.quantity || !item.total_amount) {
        alert('请填写完整的采购项信息');
        return;
      }
    }

    // Check unit compatibility for all items
    const warnings = [];
    for (let item of orderForm.items) {
      try {
        const response = await checkUnitCompatibility(item.ingredient_name, item.unit_name);
        if (!response.data.compatible) {
          warnings.push(`${item.ingredient_name}选择的单位无法转换 (${response.data.purchase_unit} → ${response.data.ingredient_unit})`);
        }
      } catch (error) {
        console.error('Unit compatibility check failed:', error);
      }
    }

    // Show warnings if any
    if (warnings.length > 0) {
      const message = '错误：以下采购项的单位无法转换到库存单位：\n\n' + warnings.join('\n') + '\n\n无法创建采购单，请修改单位后重试。';
      alert(message);
      return;
    }

    try {
      // 转换数据类型
      const data = {
        order_date: new Date().toISOString().split('T')[0], // YYYY-MM-DD
        store_id: orderForm.store_id.toString(),
        items: orderForm.items.map(item => ({
          ingredient_name: item.ingredient_name,
          unit_name: item.unit_name,
          quantity: parseFloat(item.quantity),
          total_amount: parseFloat(item.total_amount),
          vendor: item.vendor || null,
        })),
      };

      await createPurchaseOrder(data);
      alert('采购单创建成功');
      setShowCreateForm(false);
      setOrderForm({
        store_id: 1,
        items: [{ ingredient_name: '', unit_name: '', quantity: '', total_amount: '', vendor: '' }],
      });
      loadPurchaseOrders();
    } catch (error) {
      alert('创建采购单失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleViewOrder = async (order) => {
    try {
      const response = await getPurchaseOrderById(order.po_code);
      setSelectedOrder(response.data);
    } catch (error) {
      alert('加载采购单详情失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const calculateOrderTotal = () => {
    return orderForm.items.reduce((sum, item) => sum + (parseFloat(item.total_amount) || 0), 0);
  };

  return (
    <div className="purchase-order">
      <div className="header">
        <h1>采购单管理</h1>
        <button className="create-btn" onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? '取消创建' : '+ 新建采购单'}
        </button>
      </div>

      {/* 创建采购单表单 */}
      {showCreateForm && (
        <div className="create-form-container">
          <h2>新建采购单</h2>
          <form onSubmit={handleCreateOrder}>
            <div className="form-group">
              <label>门店 ID:</label>
              <input
                type="number"
                value={orderForm.store_id}
                onChange={(e) => setOrderForm({ ...orderForm, store_id: parseInt(e.target.value) })}
              />
            </div>

            <h3>采购项目</h3>
            {orderForm.items.map((item, index) => (
              <div key={index} className="order-item">
                <div className="item-number">{index + 1}</div>
                <div className="item-fields">
                  <select
                    value={item.ingredient_name}
                    onChange={(e) => handleItemChange(index, 'ingredient_name', e.target.value)}
                    required
                  >
                    <option value="">选择原料</option>
                    {ingredients.map(ing => (
                      <option key={ing.id} value={ing.name}>{ing.name}</option>
                    ))}
                  </select>

                  <select
                    value={item.unit_name}
                    onChange={(e) => handleItemChange(index, 'unit_name', e.target.value)}
                    required
                    disabled={!item.ingredient_name}
                  >
                    <option value="">选择单位</option>
                    {getUnitsForIngredient(item.ingredient_name).map(unit => (
                      <option key={unit.id} value={unit.name}>{unit.name}</option>
                    ))}
                  </select>

                  <input
                    type="number"
                    step="0.01"
                    placeholder="数量"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                    required
                  />

                  <input
                    type="number"
                    step="0.01"
                    placeholder="总金额"
                    value={item.total_amount}
                    onChange={(e) => handleItemChange(index, 'total_amount', e.target.value)}
                    required
                  />

                  <input
                    type="text"
                    placeholder="供应商 (可选)"
                    value={item.vendor}
                    onChange={(e) => handleItemChange(index, 'vendor', e.target.value)}
                  />

                  {orderForm.items.length > 1 && (
                    <button
                      type="button"
                      className="remove-item-btn"
                      onClick={() => handleRemoveItem(index)}
                    >
                      删除
                    </button>
                  )}
                </div>
              </div>
            ))}

            <button type="button" className="add-item-btn" onClick={handleAddItem}>
              + 添加采购项
            </button>

            <div className="form-total">
              <strong>总金额: ${calculateOrderTotal().toFixed(2)}</strong>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-btn">创建采购单</button>
              <button type="button" className="cancel-btn" onClick={() => setShowCreateForm(false)}>
                取消
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 采购单列表 */}
      <div className="orders-list">
        <h2>采购单列表</h2>
        {loading ? (
          <div className="loading">加载中...</div>
        ) : purchaseOrders.length === 0 ? (
          <div className="empty">暂无采购单</div>
        ) : (
          <div className="orders-grid">
            {purchaseOrders.map(order => (
              <div key={order.po_code} className="order-card">
                <div className="order-header">
                  <span className="order-id">单号: {order.po_code}</span>
                  <span className="order-date">
                    {new Date(order.order_date).toLocaleDateString('zh-CN')}
                  </span>
                </div>
                <div className="order-info">
                  <div>门店: {order.store_id}</div>
                  <div className="order-total">总金额: ${parseFloat(order.total_amount || 0).toFixed(2)}</div>
                </div>
                <button className="view-btn" onClick={() => handleViewOrder(order)}>
                  查看详情
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 采购单详情弹窗 */}
      {selectedOrder && (
        <div className="modal-overlay" onClick={() => setSelectedOrder(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>采购单详情 {selectedOrder.po_code}</h2>
              <button className="close-btn" onClick={() => setSelectedOrder(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <strong>门店:</strong> {selectedOrder.store_id}
              </div>
              <div className="detail-row">
                <strong>创建时间:</strong> {new Date(selectedOrder.order_date).toLocaleString('zh-CN')}
              </div>
              <div className="detail-row">
                <strong>总金额:</strong> ${parseFloat(selectedOrder.total_amount || 0).toFixed(2)}
              </div>

              <h3>采购明细</h3>
              <table className="items-table">
                <thead>
                  <tr>
                    <th>原料</th>
                    <th>分类</th>
                    <th>数量</th>
                    <th>总金额</th>
                    <th>供应商</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrder.items?.map((item, index) => (
                    <tr key={index}>
                      <td>{item.ingredient_name}</td>
                      <td>{item.category_name}</td>
                      <td>{item.quantity} {item.unit_abbreviation}</td>
                      <td>${parseFloat(item.total_amount || 0).toFixed(2)}</td>
                      <td>{item.vendor || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PurchaseOrder;
