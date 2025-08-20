import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // --- 添加这个 resolve.dedupe 配置 ---
  resolve: {
    dedupe: ['react', 'react-dom'],
  },
})