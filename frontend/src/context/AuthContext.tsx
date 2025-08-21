/* 请将以下完整内容创建并保存到该文件中 */

import { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// 定义 Context 中共享的数据结构
interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  login: (jwtToken: string) => void;
  logout: () => void;
}

// 创建 Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 创建一个 Provider 组件
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const navigate = useNavigate();

  // 当应用加载时，检查本地存储中是否已有 token
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = (jwtToken: string) => {
    localStorage.setItem('authToken', jwtToken);
    setToken(jwtToken);
    navigate('/agent'); // 登录后跳转到应用页面
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    navigate('/login'); // 登出后跳转到登录页面
  };

  const value = {
    isAuthenticated: !!token,
    token,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 创建一个自定义 Hook，方便在其他组件中使用
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}