#!/bin/bash

# 甜品店管理系统 - 快速启动脚本

echo "================================"
echo "甜品店管理系统 - 启动脚本"
echo "================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "🚀 启动后端服务..."
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境并启动后端
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 在后台启动 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID, 端口: 8000)"
echo "   日志文件: backend.log"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端开发服务器..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "⚠️  未找到 node_modules，正在安装依赖..."
    npm install
fi

# 启动前端开发服务器
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID, 端口: 5173)"

echo ""
echo "================================"
echo "✨ 启动完成！"
echo "================================"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "⚠️  停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 提示: 按 Ctrl+C 停止监控，但服务仍在后台运行"
echo ""

# 保存 PID 到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 等待用户中断
trap "echo ''; echo '⚠️  服务仍在后台运行，使用以下命令停止:'; echo '   kill $BACKEND_PID $FRONTEND_PID'; exit 0" INT

echo "📊 实时日志 (backend.log):"
tail -f backend.log
