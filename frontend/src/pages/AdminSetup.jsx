import { useState, useEffect } from 'react';
import {
  getUnits,
  createUnit,
  deleteUnit,
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  getIngredients,
  batchCreateIngredients,
  updateIngredient,
  deleteIngredient,
  getProducts,
  getProductByName,
  createProduct,
  updateProduct,
} from '../services/api';
import './AdminSetup.css';

function AdminSetup() {
  const [activeTab, setActiveTab] = useState('units'); // units, categories, ingredients, products
  const [units, setUnits] = useState([]);
  const [categories, setCategories] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [newUnit, setNewUnit] = useState({ name: '', abbreviation: '' });
  const [newCategory, setNewCategory] = useState({ name: '', selectedUnits: [] });
  const [newIngredient, setNewIngredient] = useState({ name: '', category_name: '', unit_name: '', brand: '', threshold: '' });
  const [newProduct, setNewProduct] = useState({ name: '', prep_time_hours: '', ingredients: [] });
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingIngredient, setEditingIngredient] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    loadUnits(); // Always load units first for category management
    if (activeTab === 'units') loadUnits();
    else if (activeTab === 'categories') loadCategories();
    else if (activeTab === 'ingredients') {
      loadCategories(); // Load categories for dropdown
      loadIngredients();
    }
    else if (activeTab === 'products') {
      loadIngredients(); // Load ingredients for product creation
      loadProducts();
    }
  }, [activeTab]);

  // ========== 单位管理 ==========
  const loadUnits = async () => {
    try {
      setLoading(true);
      const response = await getUnits();
      setUnits(response.data);
    } catch (error) {
      alert('加载单位失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUnit = async (e) => {
    e.preventDefault();
    if (!newUnit.name || !newUnit.abbreviation) {
      alert('请填写完整信息');
      return;
    }
    try {
      await createUnit([newUnit]); // Wrap in array as backend expects List[UnitCreate]
      setNewUnit({ name: '', abbreviation: '' });
      loadUnits();
      alert('创建成功');
    } catch (error) {
      alert('创建失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteUnit = async (unit) => {
    if (!confirm('确定删除此单位吗？')) return;
    try {
      await deleteUnit(unit.name);
      loadUnits();
      alert('删除成功');
    } catch (error) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  // ========== 分类管理 ==========
  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await getCategories();
      setCategories(response.data);
    } catch (error) {
      alert('加载分类失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!newCategory.name) {
      alert('请填写分类名称');
      return;
    }
    if (newCategory.selectedUnits.length === 0) {
      alert('请至少选择一个单位');
      return;
    }
    try {
      const categoryData = {
        name: newCategory.name,
        tag: newCategory.tag || null,
        unit_names: newCategory.selectedUnits
      };
      await createCategory(categoryData);
      setNewCategory({ name: '', selectedUnits: [] });
      loadCategories();
      alert('创建成功');
    } catch (error) {
      alert('创建失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUpdateCategory = async (e) => {
    e.preventDefault();
    if (!editingCategory) return;

    if (editingCategory.selectedUnits.length === 0) {
      alert('请至少选择一个单位');
      return;
    }

    try {
      const categoryData = {
        name: editingCategory.name,
        tag: editingCategory.tag || null,
        unit_names: editingCategory.selectedUnits
      };
      await updateCategory(editingCategory.originalName, categoryData);
      setEditingCategory(null);
      loadCategories();
      alert('更新成功');
    } catch (error) {
      alert('更新失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStartEditCategory = (category) => {
    setEditingCategory({
      originalName: category.name,
      name: category.name,
      tag: category.tag || '',
      selectedUnits: category.units ? category.units.map(u => u.name) : []
    });
  };

  const handleToggleUnit = (unitName, isEditing = false) => {
    if (isEditing && editingCategory) {
      const selected = editingCategory.selectedUnits.includes(unitName);
      setEditingCategory({
        ...editingCategory,
        selectedUnits: selected
          ? editingCategory.selectedUnits.filter(u => u !== unitName)
          : [...editingCategory.selectedUnits, unitName]
      });
    } else {
      const selected = newCategory.selectedUnits.includes(unitName);
      setNewCategory({
        ...newCategory,
        selectedUnits: selected
          ? newCategory.selectedUnits.filter(u => u !== unitName)
          : [...newCategory.selectedUnits, unitName]
      });
    }
  };

  const handleDeleteCategory = async (category) => {
    if (!confirm('确定删除此分类吗？')) return;
    try {
      await deleteCategory(category.name);
      loadCategories();
      alert('删除成功');
    } catch (error) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  // ========== 原料批量创建 ==========
  const loadIngredients = async () => {
    try {
      setLoading(true);
      const response = await getIngredients();
      setIngredients(response.data);
    } catch (error) {
      alert('加载原料失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIngredient = async (e) => {
    e.preventDefault();
    if (!newIngredient.name || !newIngredient.category_name || !newIngredient.unit_name) {
      alert('请填写名称、分类和单位');
      return;
    }

    try {
      const ingredientData = {
        name: newIngredient.name,
        category_name: newIngredient.category_name,
        unit_name: newIngredient.unit_name,
        brand: newIngredient.brand || null,
        threshold: newIngredient.threshold ? parseFloat(newIngredient.threshold) : null,
      };

      await batchCreateIngredients([ingredientData]);
      setNewIngredient({ name: '', category_name: '', unit_name: '', brand: '', threshold: '' });
      loadIngredients();
      alert('创建成功');
    } catch (error) {
      alert('创建失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUpdateIngredient = async (e) => {
    e.preventDefault();
    if (!editingIngredient) return;

    if (!editingIngredient.name || !editingIngredient.category_name || !editingIngredient.unit_name) {
      alert('请填写名称、分类和单位');
      return;
    }

    try {
      const ingredientData = {
        name: editingIngredient.name,
        category_name: editingIngredient.category_name,
        unit_name: editingIngredient.unit_name,
        brand: editingIngredient.brand || null,
        threshold: editingIngredient.threshold ? parseFloat(editingIngredient.threshold) : null,
      };
      await updateIngredient(editingIngredient.originalName, ingredientData);
      setEditingIngredient(null);
      loadIngredients();
      alert('更新成功');
    } catch (error) {
      alert('更新失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStartEditIngredient = (ingredient) => {
    setEditingIngredient({
      originalName: ingredient.name,
      name: ingredient.name,
      category_name: ingredient.category_name,
      unit_name: ingredient.unit_name,
      brand: ingredient.brand || '',
      threshold: ingredient.threshold || ''
    });
  };

  const handleDeleteIngredient = async (ingredient) => {
    if (!confirm(`确定删除原料 "${ingredient.name}" 吗？`)) return;
    try {
      await deleteIngredient(ingredient.name);
      loadIngredients();
      alert('删除成功');
    } catch (error) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  // ========== 半成品批量创建 ==========
  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await getProducts();

      // Fetch full details for each product to get ingredients
      const productsWithDetails = await Promise.all(
        response.data.map(async (product) => {
          try {
            const detailResponse = await getProductByName(product.name);
            return detailResponse.data;
          } catch (error) {
            console.error(`Failed to load details for ${product.name}:`, error);
            return product; // Return basic info if detail fetch fails
          }
        })
      );

      setProducts(productsWithDetails);
    } catch (error) {
      alert('加载半成品失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAddIngredientRow = () => {
    setNewProduct({
      ...newProduct,
      ingredients: [...newProduct.ingredients, { ingredient_name: '', quantity: '', unit_name: '' }]
    });
  };

  const handleRemoveIngredientRow = (index) => {
    const updatedIngredients = newProduct.ingredients.filter((_, i) => i !== index);
    setNewProduct({ ...newProduct, ingredients: updatedIngredients });
  };

  const handleIngredientChange = (index, field, value) => {
    const updatedIngredients = [...newProduct.ingredients];
    updatedIngredients[index][field] = value;

    // Auto-fill unit when ingredient is selected
    if (field === 'ingredient_name' && value) {
      const selectedIngredient = ingredients.find(ing => ing.name === value);
      if (selectedIngredient) {
        updatedIngredients[index].unit_name = selectedIngredient.unit_name;
      }
    }

    setNewProduct({ ...newProduct, ingredients: updatedIngredients });
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    if (!newProduct.name || !newProduct.prep_time_hours) {
      alert('请填写名称和准备时间');
      return;
    }
    if (newProduct.ingredients.length === 0) {
      alert('请至少添加一个原料');
      return;
    }

    // Validate all ingredients have required fields
    for (const ing of newProduct.ingredients) {
      if (!ing.ingredient_name || !ing.quantity || !ing.unit_name) {
        alert('请填写所有原料的完整信息');
        return;
      }
    }

    try {
      const productData = {
        name: newProduct.name,
        prep_time_hours: parseFloat(newProduct.prep_time_hours),
        ingredients: newProduct.ingredients.map(ing => ({
          ingredient_name: ing.ingredient_name,
          quantity: parseFloat(ing.quantity),
          unit_name: ing.unit_name
        }))
      };

      await createProduct(productData);
      setNewProduct({ name: '', prep_time_hours: '', ingredients: [] });
      loadProducts();
      alert('创建成功');
    } catch (error) {
      alert('创建失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStartEditProduct = (product) => {
    setEditingProduct({
      originalName: product.name,
      name: product.name,
      prep_time_hours: product.prep_time_hours,
      ingredients: product.ingredients.map(ing => ({
        ingredient_name: ing.ingredient_name,
        quantity: ing.quantity,
        unit_name: ing.unit_abbreviation
      }))
    });
  };

  const handleEditIngredientChange = (index, field, value) => {
    const updatedIngredients = [...editingProduct.ingredients];
    updatedIngredients[index][field] = value;

    // Auto-fill unit when ingredient is selected
    if (field === 'ingredient_name' && value) {
      const selectedIngredient = ingredients.find(ing => ing.name === value);
      if (selectedIngredient) {
        updatedIngredients[index].unit_name = selectedIngredient.unit_name;
      }
    }

    setEditingProduct({ ...editingProduct, ingredients: updatedIngredients });
  };

  const handleAddEditIngredientRow = () => {
    setEditingProduct({
      ...editingProduct,
      ingredients: [...editingProduct.ingredients, { ingredient_name: '', quantity: '', unit_name: '' }]
    });
  };

  const handleRemoveEditIngredientRow = (index) => {
    const updatedIngredients = editingProduct.ingredients.filter((_, i) => i !== index);
    setEditingProduct({ ...editingProduct, ingredients: updatedIngredients });
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    if (!editingProduct) return;

    if (!editingProduct.name || !editingProduct.prep_time_hours) {
      alert('请填写名称和准备时间');
      return;
    }
    if (editingProduct.ingredients.length === 0) {
      alert('请至少添加一个原料');
      return;
    }

    // Validate all ingredients have required fields
    for (const ing of editingProduct.ingredients) {
      if (!ing.ingredient_name || !ing.quantity || !ing.unit_name) {
        alert('请填写所有原料的完整信息');
        return;
      }
    }

    try {
      const productData = {
        name: editingProduct.name,
        prep_time_hours: parseFloat(editingProduct.prep_time_hours),
        ingredients: editingProduct.ingredients.map(ing => ({
          ingredient_name: ing.ingredient_name,
          quantity: parseFloat(ing.quantity),
          unit_name: ing.unit_name
        }))
      };

      await updateProduct(editingProduct.originalName, productData);
      setEditingProduct(null);
      loadProducts();
      alert('更新成功');
    } catch (error) {
      alert('更新失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="admin-setup">
      <div className="tabs">
        <button
          className={activeTab === 'units' ? 'active' : ''}
          onClick={() => setActiveTab('units')}
        >
          单位管理
        </button>
        <button
          className={activeTab === 'categories' ? 'active' : ''}
          onClick={() => setActiveTab('categories')}
        >
          分类管理
        </button>
        <button
          className={activeTab === 'ingredients' ? 'active' : ''}
          onClick={() => setActiveTab('ingredients')}
        >
          批量创建原料
        </button>
        <button
          className={activeTab === 'products' ? 'active' : ''}
          onClick={() => setActiveTab('products')}
        >
          创建半成品
        </button>
      </div>

      <div className="tab-content">
        {loading && <div className="loading">加载中...</div>}

        {/* 单位管理 */}
        {activeTab === 'units' && (
          <div className="units-section">
            <h2>单位管理</h2>
            <form onSubmit={handleCreateUnit} className="create-form">
              <input
                type="text"
                placeholder="单位名称 (如: 克)"
                value={newUnit.name}
                onChange={(e) => setNewUnit({ ...newUnit, name: e.target.value })}
              />
              <input
                type="text"
                placeholder="缩写 (如: g)"
                value={newUnit.abbreviation}
                onChange={(e) => setNewUnit({ ...newUnit, abbreviation: e.target.value })}
              />
              <button type="submit">创建单位</button>
            </form>

            <div className="list">
              {units.map(unit => (
                <div key={unit.id} className="list-item">
                  <span><strong>{unit.name}</strong> ({unit.abbreviation})</span>
                  <button onClick={() => handleDeleteUnit(unit)} className="delete-btn">
                    删除
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 分类管理 */}
        {activeTab === 'categories' && (
          <div className="categories-section">
            <h2>分类管理</h2>
            <form onSubmit={handleCreateCategory} className="create-form">
              <input
                type="text"
                placeholder="分类名称 (如: 水果)"
                value={newCategory.name}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
              />
              <div className="unit-selection">
                <label>允许的单位:</label>
                <div className="checkbox-group">
                  {units.map(unit => (
                    <label key={unit.id} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={newCategory.selectedUnits.includes(unit.name)}
                        onChange={() => handleToggleUnit(unit.name, false)}
                      />
                      <span>{unit.name} ({unit.abbreviation})</span>
                    </label>
                  ))}
                </div>
              </div>
              <button type="submit">创建分类</button>
            </form>

            {editingCategory && (
              <div className="edit-modal">
                <div className="modal-content">
                  <h3>编辑分类</h3>
                  <form onSubmit={handleUpdateCategory}>
                    <input
                      type="text"
                      value={editingCategory.name}
                      onChange={(e) => setEditingCategory({ ...editingCategory, name: e.target.value })}
                      placeholder="分类名称"
                    />
                    <div className="unit-selection">
                      <label>允许的单位:</label>
                      <div className="checkbox-group">
                        {units.map(unit => (
                          <label key={unit.id} className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={editingCategory.selectedUnits.includes(unit.name)}
                              onChange={() => handleToggleUnit(unit.name, true)}
                            />
                            <span>{unit.name} ({unit.abbreviation})</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="modal-actions">
                      <button type="submit">保存</button>
                      <button type="button" onClick={() => setEditingCategory(null)}>取消</button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="list">
              {categories.map(category => (
                <div key={category.id} className="list-item">
                  <div className="category-detail">
                    <strong>{category.name}</strong>
                    {category.units && category.units.length > 0 && (
                      <div className="unit-badges">
                        {category.units.map(unit => (
                          <span key={unit.id} className="badge">{unit.abbreviation}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="item-actions">
                    <button onClick={() => handleStartEditCategory(category)} className="edit-btn">编辑</button>
                    <button onClick={() => handleDeleteCategory(category)} className="delete-btn">删除</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 原料创建 */}
        {activeTab === 'ingredients' && (
          <div className="ingredients-section">
            <h2>创建原料</h2>
            <form onSubmit={handleCreateIngredient} className="ingredient-form">
              <div className="form-grid">
                <div className="form-field">
                  <label>名称 *</label>
                  <input
                    type="text"
                    placeholder="如：草莓"
                    value={newIngredient.name}
                    onChange={(e) => setNewIngredient({ ...newIngredient, name: e.target.value })}
                  />
                </div>
                <div className="form-field">
                  <label>分类 *</label>
                  <select
                    value={newIngredient.category_name}
                    onChange={(e) => setNewIngredient({ ...newIngredient, category_name: e.target.value })}
                  >
                    <option value="">选择分类</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.name}>{cat.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label>单位 *</label>
                  <select
                    value={newIngredient.unit_name}
                    onChange={(e) => setNewIngredient({ ...newIngredient, unit_name: e.target.value })}
                  >
                    <option value="">选择单位</option>
                    {units.map(unit => (
                      <option key={unit.id} value={unit.name}>{unit.name} ({unit.abbreviation})</option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label>品牌(可选)</label>
                  <input
                    type="text"
                    placeholder="如：新鲜果园"
                    value={newIngredient.brand}
                    onChange={(e) => setNewIngredient({ ...newIngredient, brand: e.target.value })}
                  />
                </div>
                <div className="form-field">
                  <label>阈值(可选)</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="如：50"
                    value={newIngredient.threshold}
                    onChange={(e) => setNewIngredient({ ...newIngredient, threshold: e.target.value })}
                  />
                </div>
              </div>
              <button type="submit" className="submit-btn">创建原料</button>
            </form>

            {editingIngredient && (
              <div className="edit-modal">
                <div className="modal-content">
                  <h3>编辑原料</h3>
                  <form onSubmit={handleUpdateIngredient}>
                    <div className="form-grid">
                      <div className="form-field">
                        <label>名称 *</label>
                        <input
                          type="text"
                          value={editingIngredient.name}
                          onChange={(e) => setEditingIngredient({ ...editingIngredient, name: e.target.value })}
                        />
                      </div>
                      <div className="form-field">
                        <label>分类 *</label>
                        <select
                          value={editingIngredient.category_name}
                          onChange={(e) => setEditingIngredient({ ...editingIngredient, category_name: e.target.value })}
                        >
                          <option value="">选择分类</option>
                          {categories.map(cat => (
                            <option key={cat.id} value={cat.name}>{cat.name}</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-field">
                        <label>单位 *</label>
                        <select
                          value={editingIngredient.unit_name}
                          onChange={(e) => setEditingIngredient({ ...editingIngredient, unit_name: e.target.value })}
                        >
                          <option value="">选择单位</option>
                          {units.map(unit => (
                            <option key={unit.id} value={unit.name}>{unit.name} ({unit.abbreviation})</option>
                          ))}
                        </select>
                      </div>
                      <div className="form-field">
                        <label>品牌(可选)</label>
                        <input
                          type="text"
                          value={editingIngredient.brand}
                          onChange={(e) => setEditingIngredient({ ...editingIngredient, brand: e.target.value })}
                        />
                      </div>
                      <div className="form-field">
                        <label>阈值(可选)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={editingIngredient.threshold}
                          onChange={(e) => setEditingIngredient({ ...editingIngredient, threshold: e.target.value })}
                        />
                      </div>
                    </div>
                    <div className="modal-actions">
                      <button type="submit">保存</button>
                      <button type="button" onClick={() => setEditingIngredient(null)}>取消</button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <h3>现有原料 ({ingredients.length})</h3>
            <div className="ingredients-grid">
              {ingredients.map(ing => (
                <div key={ing.id} className="ingredient-card">
                  <div className="card-field">
                    <span className="field-label">名称:</span>
                    <span className="field-value">{ing.name}</span>
                  </div>
                  <div className="card-field">
                    <span className="field-label">分类:</span>
                    <span className="field-value">{ing.category_name}</span>
                  </div>
                  <div className="card-field">
                    <span className="field-label">单位:</span>
                    <span className="field-value">{ing.unit_name}</span>
                  </div>
                  {ing.brand && (
                    <div className="card-field">
                      <span className="field-label">品牌:</span>
                      <span className="field-value">{ing.brand}</span>
                    </div>
                  )}
                  {ing.threshold && (
                    <div className="card-field">
                      <span className="field-label">阈值:</span>
                      <span className="field-value">{ing.threshold}</span>
                    </div>
                  )}
                  <div className="card-actions">
                    <button onClick={() => handleStartEditIngredient(ing)} className="edit-btn">编辑</button>
                    <button onClick={() => handleDeleteIngredient(ing)} className="delete-btn">删除</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 半成品批量创建 */}
        {activeTab === 'products' && (
          <div className="products-section">
            <h2>创建半成品</h2>
            <form onSubmit={handleCreateProduct} className="product-form">
              <div className="form-row">
                <div className="form-field">
                  <label>Name:</label>
                  <input
                    type="text"
                    value={newProduct.name}
                    onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                    placeholder="输入半成品名称"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Prep time: <input
                    type="number"
                    step="0.1"
                    value={newProduct.prep_time_hours}
                    onChange={(e) => setNewProduct({ ...newProduct, prep_time_hours: e.target.value })}
                    placeholder="0"
                    style={{ width: '80px', display: 'inline' }}
                  /> hours</label>
                </div>
              </div>

              <div className="form-row">
                <label>Ingredients:</label>
              </div>

              <div className="ingredients-table">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Quantity</th>
                      <th>Unit</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {newProduct.ingredients.length === 0 ? (
                      <tr>
                        <td colSpan="4" style={{ textAlign: 'center', color: '#999' }}>
                          (只能从已有的ingredients里面选，支持autofill)
                        </td>
                      </tr>
                    ) : (
                      newProduct.ingredients.map((ing, index) => (
                        <tr key={index}>
                          <td>
                            <select
                              value={ing.ingredient_name}
                              onChange={(e) => handleIngredientChange(index, 'ingredient_name', e.target.value)}
                            >
                              <option value="">选择原料</option>
                              {ingredients.map(ingredient => (
                                <option key={ingredient.id} value={ingredient.name}>
                                  {ingredient.name}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td>
                            <input
                              type="number"
                              step="0.01"
                              value={ing.quantity}
                              onChange={(e) => handleIngredientChange(index, 'quantity', e.target.value)}
                              placeholder="数量"
                            />
                          </td>
                          <td>
                            <input
                              type="text"
                              value={ing.unit_name}
                              readOnly
                              placeholder="单位"
                              style={{ backgroundColor: '#f5f5f5' }}
                            />
                          </td>
                          <td>
                            <button
                              type="button"
                              onClick={() => handleRemoveIngredientRow(index)}
                              className="remove-row-btn"
                            >
                              ×
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                    <tr>
                      <td colSpan="4">
                        <button
                          type="button"
                          onClick={handleAddIngredientRow}
                          className="add-row-btn"
                        >
                          + 添加原料
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <button type="submit" className="submit-btn">创建半成品</button>
            </form>

            {editingProduct && (
              <div className="edit-modal">
                <div className="modal-content">
                  <h3>编辑半成品</h3>
                  <form onSubmit={handleUpdateProduct} className="product-form">
                    <div className="form-row">
                      <div className="form-field">
                        <label>Name:</label>
                        <input
                          type="text"
                          value={editingProduct.name}
                          onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                          placeholder="输入半成品名称"
                        />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-field">
                        <label>Prep time: <input
                          type="number"
                          step="0.1"
                          value={editingProduct.prep_time_hours}
                          onChange={(e) => setEditingProduct({ ...editingProduct, prep_time_hours: e.target.value })}
                          placeholder="0"
                          style={{ width: '80px', display: 'inline' }}
                        /> hours</label>
                      </div>
                    </div>

                    <div className="form-row">
                      <label>Ingredients:</label>
                    </div>

                    <div className="ingredients-table">
                      <table>
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>Quantity</th>
                            <th>Unit</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          {editingProduct.ingredients.map((ing, index) => (
                            <tr key={index}>
                              <td>
                                <select
                                  value={ing.ingredient_name}
                                  onChange={(e) => handleEditIngredientChange(index, 'ingredient_name', e.target.value)}
                                >
                                  <option value="">选择原料</option>
                                  {ingredients.map(ingredient => (
                                    <option key={ingredient.id} value={ingredient.name}>
                                      {ingredient.name}
                                    </option>
                                  ))}
                                </select>
                              </td>
                              <td>
                                <input
                                  type="number"
                                  step="0.01"
                                  value={ing.quantity}
                                  onChange={(e) => handleEditIngredientChange(index, 'quantity', e.target.value)}
                                  placeholder="数量"
                                />
                              </td>
                              <td>
                                <input
                                  type="text"
                                  value={ing.unit_name}
                                  readOnly
                                  placeholder="单位"
                                  style={{ backgroundColor: '#f5f5f5' }}
                                />
                              </td>
                              <td>
                                <button
                                  type="button"
                                  onClick={() => handleRemoveEditIngredientRow(index)}
                                  className="remove-row-btn"
                                >
                                  ×
                                </button>
                              </td>
                            </tr>
                          ))}
                          <tr>
                            <td colSpan="4">
                              <button
                                type="button"
                                onClick={handleAddEditIngredientRow}
                                className="add-row-btn"
                              >
                                + 添加原料
                              </button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                    <div className="modal-actions">
                      <button type="submit">保存</button>
                      <button type="button" onClick={() => setEditingProduct(null)}>取消</button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <h3>现有半成品 ({products.length})</h3>
            <div className="products-list">
              {products.map(prod => (
                <div key={prod.id} className="product-card">
                  <div className="product-header">
                    <strong>{prod.name}</strong>
                    <span className="prep-time">准备时间: {prod.prep_time_hours} 小时</span>
                  </div>
                  {prod.ingredients && prod.ingredients.length > 0 && (
                    <div className="product-ingredients">
                      <label>原料:</label>
                      <ul>
                        {prod.ingredients.map((ing, idx) => (
                          <li key={idx}>
                            {ing.ingredient_name}: {ing.quantity} {ing.unit_abbreviation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="card-actions">
                    <button onClick={() => handleStartEditProduct(prod)} className="edit-btn">编辑</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminSetup;
