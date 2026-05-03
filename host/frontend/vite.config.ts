import path from "node:path"
import { defineConfig, loadEnv } from "vite"
import react from "@vitejs/plugin-react"

// During `vite dev` the FastAPI host runs on a random ephemeral port.
// Set VITE_API_PORT in .env.local (or your shell) to point the proxy at it.
// Default is 8741 — also used by start-uja.sh in production launches.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const apiPort = env.VITE_API_PORT || "8741"
  const apiHost = env.VITE_API_HOST || "127.0.0.1"
  const apiTarget = `http://${apiHost}:${apiPort}`

  return {
    plugins: [react()],
    resolve: {
      alias: { "@": path.resolve(__dirname, "./src") },
    },
    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: false,
          ws: false,
          configure: (proxy) => {
            proxy.on("error", (err) => {
              // Helps when FastAPI isn't running yet — keeps the dev server alive.
              console.warn("[vite proxy] /api -> " + apiTarget + " unreachable:", err.message)
            })
          },
        },
      },
    },
    build: {
      outDir: "dist",
      sourcemap: false,
      // Phase 17 acceptance gate: bundle < 500 KB gz. We code-split the heavy
      // preview libs (PDF.js, mammoth) by route below.
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              if (id.includes("react") || id.includes("scheduler")) return "react"
              if (id.includes("@radix-ui")) return "radix"
              if (id.includes("mammoth")) return "preview-docx"
              if (id.includes("marked") || id.includes("dompurify")) return "preview-md"
            }
          },
        },
      },
    },
  }
})
