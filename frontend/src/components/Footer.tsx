/* 请用以下完整内容替换该文件的所有内容 */

import './Footer.css';

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>&copy; {new Date().getFullYear()} 智图魔方. 版权所有.</p>
        <div className="footer-links">
          <a href="#">服务条款</a>
          <a href="#">隐私政策</a>
        </div>
      </div>
    </footer>
  );
}