/**
 * Theme provider — light / dark / system, persisted via localStorage.
 * No external state lib; the tree is small enough to use context + a hook.
 */
import { createContext, useContext, useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"

type Theme = "light" | "dark" | "system"
type Effective = "light" | "dark"

const THEME_KEY = "uja:theme"

interface ThemeCtx {
  theme: Theme
  effective: Effective
  setTheme: (t: Theme) => void
}

const Ctx = createContext<ThemeCtx | null>(null)

function readStored(): Theme {
  try {
    const v = localStorage.getItem(THEME_KEY)
    if (v === "light" || v === "dark" || v === "system") return v
  } catch { /* ignore — privacy mode etc. */ }
  return "system"
}

function systemPrefersDark(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => readStored())
  const [systemDark, setSystemDark] = useState<boolean>(() => systemPrefersDark())

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)")
    const onChange = () => setSystemDark(mql.matches)
    mql.addEventListener("change", onChange)
    return () => mql.removeEventListener("change", onChange)
  }, [])

  const effective: Effective = theme === "system" ? (systemDark ? "dark" : "light") : theme

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle("dark", effective === "dark")
  }, [effective])

  const setTheme = (t: Theme) => {
    setThemeState(t)
    try { localStorage.setItem(THEME_KEY, t) } catch { /* ignore */ }
  }

  const value = useMemo(() => ({ theme, effective, setTheme }), [theme, effective])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useTheme(): ThemeCtx {
  const v = useContext(Ctx)
  if (!v) throw new Error("useTheme must be used within ThemeProvider")
  return v
}
