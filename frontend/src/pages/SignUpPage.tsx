/* 请用以下完整内容替换该文件的所有内容 */

import { Link } from 'react-router-dom';
import './PageStyles.css';

export function SignUpPage() {
  return (
    <div className="page-container form-container">
      <h2>创建账户</h2>
      <form>
        <input type="email" placeholder="电子邮箱地址" required />
        <input type="password" placeholder="密码" required />
        <button type="submit" className="cta-button">注册</button>
      </form>
      <p>已有账户？ <Link to="/login">立即登录</Link></p>
    </div>
  );
}