"""
SMS Service using Twilio
发送短信验证码服务
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, ENVIRONMENT


class SMSService:
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_PHONE_NUMBER
        self.client = None

        # 只在生产环境或配置了凭证时初始化 Twilio 客户端
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"Twilio 客户端初始化失败: {e}")

    def send_verification_code(self, phone_number: str, code: str) -> dict:
        """
        发送验证码短信

        Args:
            phone_number: 电话号码，格式：+1XXXXXXXXXX
            code: 6位验证码

        Returns:
            dict: {"success": bool, "message": str, "debug_code": str (仅开发环境)}
        """
        # 开发环境：不发送真实短信，直接返回验证码
        if ENVIRONMENT == "development" or not self.client:
            print(f"[开发模式] 验证码发送到 {phone_number}: {code}")
            return {
                "success": True,
                "message": "Verification code sent (development mode)",
                "debug_code": code  # 开发环境返回验证码
            }

        # 生产环境：发送真实短信
        try:
            message = self.client.messages.create(
                body=f"Your DessertPOS verification code is: {code}. Valid for 5 minutes.",
                from_=self.from_number,
                to=phone_number
            )

            return {
                "success": True,
                "message": "Verification code sent successfully",
                "sid": message.sid  # Twilio 消息ID
            }

        except TwilioRestException as e:
            print(f"Twilio 发送失败: {e}")
            return {
                "success": False,
                "message": f"Failed to send SMS: {e.msg}"
            }
        except Exception as e:
            print(f"发送短信时发生错误: {e}")
            return {
                "success": False,
                "message": "Failed to send SMS due to server error"
            }


# 创建全局实例
sms_service = SMSService()
