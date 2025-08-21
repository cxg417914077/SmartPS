/* 请用以下完整内容替换该文件的所有内容 */

import { Link } from 'react-router-dom';
import './PageStyles.css';

export function HomePage() {
  return (
    // 添加一个新的 'hero-wrapper' 用于承载背景效果
    <div className="hero-wrapper">
      {/* 添加背景的装饰性形状 */}
      <div className="background-shape shape1"></div>
      <div className="background-shape shape2"></div>

      <div className="page-container hero-section">
        <h1 className="animate-fade-in-down">AI 赋能图像编辑，重塑你的想象</h1>
        <p className="animate-fade-in-up delay-1">
          通过简单的文本指令，自动化完成复杂的图像编辑。让我们的智能体为您处理繁重的工作。
        </p>
        <div className="animate-fade-in-up delay-2">
          <Link to="/agent" className="cta-button">
            立即体验
          </Link>
        </div>
      </div>
    </div>
  );
}