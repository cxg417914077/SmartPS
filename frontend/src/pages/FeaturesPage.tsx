/* 请用以下完整内容替换该文件的所有内容 */

import './PageStyles.css';

export function FeaturesPage() {
  const features = [
    { title: "AI 智能移除", description: "从您的照片中无缝擦除不想要的物体。" },
    { title: "背景替换", description: "用一句文本指令，更换任何图像的背景。" },
    { title: "智能缩放与裁剪", description: "智能地裁剪和调整图像大小，以适应任何格式。" },
    { title: "色彩校正", description: "自动调整色彩、亮度、对比度，让画面更生动。" },
  ];

  return (
    <div className="page-container">
      <h1>功能介绍</h1>
      <div className="card-grid">
        {features.map((feature, index) => (
          <div key={index} className="card">
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}