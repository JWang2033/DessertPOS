import { useState } from 'react';
import { sendVerificationCode, login } from '../services/api';

export default function Login({ onLoginSuccess }) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1); // 1: 输入手机号, 2: 输入验证码
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(0);

  const handleSendCode = async (e) => {
    e.preventDefault();
    setError('');

    if (!/^\d{10}$/.test(phoneNumber)) {
      setError('请输入10位电话号码');
      return;
    }

    setLoading(true);
    try {
      const fullPhone = `+1${phoneNumber}`;
      const response = await sendVerificationCode(fullPhone);
      console.log('验证码（开发环境）:', response.data.debug_code);
      alert(`验证码：${response.data.debug_code}`); // 开发环境显示验证码
      setStep(2);
      setCountdown(60);

      // 倒计时
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.detail || '发送验证码失败');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    if (!code || code.length !== 6) {
      setError('请输入6位验证码');
      return;
    }

    setLoading(true);
    try {
      const fullPhone = `+1${phoneNumber}`;
      const response = await login(fullPhone, code);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      onLoginSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          🍰 DessertPOS
        </h1>
        <p className="text-center text-gray-600 mb-8">欢迎回来</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleSendCode}>
            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                电话号码
              </label>
              <div className="flex items-center border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-primary">
                <span className="px-4 py-3 bg-gray-100 text-gray-700 font-semibold border-r">
                  +1
                </span>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '').slice(0, 10);
                    setPhoneNumber(value);
                  }}
                  placeholder="输入10位电话号码"
                  className="flex-1 px-4 py-3 outline-none rounded-r-lg"
                  required
                  maxLength="10"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400"
            >
              {loading ? '发送中...' : '获取验证码'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label className="block text-gray-700 font-semibold mb-2">
                电话号码
              </label>
              <div className="text-gray-600 py-2">+1 {phoneNumber}</div>
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                验证码
              </label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                placeholder="请输入6位验证码"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                maxLength={6}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors disabled:bg-gray-400 mb-3"
            >
              {loading ? '登录中...' : '登录'}
            </button>
            <button
              type="button"
              onClick={() => setStep(1)}
              disabled={countdown > 0}
              className="w-full bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors disabled:bg-gray-100"
            >
              {countdown > 0 ? `${countdown}秒后重新获取` : '重新获取验证码'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
