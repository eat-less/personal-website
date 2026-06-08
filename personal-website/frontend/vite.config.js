import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://127.0.0.1:8000"
    },
    fs: {
      strict: false,
      allow: ["C:/Users/冯家宝/Documents/Codex/2026-06-08/files-mentioned-by-the-user-a3f9a59c9cb3a465e99ea00ec38e71eb/personal-website"]
    }
  }
})