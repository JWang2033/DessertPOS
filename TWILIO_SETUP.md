# Twilio SMS 集成配置指南

## ✅ 完成状态
已成功集成 Twilio SMS 服务！

## 📋 配置步骤

### 1. 注册 Twilio 账户
访问：https://www.twilio.com/try-twilio
- 注册免费试用账户（提供 $15 免费额度）
- 验证你的邮箱和手机号

### 2. 获取 Twilio 凭证
登录 Twilio Console：https://console.twilio.com/

获取以下信息：
- **Account SID**：在 Dashboard 首页可以看到
- **Auth Token**：在 Account SID 下方（点击"Show"显示）
- **Twilio Phone Number**：
  - 进入 Phone Numbers → Manage → Active numbers
  - 如果没有号码，点击 "Buy a number" 购买一个
  - 选择支持 SMS 的号码（试用账户可以免费获得一个）

### 3. 配置环境变量

创建 `.env` 文件（在项目根目录）：

```bash
# 复制示例文件
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Twilio 凭证：

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Environment (开发环境设置为 development)
ENVIRONMENT=development
```

### 4. 环境说明

**开发环境** (`ENVIRONMENT=development`):
- 不会发送真实短信
- 验证码会在 API 响应中返回（`debug_code` 字段）
- 验证码也会打印在后端控制台

**生产环境** (`ENVIRONMENT=production`):
- 发送真实短信到用户手机
- API 响应中不包含验证码
- 用户通过短信接收验证码

### 5. 重启后端服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
./venv/bin/uvicorn main:app --reload
```

## 🧪 测试

### 开发环境测试（不发送真实短信）
```bash
curl -X POST "http://localhost:8000/user/send-code" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+12025551234"}'

# 响应示例：
{
  "message": "Verification code sent (development mode)",
  "debug_code": "123456"
}
```

### 生产环境测试（发送真实短信）
1. 修改 `.env`：`ENVIRONMENT=production`
2. 重启服务
3. 使用 **已在 Twilio 验证的手机号**（试用账户限制）
4. 发送请求后，手机会收到真实短信

## ⚠️ 重要提示

### 试用账户限制
- 只能发送短信到**已验证的手机号**
- 需要在 Twilio Console 中验证接收短信的号码
- 路径：Phone Numbers → Manage → Verified Caller IDs

### 升级到付费账户
- 解除号码限制，可以发送到任何号码
- 价格：约 $0.0079/条短信（美国号码）
- 账户余额用完后需要充值

## 📊 费用预估
- 试用额度：$15（约可发送 1,900 条短信）
- 美国短信：$0.0079/条
- 月租（号码）：$1.15/月

## 🔧 故障排查

### 问题：后端启动失败
- 检查 `.env` 文件是否创建
- 检查环境变量格式是否正确

### 问题：发送短信失败
- 检查 TWILIO_ACCOUNT_SID 和 TWILIO_AUTH_TOKEN 是否正确
- 检查 TWILIO_PHONE_NUMBER 格式：+1XXXXXXXXXX
- 试用账户：确认接收号码已在 Twilio 验证

### 问题：收不到短信
- 检查手机号格式：必须是 +1XXXXXXXXXX
- 检查 Twilio Console 的 SMS Logs
- 确认 Twilio 账户余额充足

## 📝 代码说明

已修改的文件：
- ✅ `backend/utils/sms_service.py` - SMS 服务封装
- ✅ `backend/config.py` - 配置管理
- ✅ `backend/routers/user_router.py` - 集成 SMS 服务
- ✅ `requirements.txt` - 添加 Twilio 依赖
- ✅ `.env.example` - 配置模板

## 🚀 下一步

1. 注册 Twilio 账户
2. 获取凭证并填入 `.env` 文件
3. 重启后端服务
4. 测试发送验证码功能
5. 如果一切正常，可以将 `ENVIRONMENT` 改为 `production` 启用真实短信
