// 这是 src/App.tsx 文件现在应该有的【全新】内容
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { FeaturesPage } from './pages/FeaturesPage';
import { PricingPage } from './pages/PricingPage';
import { LoginPage } from './pages/LoginPage';
import { SignUpPage } from './pages/SignUpPage';
import { AgentPage } from './pages/AgentPage';
import './App.css'; // 引入全局样式

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 使用通用布局的页面 */}
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/agent" element={<AgentPage />} />
        </Route>

        {/* 不使用通用布局的特殊页面 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;