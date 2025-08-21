/* 请将以下完整内容创建并保存到该文件中 */

import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  // 检查用户是否已认证
  if (!isAuthenticated) {
    // 如果未认证，重定向到登录页面
    // `replace` 属性可以防止用户通过浏览器的“后退”按钮回到这个受保护的页面
    return <Navigate to="/login" replace />;
  }

  // 如果已认证，则渲染该路由下的子组件 (例如 AgentPage)
  return <Outlet />;
}