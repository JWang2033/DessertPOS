# DessertPOS 前端启动指南

## 🎉 项目已创建完成！

前端使用 React + Vite + TailwindCSS 构建。

## 📦 已完成的工作

✅ 项目结构创建
✅ 所有依赖安装
✅ 所有组件创建
- Login.jsx - 手机验证码登录
- MenuList.jsx - 菜单浏览
- ProductDetail.jsx - 商品详情
- Cart.jsx - 购物车管理
- OrderSuccess.jsx - 订单成功提示

✅ API 服务配置
✅ TailwindCSS 样式配置
✅ Vite 代理配置（指向后端 8000 端口）

## 🚀 启动步骤

### 1. 启动后端服务（如果还没启动）

```bash
cd /Users/yizhouwang/Desktop/DessertPOS
source venv/bin/activate
./venv/bin/uvicorn main:app --reload
```

后端运行在：`http://localhost:8000`

### 2. 启动前端服务（已启动）

```bash
cd /Users/yizhouwang/Desktop/DessertPOS/frontend
npm run dev
```

前端运行在：`http://localhost:3000`

## 🌐 访问应用

打开浏览器访问：**http://localhost:3000**

## 📱 使用流程

1. **登录**
   - 输入手机号（例如：13800138000）
   - 点击"获取验证码"
   - 开发环境会弹出 alert 显示验证码
   - 输入验证码登录

2. **浏览菜单**
   - 查看所有商品
   - 点击分类标签筛选
   - 点击商品卡片查看详情

3. **添加商品**
   - 在商品详情中选择配料（如果有）
   - 调整数量
   - 点击"加入购物车"

4. **查看购物车**
   - 点击右上角"购物车"按钮
   - 修改商品数量
   - 删除不需要的商品
   - 查看总价

5. **结算**
   - 在购物车中点击"结算"按钮
   - 查看订单详情
   - 订单创建成功！

## 🛠️ 技术栈

- **React 19** - UI 框架
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **Axios** - HTTP 客户端
- **LocalStorage** - Token 存储

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/         # 所有 React 组件
│   ├── services/
│   │   └── api.js         # API 调用封装
│   ├── App.jsx            # 主应用组件
│   ├── main.jsx           # 入口文件
│   └── index.css          # Tailwind 样式
├── index.html
├── vite.config.js         # Vite 配置（含代理）
├── tailwind.config.js
└── package.json
```

## 🔧 开发命令

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```

## ⚙️ 配置说明

### API 代理

在 `vite.config.js` 中配置：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

所有 `/api/*` 请求会自动代理到后端 `http://localhost:8000`

### Token 存储

登录后 JWT token 自动保存在 `localStorage`：
- Key: `token`
- 用于所有需要认证的 API 请求

### 购物车过期

购物车数据存储在 Redis，2小时后自动过期。

## 🎨 样式定制

在 `tailwind.config.js` 中定制主题：

```javascript
theme: {
  extend: {
    colors: {
      primary: '#3B82F6',    // 主色调（蓝色）
      secondary: '#10B981',  // 次要色（绿色）
    }
  },
}
```

## 📝 注意事项

1. 确保后端服务在 8000 端口运行
2. 确保 MySQL 和 Redis 服务已启动
3. 手机号格式：1开头的11位数字
4. 验证码长度：6位数字

## 🐛 常见问题

### 1. 无法连接后端

检查后端是否启动：
```bash
curl http://localhost:8000/
```

### 2. 样式没有加载

检查 TailwindCSS 配置，确保已安装依赖：
```bash
npm install -D tailwindcss postcss autoprefixer
```

### 3. API 请求失败

检查浏览器控制台 Network 标签，查看具体错误信息。

## 🎯 下一步

- ✨ 添加更多动画效果
- 🔍 添加商品搜索功能
- 📦 添加订单历史查看
- 💳 集成支付功能
- 🎨 优化移动端适配

---

**祝使用愉快！** 🎉
