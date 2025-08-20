/* 请用以下完整内容替换该文件的所有内容 */

import { Link, NavLink } from 'react-router-dom';
import './Navbar.css';

export function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          智图魔方
        </Link>
        <div className="nav-menu">
          <NavLink to="/features" className="nav-link">功能介绍</NavLink>
          <NavLink to="/pricing" className="nav-link">价格方案</NavLink>
          <NavLink to="/agent" className="nav-link">在线体验</NavLink>
        </div>
        <div className="nav-auth">
          <Link to="/login" className="nav-button login">登录</Link>
          <Link to="/signup" className="nav-button signup">注册</Link>
        </div>
      </div>
    </nav>
  );
}