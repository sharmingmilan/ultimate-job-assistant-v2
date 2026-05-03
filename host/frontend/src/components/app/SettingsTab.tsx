/**
 * Settings tab — app behavior.
 *
 * Per ADR §D10, the Settings tab is the canonical app-config surface
 * (project root, API key, theme, etc.). The richer memory.md / tracker.md
 * editors live in Materials. Phase 17 ships the load-bearing Settings
 * controls; the rest grow into this tab in later phases.
 *
 * The API key field is write-only on purpose. The OS keychain is the
 * source of truth (D8); we render presence + a "Replace" affordance and
 * NEVER read the key back from the server.
 */
import { useCallback, useEffect, useState } from "react"
import { Loader2, KeyRound, FolderOpen, Trash2, RefreshCw, MessageSquare, Info, AlertCircle, CheckCircle2 } from "lucide-react"
import { api, ApiError } from "@/lib/api"
import type { ConfigResponse, KeyStatusResponse, ConversationSummary, HealthResponse } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { useTheme } from "@/lib/theme"

interface FlashMsg { kind: "ok" | "err"; text: string }

export function SettingsTab({ onConfigChanged }: { onConfigChanged?: () => void }) {
  return (
    <div className="h-full overflow-auto">
      <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 space-y-6">
        <h1 className="text-xl font-semibold tracking-tight">Settings</h1>
        <ProjectRootCard onChanged={onConfigChanged} />
        <ApiKeyCard />
        <ThemeCard />
        <ConversationsCard />
        <AboutCard />
      </div>
    </div>
  )
}

/* ---------- project root ---------- */

