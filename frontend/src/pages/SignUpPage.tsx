/* 请用以下完整内容替换该文件的所有内容 */

import { useState, FormEvent, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { CaptchaModal } from '../components/CaptchaModal'; // 1. 导入模态框组件
import './PageStyles.css';

// 2. 将你的 reCAPTCHA 站点密钥放在这里
// 强烈建议: 在实际项目中，应将此密钥存储在 .env 文件中
const RECAPTCHA_SITE_KEY = "6Levxq0rAAAAAOv2YrOyLx4PfNtCntmxXcdaaLeF";

export function SignUpPage() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isSendingCode, setIsSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // --- 新增状态：控制模态框的显示与隐藏 ---
  const [isCaptchaModalOpen, setIsCaptchaModalOpen] = useState(false);

  const auth = useAuth();

  useEffect(() => {
    let timer: number;
    if (countdown > 0) {
      timer = window.setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => window.clearTimeout(timer);
  }, [countdown]);

  // --- 步骤 3: 修改 handleSendCode，让它只打开模态框 ---
  const handleOpenCaptcha = () => {
    if (!email) {
      setError('请输入有效的电子邮箱地址。');
      return;
    }
    setError(null);
    setIsCaptchaModalOpen(true);
  };

  // --- 步骤 4: 创建一个新的函数，在人机验证成功后被调用 ---
  const handleCaptchaVerifyAndSendCode = async (captchaToken: string) => {
    setIsCaptchaModalOpen(false); // 关闭模态框
    setIsSendingCode(true);

    try {
      const response = await fetch('/api/send-verification-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // 将邮箱和 reCAPTCHA token 一起发送给后端
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
    // ... (注册逻辑保持不变) ...
  };

  return (
    <> {/* 使用 Fragment 包裹 */}
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
                onClick={handleOpenCaptcha} // 5. 按钮现在调用打开模态框的函数
                className="send-code-btn"
                disabled={isSendingCode || countdown > 0}
              >
                {isSendingCode ? '发送中...' : countdown > 0 ? `${countdown}s 后重试` : '发送验证码'}
              </button>
            </div>
            {/* ... (其他输入框保持不变) ... */}
            <input type="text" placeholder="邮箱验证码" value={code} onChange={(e) => setCode(e.target.value)} required autoComplete="one-time-code" />
            <input type="password" placeholder="设置密码" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password" />
            <input type="password" placeholder="确认密码" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required autoComplete="new-password" />
            <button type="submit" className="cta-button" disabled={isLoading}>
              {isLoading ? '注册中...' : '注册'}
            </button>
          </form>
          <p>已有账户？ <Link to="/login">立即登录</Link></p>
        </div>
      </div>

      {/* 6. 在页面上渲染模态框组件 */}
      <CaptchaModal
        isOpen={isCaptchaModalOpen}
        onClose={() => setIsCaptchaModalOpen(false)}
        onVerify={handleCaptchaVerifyAndSendCode}
        siteKey={RECAPTCHA_SITE_KEY}
      />
    </>
  );
}