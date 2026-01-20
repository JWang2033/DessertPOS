import { useState, useEffect } from 'react';
import {
  getInventory,
  createInventory,
  updateInventory,
  getIngredients,
  getUnits,
} from '../services/api';
import './Inventory.css';

function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // 筛选和排序选项
  const [groupBy, setGroupBy] = useState(''); // '', 'location', 'restock_needed'
  const [sortBy, setSortBy] = useState(''); // '', 'actual_qty', 'standard_qty', 'update_time'
  const [storeId, setStoreId] = useState(1);

  // 创建库存表单
  const [newInventory, setNewInventory] = useState({
    ingredient_name: '',
    unit_name: '',
    standard_qty: '',
    actual_qty: '',
    location: '',
    store_id: 1,
  });

  // 编辑库存
  const [editingId, setEditingId] = useState(null);
  const [editingQty, setEditingQty] = useState('');

  useEffect(() => {
    loadInventory();
    loadIngredients();
    loadUnits();
  }, [groupBy, sortBy, storeId]);

  const loadInventory = async () => {
    try {
      setLoading(true);
      const params = {};
      if (groupBy) params.group_by = groupBy;
      if (sortBy) params.sort_by = sortBy;
      if (storeId) params.store_id = storeId;

      const response = await getInventory(params);
      setInventory(response.data);
    } catch (error) {
      alert('加载库存失败: ' + (error.response?.data?.detail || error.message));
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

  const handleCreateInventory = async (e) => {
    e.preventDefault();

    if (!newInventory.ingredient_name || !newInventory.unit_name ||
        !newInventory.standard_qty || !newInventory.actual_qty) {
      alert('请填写完整的库存信息');
      return;
    }

    try {
      const data = {
        ingredient_name: newInventory.ingredient_name,
        unit_name: newInventory.unit_name,
        standard_qty: parseFloat(newInventory.standard_qty),
        actual_qty: parseFloat(newInventory.actual_qty),
        location: newInventory.location || null,
        store_id: newInventory.store_id,
      };

      await createInventory(data);
      alert('库存创建成功');
      setShowCreateForm(false);
      setNewInventory({
        ingredient_name: '',
        unit_name: '',
        standard_qty: '',
        actual_qty: '',
        location: '',
        store_id: 1,
      });
      loadInventory();
    } catch (error) {
      alert('创建库存失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStartEdit = (item) => {
    setEditingId(item.inventory_id);
    setEditingQty(item.actual_qty.toString());
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingQty('');
  };

  const handleSaveEdit = async (id) => {
    if (!editingQty || parseFloat(editingQty) < 0) {
      alert('请输入有效的数量');
      return;
    }

    try {
      await updateInventory(id, { actual_qty: parseFloat(editingQty) });
      alert('更新成功');
      setEditingId(null);
      setEditingQty('');
      loadInventory();
    } catch (error) {
      alert('更新失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getStockStatus = (item) => {
    if (item.restock_needed) {
      return { text: '需要补货', className: 'status-warning' };
    }
    if (item.actual_qty >= item.standard_qty) {
      return { text: '充足', className: 'status-good' };
    }
    return { text: '正常', className: 'status-normal' };
  };

  const renderGroupedInventory = () => {
    if (!groupBy) {
      return (
        <div className="inventory-table-container">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>原料</th>
                <th>分类</th>
                <th>品牌</th>
                <th>标准库存</th>
                <th>实际库存</th>
                <th>位置</th>
                <th>状态</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map(item => {
                const status = getStockStatus(item);
                return (
                  <tr key={item.inventory_id}>
                    <td><strong>{item.ingredient_name}</strong></td>
                    <td>{item.category_name}</td>
                    <td>{item.brand || '-'}</td>
                    <td>{item.standard_qty} {item.unit_abbreviation}</td>
                    <td>
                      {editingId === item.inventory_id ? (
                        <input
                          type="number"
                          step="0.01"
                          value={editingQty}
                          onChange={(e) => setEditingQty(e.target.value)}
                          className="edit-input"
                          autoFocus
                        />
                      ) : (
                        <span className={item.restock_needed ? 'low-stock' : ''}>
                          {item.actual_qty} {item.unit_abbreviation}
                        </span>
                      )}
                    </td>
                    <td>{item.location || '-'}</td>
                    <td>
                      <span className={`status-badge ${status.className}`}>
                        {status.text}
                      </span>
                    </td>
                    <td>{new Date(item.update_time).toLocaleString('zh-CN')}</td>
                    <td>
                      {editingId === item.inventory_id ? (
                        <div className="edit-actions">
                          <button className="save-btn" onClick={() => handleSaveEdit(item.inventory_id)}>
                            保存
                          </button>
                          <button className="cancel-btn-small" onClick={handleCancelEdit}>
                            取消
                          </button>
                        </div>
                      ) : (
                        <button className="edit-btn" onClick={() => handleStartEdit(item)}>
                          编辑
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
    }

    // 分组显示
    const grouped = {};
    inventory.forEach(item => {
      const key = groupBy === 'location'
        ? (item.location || '未分配位置')
        : (item.restock_needed ? '需要补货' : '库存充足');

      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(item);
    });

    return (
      <div className="grouped-inventory">
        {Object.entries(grouped).map(([groupName, items]) => (
          <div key={groupName} className="inventory-group">
            <h3 className="group-title">
              {groupName} ({items.length})
            </h3>
            <div className="inventory-grid">
              {items.map(item => {
                const status = getStockStatus(item);
                return (
                  <div key={item.inventory_id} className="inventory-card">
                    <div className="card-header">
                      <h4>{item.ingredient_name}</h4>
                      <span className={`status-badge ${status.className}`}>
                        {status.text}
                      </span>
                    </div>
                    <div className="card-body">
                      <div className="info-row">
                        <span className="label">分类:</span>
                        <span>{item.category_name}</span>
                      </div>
                      {item.brand && (
                        <div className="info-row">
                          <span className="label">品牌:</span>
                          <span>{item.brand}</span>
                        </div>
                      )}
                      <div className="info-row">
                        <span className="label">标准库存:</span>
                        <span>{item.standard_qty} {item.unit_abbreviation}</span>
                      </div>
                      <div className="info-row">
                        <span className="label">实际库存:</span>
                        {editingId === item.inventory_id ? (
                          <input
                            type="number"
                            step="0.01"
                            value={editingQty}
                            onChange={(e) => setEditingQty(e.target.value)}
                            className="edit-input"
                            autoFocus
                          />
                        ) : (
                          <span className={item.restock_needed ? 'low-stock' : ''}>
                            {item.actual_qty} {item.unit_abbreviation}
                          </span>
                        )}
                      </div>
                      {item.location && (
                        <div className="info-row">
                          <span className="label">位置:</span>
                          <span>{item.location}</span>
                        </div>
                      )}
                      <div className="info-row">
                        <span className="label">更新:</span>
                        <span className="small-text">
                          {new Date(item.update_time).toLocaleString('zh-CN')}
                        </span>
                      </div>
                    </div>
                    <div className="card-footer">
                      {editingId === item.inventory_id ? (
                        <div className="edit-actions">
                          <button className="save-btn" onClick={() => handleSaveEdit(item.inventory_id)}>
                            保存
                          </button>
                          <button className="cancel-btn-small" onClick={handleCancelEdit}>
                            取消
                          </button>
                        </div>
                      ) : (
                        <button className="edit-btn" onClick={() => handleStartEdit(item)}>
                          编辑库存
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="inventory">
      <div className="header">
        <h1>库存管理</h1>
        <button className="create-btn" onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? '取消创建' : '+ 新建库存'}
        </button>
      </div>

      {/* 筛选和排序工具栏 */}
      <div className="toolbar">
        <div className="toolbar-section">
          <label>门店:</label>
          <select value={storeId} onChange={(e) => setStoreId(parseInt(e.target.value))}>
            <option value={1}>门店 1</option>
            <option value={2}>门店 2</option>
            <option value={3}>门店 3</option>
          </select>
        </div>

        <div className="toolbar-section">
          <label>分组方式:</label>
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
            <option value="">不分组</option>
            <option value="location">按位置分组</option>
            <option value="restock_needed">按补货状态分组</option>
          </select>
        </div>

        <div className="toolbar-section">
          <label>排序方式:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="">默认排序</option>
            <option value="actual_qty">按实际库存排序</option>
            <option value="standard_qty">按标准库存排序</option>
            <option value="update_time">按更新时间排序</option>
          </select>
        </div>

        <button className="refresh-btn" onClick={loadInventory}>
          刷新
        </button>
      </div>

      {/* 创建库存表单 */}
      {showCreateForm && (
        <div className="create-form-container">
          <h2>新建库存记录</h2>
          <form onSubmit={handleCreateInventory}>
            <div className="form-row">
              <div className="form-group">
                <label>原料 *</label>
                <select
                  value={newInventory.ingredient_name}
                  onChange={(e) => setNewInventory({ ...newInventory, ingredient_name: e.target.value })}
                  required
                >
                  <option value="">选择原料</option>
                  {ingredients.map(ing => (
                    <option key={ing.id} value={ing.name}>{ing.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>单位 *</label>
                <select
                  value={newInventory.unit_name}
                  onChange={(e) => setNewInventory({ ...newInventory, unit_name: e.target.value })}
                  required
                >
                  <option value="">选择单位</option>
                  {units.map(unit => (
                    <option key={unit.id} value={unit.name}>{unit.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>标准库存 *</label>
                <input
                  type="number"
                  step="0.01"
                  value={newInventory.standard_qty}
                  onChange={(e) => setNewInventory({ ...newInventory, standard_qty: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>实际库存 *</label>
                <input
                  type="number"
                  step="0.01"
                  value={newInventory.actual_qty}
                  onChange={(e) => setNewInventory({ ...newInventory, actual_qty: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>存放位置</label>
                <input
                  type="text"
                  placeholder="如: 冷藏区A"
                  value={newInventory.location}
                  onChange={(e) => setNewInventory({ ...newInventory, location: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>门店 ID</label>
                <input
                  type="number"
                  value={newInventory.store_id}
                  onChange={(e) => setNewInventory({ ...newInventory, store_id: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-btn">创建库存</button>
              <button type="button" className="cancel-btn" onClick={() => setShowCreateForm(false)}>
                取消
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 库存列表 */}
      <div className="inventory-content">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : inventory.length === 0 ? (
          <div className="empty">暂无库存记录</div>
        ) : (
          renderGroupedInventory()
        )}
      </div>
    </div>
  );
}

export default Inventory;