function ProjectRootCard({ onChanged }: { onChanged?: () => void }) {
  const [cfg, setCfg] = useState<ConfigResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [draft, setDraft] = useState("")
  const [flash, setFlash] = useState<FlashMsg | null>(null)

  const refresh = useCallback(async () => {
    try {
      const r = await api.getConfig()
      setCfg(r)
      setDraft(r.project_root ?? "")
    } catch (e) {
      setFlash({ kind: "err", text: e instanceof Error ? e.message : String(e) })
    }
  }, [])

  useEffect(() => { refresh() }, [refresh])

  async function save() {
    setBusy(true); setFlash(null)
    try {
      const r = await api.setProjectRoot(draft.trim())
      setCfg(r)
      setFlash({ kind: "ok", text: "Project root saved." })
      onChanged?.()
    } catch (e) {
      setFlash({ kind: "err", text: e instanceof ApiError ? String(e.detail) : String(e) })
    } finally { setBusy(false) }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><FolderOpen className="w-4 h-4" /> Project root</CardTitle>
        <CardDescription>
          The folder the host can read and write inside. All file tools are sandboxed to this path.
          Changing it does not yet trigger a server restart in Phase 17 — relaunch the host after a change.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <Label htmlFor="root">Absolute path</Label>
          <Input id="root" value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="/Users/you/Documents/Ultimate Job Assistant" />
        </div>
        {cfg && (
          <p className="text-xs text-muted-foreground">
            Schema version <span className="font-mono">{cfg.schema_version}</span>.
            Currently set to: <span className="font-mono">{cfg.project_root ?? "(not configured)"}</span>
          </p>
        )}
        {flash && <FlashAlert flash={flash} />}
        <div className="flex justify-end">
          <Button onClick={save} disabled={busy || !draft.trim() || draft.trim() === cfg?.project_root}>
            {busy && <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden />}
            Save
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

/* ---------- API key ---------- */

function ApiKeyCard() {
  const [status, setStatus] = useState<KeyStatusResponse | null>(null)
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [flash, setFlash] = useState<FlashMsg | null>(null)
  const [editing, setEditing] = useState(false)

  const refresh = useCallback(async () => {
    try { setStatus(await api.getKeyStatus()) }
    catch (e) { setFlash({ kind: "err", text: e instanceof Error ? e.message : String(e) }) }
  }, [])

  useEffect(() => { refresh() }, [refresh])

  async function save() {
    setBusy(true); setFlash(null)
    try {
      await api.setKey(draft.trim(), true)
      setFlash({ kind: "ok", text: "Key saved to OS keychain and verified." })
      setDraft("")
      setEditing(false)
      await refresh()
    } catch (e) {
      setFlash({ kind: "err", text: e instanceof ApiError ? String(e.detail) : String(e) })
    } finally { setBusy(false) }
  }

  async function clear() {
    setBusy(true); setFlash(null)
    try {
      await api.deleteKey()
      setFlash({ kind: "ok", text: "Key removed from keychain." })
      await refresh()
    } catch (e) {
      setFlash({ kind: "err", text: e instanceof Error ? e.message : String(e) })
    } finally { setBusy(false) }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><KeyRound className="w-4 h-4" /> Anthropic API key</CardTitle>
        <CardDescription>
          The key never leaves your machine. The host stores only a pointer to your OS keychain entry —
          we never read the secret back into the UI.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="text-sm flex items-center gap-3">
          {status === null ? (
            <span className="text-muted-foreground inline-flex items-center"><Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" aria-hidden /> Checking…</span>
          ) : status.has_key ? (
            <span className="inline-flex items-center text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="w-4 h-4 mr-1.5" aria-hidden /> Key configured
              {status.using_memory_fallback && (
                <span className="ml-2 text-xs text-amber-600 dark:text-amber-400">
                  (in-memory fallback — keychain unavailable; key won't persist after restart)
                </span>
              )}
            </span>
          ) : (
            <span className="inline-flex items-center text-amber-600 dark:text-amber-400">
              <AlertCircle className="w-4 h-4 mr-1.5" aria-hidden /> No key set
            </span>
          )}
        </div>

        {(editing || !status?.has_key) && (
          <div className="space-y-2">
            <Label htmlFor="key">Paste a new key</Label>
            <Input
              id="key"
              type="password"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="sk-ant-..."
              autoComplete="off"
            />
          </div>
        )}

        {flash && <FlashAlert flash={flash} />}

        <div className="flex justify-end gap-2">
          {status?.has_key && !editing && (
            <>
              <Button variant="outline" onClick={() => setEditing(true)} disabled={busy}>Replace key</Button>
              <Button variant="destructive" onClick={clear} disabled={busy}>
                <Trash2 className="w-4 h-4 mr-1.5" aria-hidden /> Clear key
              </Button>
            </>
          )}
          {editing && (
            <Button variant="ghost" onClick={() => { setEditing(false); setDraft(""); setFlash(null) }} disabled={busy}>
              Cancel
            </Button>
          )}
          {(editing || !status?.has_key) && (
            <Button onClick={save} disabled={busy || draft.trim().length < 10}>
              {busy && <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden />}
              Save and test
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

/* ---------- theme ---------- */

function ThemeCard() {
  const { theme, effective, setTheme } = useTheme()
  const opts: { id: "system" | "light" | "dark"; label: string }[] = [
    { id: "system", label: "Match system" },
    { id: "light", label: "Light" },
    { id: "dark", label: "Dark" },
  ]
  return (
    <Card>
      <CardHeader>
        <CardTitle>Appearance</CardTitle>
        <CardDescription>
          Theme is remembered locally in this browser — the host doesn't sync it across devices.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div role="radiogroup" aria-label="Theme" className="flex gap-2">
          {opts.map((o) => (
            <button
              key={o.id}
              role="radio"
              aria-checked={theme === o.id}
              onClick={() => setTheme(o.id)}
              className={[
                "h-9 px-3 rounded-md border text-sm transition-colors",
                theme === o.id
                  ? "bg-accent text-accent-foreground border-brand-sky/40"
                  : "bg-card hover:bg-accent/30",
              ].join(" ")}
            >
              {o.label}
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          Currently rendering as <span className="font-mono">{effective}</span>.
        </p>
      </CardContent>
    </Card>
  )
}

/* ---------- conversations ---------- */

function ConversationsCard() {
  const [convs, setConvs] = useState<ConversationSummary[] | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<string | null>(null)

  const load = useCallback(async () => {
    setErr(null)
    try {
      const r = await api.listConversations()
      setConvs(r.conversations)
    } catch (e) {
      setErr(e instanceof ApiError ? String(e.detail) : String(e))
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function del(id: string) {
    if (!confirm("Delete this conversation? This also removes its messages, tool history, and any pending changes.")) return
    setBusyId(id); setErr(null)
    try {
      const r = await fetch(`/api/conversations/${encodeURIComponent(id)}`, { method: "DELETE" })
      if (!r.ok) {
        let detail: unknown = r.statusText
        try { detail = (await r.json()).detail } catch { /* ignore */ }
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail))
      }
      await load()
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e))
    } finally { setBusyId(null) }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><MessageSquare className="w-4 h-4" /> Conversations</CardTitle>
        <CardDescription>
          Stored in <span className="font-mono">.uja/state.db</span> at the project root. Delete cascades
          to messages, tool invocations, and pending change-sets.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {err && (
          <Alert variant="destructive" role="alert">
            <AlertCircle className="w-4 h-4" aria-hidden />
            <AlertTitle>Couldn't load</AlertTitle>
            <AlertDescription>{err}</AlertDescription>
          </Alert>
        )}
        <div className="flex justify-end">
          <Button size="sm" variant="ghost" onClick={load}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" aria-hidden /> Refresh
          </Button>
        </div>
        {convs === null ? (
          <ListSkeleton />
        ) : convs.length === 0 ? (
          <p className="text-sm text-muted-foreground py-2">No conversations yet.</p>
        ) : (
          <ul className="divide-y border rounded-md">
            {convs.map((c) => (
              <li key={c.id} className="px-3 py-2 flex items-center gap-3 text-sm">
                <span className="flex-1 min-w-0">
                  <span className="block truncate">{c.title || "(untitled)"}</span>
                  <span className="block text-[11px] text-muted-foreground font-mono truncate">{c.id}</span>
                </span>
                <Button
                  size="sm" variant="ghost"
                  onClick={() => del(c.id)}
                  disabled={busyId === c.id}
                  aria-label={`Delete conversation ${c.title || c.id}`}
                >
                  {busyId === c.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden /> : <Trash2 className="w-3.5 h-3.5 text-destructive" aria-hidden />}
                </Button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}

function ListSkeleton() {
  return (
    <ul className="space-y-1.5" aria-busy="true">
      {Array.from({ length: 4 }).map((_, i) => (
        <li key={i} className="h-10 rounded-md bg-muted/40 animate-pulse" />
      ))}
    </ul>
  )
}

/* ---------- about ---------- */

function AboutCard() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [cfg, setCfg] = useState<ConfigResponse | null>(null)
  useEffect(() => {
    api.health().then(setHealth).catch(() => { /* surfaced in TopBar */ })
    api.getConfig().then(setCfg).catch(() => { /* surfaced above */ })
  }, [])
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Info className="w-4 h-4" /> About</CardTitle>
      </CardHeader>
      <CardContent className="text-sm space-y-1">
        <Row k="Host version" v={health?.version ?? "—"} />
        <Row k="DB schema version" v={cfg?.schema_version ?? "—"} />
        <Row k="Project root" v={cfg?.project_root ?? "(not configured)"} mono />
        <Separator className="my-2" />
        <p className="text-xs text-muted-foreground">
          Ultimate Job Assistant runs locally. Network bind defaults to <span className="font-mono">127.0.0.1</span>.
        </p>
      </CardContent>
    </Card>
  )
}

function Row({ k, v, mono }: { k: string; v: string | number; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-muted-foreground">{k}</span>
      <span className={["text-right truncate", mono ? "font-mono text-xs" : ""].join(" ")}>{String(v)}</span>
    </div>
  )
}

function FlashAlert({ flash }: { flash: FlashMsg }) {
  if (flash.kind === "ok") {
    return (
      <Alert role="status" className="border-emerald-500/30">
        <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" aria-hidden />
        <AlertTitle className="text-emerald-700 dark:text-emerald-300">Saved</AlertTitle>
        <AlertDescription className="break-words">{flash.text}</AlertDescription>
      </Alert>
    )
  }
  return (
    <Alert variant="destructive" role="alert">
      <AlertCircle className="w-4 h-4" aria-hidden />
      <AlertTitle>That didn't work</AlertTitle>
      <AlertDescription className="break-words">{flash.text}</AlertDescription>
    </Alert>
  )
}
