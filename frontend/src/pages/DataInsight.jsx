import { useState, useEffect } from 'react';
import { getInventory } from '../services/api';
import './DataInsight.css';

function DataInsight() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(false);

  // 筛选和排序选项
  const [groupBy, setGroupBy] = useState(''); // '', 'store_id', 'restock_needed'
  const [sortBy, setSortBy] = useState(''); // '', 'actual_qty', 'standard_qty', 'update_time'

  useEffect(() => {
    loadInventory();
  }, [groupBy, sortBy]);

  const loadInventory = async () => {
    try {
      setLoading(true);
      const params = {};
      if (groupBy) params.group_by = groupBy;
      if (sortBy) params.sort_by = sortBy;

      const response = await getInventory(params);
      setInventory(response.data);
    } catch (error) {
      alert('加载数据失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const renderGroupedInventory = () => {
    if (!groupBy) {
      return (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Store ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Brand</th>
                <th>实际量</th>
                <th>Unit</th>
                <th>Update time</th>
                <th>补货提醒</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map(item => {
                const needsRestock = item.threshold && item.standard_qty < parseFloat(item.threshold);
                return (
                  <tr key={item.inventory_id}>
                    <td>-</td>
                    <td><strong>{item.ingredient_name}</strong></td>
                    <td>{item.category_name}</td>
                    <td>{item.brand || '-'}</td>
                    <td>{item.actual_qty}</td>
                    <td>{item.unit_abbreviation}</td>
                    <td>{new Date(item.update_time).toLocaleString('zh-CN')}</td>
                    <td>
                      {needsRestock && (
                        <span className="checkmark">✓</span>
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

    // 分组逻辑
    const grouped = {};
    inventory.forEach(item => {
      let groupName = '';
      if (groupBy === 'store_id') {
        groupName = `Store ${item.store_id || 'N/A'}`;
      } else if (groupBy === 'restock_needed') {
        const needsRestock = item.threshold && item.standard_qty < parseFloat(item.threshold);
        groupName = needsRestock ? '需要补货' : '充足';
      }

      if (!grouped[groupName]) {
        grouped[groupName] = [];
      }
      grouped[groupName].push(item);
    });

    return (
      <div className="grouped-data">
        {Object.entries(grouped).map(([groupName, items]) => (
          <div key={groupName} className="data-group">
            <h3 className="group-title">
              {groupName} ({items.length})
            </h3>
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Store ID</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Brand</th>
                    <th>实际量</th>
                    <th>Unit</th>
                    <th>Update time</th>
                    <th>补货提醒</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map(item => {
                    const needsRestock = item.threshold && item.standard_qty < parseFloat(item.threshold);
                    return (
                      <tr key={item.inventory_id}>
                        <td>-</td>
                        <td><strong>{item.ingredient_name}</strong></td>
                        <td>{item.category_name}</td>
                        <td>{item.brand || '-'}</td>
                        <td>{item.actual_qty}</td>
                        <td>{item.unit_abbreviation}</td>
                        <td>{new Date(item.update_time).toLocaleString('zh-CN')}</td>
                        <td>
                          {needsRestock && (
                            <span className="checkmark">✓</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="data-insight">
      <div className="header">
        <h1>数据洞察 (Data Insight)</h1>
        <p className="subtitle">User: Operation Manager</p>
      </div>

      {/* 筛选和排序工具栏 */}
      <div className="toolbar">
        <div className="toolbar-section">
          <label>支持Group by:</label>
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
            <option value="">不分组</option>
            <option value="store_id">Store ID</option>
            <option value="restock_needed">需要补货</option>
          </select>
        </div>

        <div className="toolbar-section">
          <label>支持Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="">默认排序</option>
            <option value="actual_qty">实际量</option>
            <option value="standard_qty">标准量</option>
            <option value="update_time">Update time</option>
          </select>
        </div>
      </div>

      {/* 数据列表 */}
      <div className="data-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : inventory.length === 0 ? (
          <div className="empty">暂无数据</div>
        ) : (
          renderGroupedInventory()
        )}
      </div>
    </div>
  );
}

export default DataInsight;
