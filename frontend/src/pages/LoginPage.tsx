/* 请用以下完整内容替换该文件的所有内容 */

import { Link } from 'react-router-dom';
import './PageStyles.css';

export function LoginPage() {
  return (
    <div className="page-container form-container">
      <h2>登录</h2>
      <form>
        <input type="email" placeholder="电子邮箱地址" required />
        <input type="password" placeholder="密码" required />
        <button type="submit" className="cta-button">登录</button>
      </form>
      <p>还没有账户？ <Link to="/signup">立即注册</Link></p>
    </div>
  );
}