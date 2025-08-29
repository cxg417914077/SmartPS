/* 请用以下完整内容替换该文件的所有内容 */

import { useState, FormEvent, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CaptchaModal } from '../components/CaptchaModal';
import { API_BASE_URL } from '../config'; // 1. 导入基础 URL
import './PageStyles.css';

const RECAPTCHA_SITE_KEY = "6LfcArYrAAAAAIqlzFHhh2AyLpbec5UZvpa0oNt8"; // <--- 请务必替换为你的真实站点密钥

export function SignUpPage() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isSendingCode, setIsSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const [isCaptchaModalOpen, setIsCaptchaModalOpen] = useState(false);

  const auth = useAuth();

  useEffect(() => {
    let timer: number;
    if (countdown > 0) {
      timer = window.setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => window.clearTimeout(timer);
  }, [countdown]);

  const handleOpenCaptcha = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
      setError('请输入有效的电子邮箱地址。');
      return;
    }
    setError(null);
    setIsCaptchaModalOpen(true);
  };

  const handleCaptchaVerifyAndSendCode = async (captchaToken: string) => {
    setIsCaptchaModalOpen(false);
    setIsSendingCode(true);
    setError(null);

    try {
      // 2. 更新 fetch 请求地址
      const response = await fetch(`${API_BASE_URL}/api/send-verification-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, captchaToken }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || '发送验证码失败，请稍后重试。');
      }
      setCountdown(60);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSendingCode(false);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致！');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 3. 更新 fetch 请求地址
      const response = await fetch(`${API_BASE_URL}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || '注册失败，请稍后重试。');
      }

      if (data.token) {
        auth.login(data.token);
      } else {
        throw new Error('注册成功，但未收到认证信息。');
      }

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="auth-page-wrapper">
        <div className="form-container">
          <h1 className="auth-logo">智图魔方</h1>
          <h2>创建账户</h2>
          <form onSubmit={handleSubmit}>
            {error && <p className="error-message">{error}</p>}
            <div className="input-group">
              <input
                type="email"
                placeholder="电子邮箱地址"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
              <button
                type="button"
                onClick={handleOpenCaptcha}
                className="send-code-btn"
                disabled={isSendingCode || countdown > 0}
              >
                {isSendingCode ? '发送中...' : countdown > 0 ? `${countdown}s 后重试` : '发送验证码'}
              </button>
            </div>
            <input
              type="text"
              placeholder="邮箱验证码"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              autoComplete="one-time-code"
            />
            <input
              type="password"
              placeholder="设置密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <input
              type="password"
              placeholder="确认密码"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <button type="submit" className="cta-button" disabled={isLoading}>
              {isLoading ? '注册中...' : '注册'}
            </button>
          </form>
          <p>已有账户？ <Link to="/login">立即登录</Link></p>
        </div>
      </div>

      <CaptchaModal
        isOpen={isCaptchaModalOpen}
        onClose={() => setIsCaptchaModalOpen(false)}
        onVerify={handleCaptchaVerifyAndSendCode}
        siteKey={RECAPTCHA_SITE_KEY}
      />
    </>
  );
}