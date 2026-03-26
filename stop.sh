#!/bin/bash

# 停止甜品店管理系统服务

echo "🛑 停止服务..."

# 读取 PID 文件
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null
    echo "✅ 后端服务已停止 (PID: $BACKEND_PID)"
    rm .backend.pid
else
    echo "⚠️  未找到后端 PID 文件"
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ 前端服务已停止 (PID: $FRONTEND_PID)"
    rm .frontend.pid
else
    echo "⚠️  未找到前端 PID 文件"
fi

# 清理可能残留的进程
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "✨ 所有服务已停止"
