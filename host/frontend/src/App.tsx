import { useEffect, useState } from "react"
import { MessageSquare, FolderOpen, Settings as SettingsIcon, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { readLocal, writeLocal } from "@/lib/storage"
import { api } from "@/lib/api"
import type { HealthResponse } from "@/lib/api"
import { ChatTab } from "@/components/app/ChatTab"
import { MaterialsTab } from "@/components/app/MaterialsTab"
import { SettingsTab } from "@/components/app/SettingsTab"
import { Onboarding } from "@/components/app/Onboarding"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/lib/theme"

type TabId = "chat" | "materials" | "settings"
const TAB_KEY = "uja:active-tab"

const TABS: { id: TabId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "materials", label: "Materials", icon: FolderOpen },
  { id: "settings", label: "Settings", icon: SettingsIcon },
]

export function App() {
  const [active, setActive] = useState<TabId>(() => readLocal<TabId>(TAB_KEY, "chat"))
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthErr, setHealthErr] = useState<string | null>(null)

  useEffect(() => writeLocal(TAB_KEY, active), [active])

  useEffect(() => {
    let cancelled = false
    api.health()
      .then((h) => { if (!cancelled) { setHealth(h); setHealthErr(null) } })
      .catch((e) => { if (!cancelled) setHealthErr(String(e?.message ?? e)) })
    return () => { cancelled = true }
  }, [])

  // Global keyboard shortcut: cmd+1/2/3 to jump tabs.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.metaKey || e.ctrlKey)) return
      if (e.key === "1") { e.preventDefault(); setActive("chat") }
      else if (e.key === "2") { e.preventDefault(); setActive("materials") }
      else if (e.key === "3") { e.preventDefault(); setActive("settings") }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  const needsOnboarding = health !== null && !health.project_root_configured

  return (
    <div className="h-full flex flex-col bg-background text-foreground">
      <TopBar active={active} setActive={setActive} health={health} healthErr={healthErr} />
      <main className="flex-1 min-h-0 overflow-hidden">
        {needsOnboarding ? (
          <Onboarding onComplete={() => api.health().then(setHealth)} />
        ) : (
          <>
            {active === "chat" && <ChatTab />}
            {active === "materials" && <MaterialsTab />}
            {active === "settings" && <SettingsTab onConfigChanged={() => api.health().then(setHealth)} />}
          </>
        )}
      </main>
    </div>
  )
}

function TopBar({
  active, setActive, health, healthErr,
}: {
  active: TabId
  setActive: (t: TabId) => void
  health: HealthResponse | null
  healthErr: string | null
}) {
  const { effective, setTheme, theme } = useTheme()
  const cycleTheme = () => setTheme(theme === "system" ? "light" : theme === "light" ? "dark" : "system")

  return (
    <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/40">
      <div className="flex items-center gap-4 px-4 h-14">
        <a href="/" className="flex items-center gap-2 group" aria-label="Ultimate Job Assistant — home">
          <span aria-hidden className="inline-block w-7 h-7 rounded-md bg-brand-gradient" />
          <span className="font-semibold tracking-tight">
            Ultimate Job Assistant
            <span className="ml-2 text-xs font-mono text-muted-foreground">
              {health?.version ?? "—"}
            </span>
          </span>
        </a>
        <nav className="ml-4 flex items-center gap-1" role="tablist" aria-label="Primary navigation">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              role="tab"
              aria-selected={active === id}
              tabIndex={active === id ? 0 : -1}
              onClick={() => setActive(id)}
              className={cn(
                "h-9 px-3 inline-flex items-center gap-2 rounded-md text-sm transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                active === id && "bg-accent text-accent-foreground shadow-sm",
              )}
            >
              <Icon className="w-4 h-4" aria-hidden />
              <span>{label}</span>
              <kbd className="ml-1 hidden sm:inline-block text-[10px] text-muted-foreground font-mono">
                ⌘{id === "chat" ? "1" : id === "materials" ? "2" : "3"}
              </kbd>
            </button>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          {healthErr && (
            <span className="inline-flex items-center gap-1 text-xs text-destructive" role="alert">
              <AlertCircle className="w-3.5 h-3.5" aria-hidden />
              host unreachable
            </span>
          )}
          <Button variant="ghost" size="sm" onClick={cycleTheme} aria-label={`Theme: ${theme} (effective ${effective})`}>
            <span className="text-xs font-mono uppercase">{theme}</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
