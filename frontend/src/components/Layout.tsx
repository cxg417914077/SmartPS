import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

export function Layout() {
  return (
    <>
      <Navbar />
      <main className="main-content">
        <Outlet /> {/* 子页面会在这里渲染 */}
      </main>
      <Footer />
    </>
  );
}