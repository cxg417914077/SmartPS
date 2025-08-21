/* 请用以下完整内容替换该文件的所有内容 */

import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { FeaturesPage } from './pages/FeaturesPage';
import { PricingPage } from './pages/PricingPage';
import { LoginPage } from './pages/LoginPage';
import { SignUpPage } from './pages/SignUpPage';
import { AgentPage } from './pages/AgentPage';
import { ProtectedRoute } from './components/ProtectedRoute'; // 1. 导入我们的守卫组件
import './App.css';

function App() {
  return (
    <Routes>
      {/* 带有导航栏和页脚的公共页面 */}
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/pricing" element={<PricingPage />} />

        {/* --- 核心修改在这里 --- */}
        {/* 创建一个受保护的路由组 */}
        <Route element={<ProtectedRoute />}>
          <Route path="/agent" element={<AgentPage />} />
          {/* 如果未来有其他需要登录才能访问的页面，也放在这里 */}
        </Route>
      </Route>

      {/* 不使用通用布局的特殊页面 */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
    </Routes>
  );
}

export default App;