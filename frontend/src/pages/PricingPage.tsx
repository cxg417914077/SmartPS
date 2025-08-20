/* 请用以下完整内容替换该文件的所有内容 */

import { Link } from 'react-router-dom';
import './PageStyles.css';

export function PricingPage() {
  const tiers = [
    { name: "免费版", price: "¥0", features: ["每月 5 次编辑", "基础工具", "社区支持"] },
    { name: "专业版", price: "¥99/月", features: ["每月 100 次编辑", "所有高级工具", "邮件支持"], recommended: true },
    { name: "企业版", price: "联系我们", features: ["无限次编辑", "API 访问权限", "专属技术支持"] },
  ];

  return (
    <div className="page-container">
      <h1>价格方案</h1>
      <div className="card-grid">
        {tiers.map((tier) => (
          <div key={tier.name} className={`card ${tier.recommended ? 'recommended' : ''}`}>
            <h3>{tier.name}</h3>
            <p className="price">{tier.price}</p>
            <ul>
              {tier.features.map(f => <li key={f}>{f}</li>)}
            </ul>
            <Link to="/signup" className="cta-button">开始使用</Link>
          </div>
        ))}
      </div>
    </div>
  );
}