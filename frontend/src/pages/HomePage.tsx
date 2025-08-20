/* 请用以下完整内容替换该文件的所有内容 */

import { Link } from 'react-router-dom';
import './PageStyles.css';

export function HomePage() {
  return (
    <div className="page-container hero-section">
      <h1>AI 赋能图像编辑，重塑你的想象</h1>
      <p>通过简单的文本指令，自动化完成复杂的图像编辑。让我们的智能体为您处理繁重的工作。</p>
      <Link to="/agent" className="cta-button">立即体验</Link>
    </div>
  );
}