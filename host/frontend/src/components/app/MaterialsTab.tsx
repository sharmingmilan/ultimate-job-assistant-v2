/**
 * Materials tab — read-only file browser scoped to the project root.
 *
 *  left:  collapsible tree view; lazy-fetches children when a folder opens
 *  right: previewer; format chosen by file extension
 *
 * Per ADR §D4, all rendering is client-side. The backend ships raw bytes
 * for binary previews (PDF, DOCX) and decoded UTF-8 text for everything
 * else. mammoth and PDF.js stay deferred imports — they are NOT loaded
 * until the user actually opens a matching file (keeps initial bundle
 * lean per the Phase 17 acceptance gate).
 */
import { useCallback, useEffect, useMemo, useState } from "react"
import { ChevronDown, ChevronRight, Folder, File as FileIcon, AlertCircle, Loader2, RefreshCw } from "lucide-react"
import { ApiError } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { marked } from "marked"
import DOMPurify from "dompurify"

interface Entry {
  name: string
  type: "dir" | "file"
  size_bytes: number | null
}

interface DirCache {
  loading: boolean
  error: string | null
  entries: Entry[] | null
}

const PATH_SEP = "/"

async function fetchTree(path: string): Promise<Entry[]> {
  const url = "/api/files/tree?path=" + encodeURIComponent(path)
  const r = await fetch(url)
  if (!r.ok) {
    let detail: unknown = r.statusText
    try { detail = (await r.json()).detail } catch { /* ignore */ }
    throw new ApiError(r.status, detail)
  }
  const j = await r.json() as { entries: Entry[] }
  return j.entries
}

export function MaterialsTab() {
  const [openDirs, setOpenDirs] = useState<Set<string>>(() => new Set(["."]))
  const [cache, setCache] = useState<Record<string, DirCache>>({})
  const [selected, setSelected] = useState<string | null>(null)

  const loadDir = useCallback(async (path: string) => {
    setCache((prev) => ({ ...prev, [path]: { loading: true, error: null, entries: prev[path]?.entries ?? null } }))
    try {
      const entries = await fetchTree(path)
      setCache((prev) => ({ ...prev, [path]: { loading: false, error: null, entries } }))
    } catch (e) {
      setCache((prev) => ({
        ...prev,
        [path]: { loading: false, error: e instanceof ApiError ? String(e.detail) : String(e), entries: prev[path]?.entries ?? null },
      }))
    }
  }, [])

  useEffect(() => { loadDir(".") }, [loadDir])

  const toggle = (path: string) => {
    setOpenDirs((prev) => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else { next.add(path); if (!cache[path]) loadDir(path) }
      return next
    })
  }

  return (
    <div className="h-full flex">
      <aside className="w-72 border-r flex flex-col bg-card/30">
        <div className="px-3 py-2 border-b flex items-center justify-between">
          <span className="text-xs uppercase tracking-wide text-muted-foreground font-medium">Project files</span>
          <Button size="sm" variant="ghost" className="h-7 px-2" onClick={() => loadDir(".")}>
            <RefreshCw className="w-3.5 h-3.5" aria-hidden />
          </Button>
        </div>
        <ScrollArea className="flex-1">
          <div className="py-1 text-sm">
            <TreeNode
              path="."
              displayName="(project root)"
              isRoot
              cache={cache}
              openDirs={openDirs}
              selected={selected}
              onToggle={toggle}
              onSelect={setSelected}
              onLoad={loadDir}
              depth={0}
            />
          </div>
        </ScrollArea>
      </aside>

      <section className="flex-1 min-w-0 flex flex-col">
        {selected ? (
          <Preview path={selected} />
        ) : (
          <EmptyMaterials />
        )}
      </section>
    </div>
  )
}

function TreeNode({
  path, displayName, isRoot,
  cache, openDirs, selected,
  onToggle, onSelect, onLoad,
  depth,
}: {
  path: string
  displayName: string
  isRoot?: boolean
  cache: Record<string, DirCache>
  openDirs: Set<string>
  selected: string | null
  onToggle: (path: string) => void
  onSelect: (path: string) => void
  onLoad: (path: string) => void
  depth: number
}) {
  const open = openDirs.has(path)
  const cur = cache[path]

  // For the root, render contents directly; for nested dirs, render a header row.
  return (
    <div>
      {!isRoot && (
        <button
          onClick={() => onToggle(path)}
          className={cn(
            "w-full flex items-center gap-1 px-2 py-1 hover:bg-accent/40 rounded-sm text-left",
          )}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          aria-expanded={open}
        >
          {open ? <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" aria-hidden /> : <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" aria-hidden />}
          <Folder className="w-3.5 h-3.5 text-brand-sky" aria-hidden />
          <span className="truncate">{displayName}</span>
        </button>
      )}
      {(open || isRoot) && (
        <DirContents
          path={path}
          cache={cache}
          openDirs={openDirs}
          selected={selected}
          onToggle={onToggle}
          onSelect={onSelect}
          onLoad={onLoad}
          depth={isRoot ? 0 : depth + 1}
          cur={cur}
        />
      )}
    </div>
  )
}

function DirContents({
  path, cache, openDirs, selected,
  onToggle, onSelect, onLoad,
  depth, cur,
}: {
  path: string
  cache: Record<string, DirCache>
  openDirs: Set<string>
  selected: string | null
  onToggle: (path: string) => void
  onSelect: (path: string) => void
  onLoad: (path: string) => void
  depth: number
  cur: DirCache | undefined
}) {
  if (!cur || (cur.loading && !cur.entries)) {
    return (
      <div className="px-2 py-1 text-xs text-muted-foreground" style={{ paddingLeft: `${depth * 12 + 8}px` }}>
        <Loader2 className="w-3.5 h-3.5 inline animate-spin mr-1" aria-hidden /> Loading…
      </div>
    )
  }
  if (cur.error) {
    return (
      <div className="px-2 py-1 text-xs text-destructive" style={{ paddingLeft: `${depth * 12 + 8}px` }}>
        <AlertCircle className="w-3.5 h-3.5 inline mr-1" aria-hidden /> {cur.error}
      </div>
    )
  }
  if (!cur.entries || cur.entries.length === 0) {
    return (
      <div className="px-2 py-1 text-xs text-muted-foreground" style={{ paddingLeft: `${depth * 12 + 8}px` }}>(empty)</div>
    )
  }
  return (
    <ul>
      {cur.entries.map((e) => {
        const childPath = path === "." ? e.name : `${path}${PATH_SEP}${e.name}`
        if (e.type === "dir") {
          return (
            <li key={childPath}>
              <TreeNode
                path={childPath}
                displayName={e.name}
                cache={cache}
                openDirs={openDirs}
                selected={selected}
                onToggle={onToggle}
                onSelect={onSelect}
                onLoad={onLoad}
                depth={depth}
              />
            </li>
          )
        }
        return (
          <li key={childPath}>
            <button
              onClick={() => onSelect(childPath)}
              className={cn(
                "w-full flex items-center gap-1 px-2 py-1 hover:bg-accent/40 rounded-sm text-left",
                selected === childPath && "bg-accent text-accent-foreground",
              )}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
            >
              <span className="w-3.5" />
              <FileIcon className="w-3.5 h-3.5 text-muted-foreground" aria-hidden />
              <span className="truncate flex-1">{e.name}</span>
              {e.size_bytes != null && (
                <span className="text-[10px] text-muted-foreground tabular-nums ml-1">
                  {formatBytes(e.size_bytes)}
                </span>
              )}
            </button>
          </li>
        )
      })}
    </ul>
  )
}

function EmptyMaterials() {
  return (
    <div className="h-full flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-4 w-12 h-12 rounded-xl bg-brand-gradient" aria-hidden />
        <h2 className="text-lg font-semibold tracking-tight">Browse your materials</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Pick a file on the left to preview it. Markdown, DOCX, PDF, and code render in place — your text
          editor stays the source of truth for edits.
        </p>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ *
 * Preview pane — format-routed
 * ------------------------------------------------------------------ */

function Preview({ path }: { path: string }) {
  const ext = useMemo(() => path.split(".").pop()?.toLowerCase() ?? "", [path])

  return (
    <div className="h-full flex flex-col min-h-0">
      <div className="border-b px-4 py-2 flex items-center gap-2 bg-card/30">
        <FileIcon className="w-4 h-4 text-muted-foreground" aria-hidden />
        <span className="font-mono text-xs truncate">{path}</span>
        <span className="ml-auto text-[11px] text-muted-foreground uppercase">{ext || "—"}</span>
      </div>
      <div className="flex-1 min-h-0 overflow-auto">
        {ext === "md" || ext === "markdown" ? <MarkdownPreview path={path} />
          : ext === "docx" ? <DocxPreview path={path} />
          : ext === "pdf" ? <PdfPreview path={path} />
          : isTextish(ext) ? <TextPreview path={path} />
          : <BinaryPreview path={path} ext={ext} />}
      </div>
    </div>
  )
}

function MarkdownPreview({ path }: { path: string }) {
  const { state, body } = useTextFile(path)
  const html = useMemo(() => {
    if (!body) return ""
    const raw = marked.parse(body, { gfm: true, breaks: false, async: false }) as string
    return DOMPurify.sanitize(raw)
  }, [body])
  if (state === "loading") return <PreviewLoading />
  if (state === "error")   return <PreviewError message={body ?? "Unknown error"} />
  return (
    <article
      className="prose prose-sm dark:prose-invert max-w-3xl mx-auto p-6 prose-pre:bg-muted prose-pre:text-foreground"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

function TextPreview({ path }: { path: string }) {
  const { state, body } = useTextFile(path)
  if (state === "loading") return <PreviewLoading />
  if (state === "error")   return <PreviewError message={body ?? "Unknown error"} />
  return (
    <pre className="p-4 text-[13px] leading-relaxed font-mono whitespace-pre-wrap">{body}</pre>
  )
}

function DocxPreview({ path }: { path: string }) {
  const [state, setState] = useState<"loading" | "ok" | "error">("loading")
  const [html, setHtml] = useState<string>("")
  const [err, setErr] = useState<string>("")
  useEffect(() => {
    let cancelled = false
    setState("loading")
    ;(async () => {
      try {
        const mammoth = await import("mammoth/mammoth.browser.js")
        const r = await fetch("/api/files/raw?path=" + encodeURIComponent(path))
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const buf = await r.arrayBuffer()
        const out = await mammoth.convertToHtml({ arrayBuffer: buf })
        if (cancelled) return
        setHtml(DOMPurify.sanitize(out.value))
        setState("ok")
      } catch (e) {
        if (cancelled) return
        setErr(e instanceof Error ? e.message : String(e))
        setState("error")
      }
    })()
    return () => { cancelled = true }
  }, [path])
  if (state === "loading") return <PreviewLoading label="Rendering DOCX (mammoth)…" />
  if (state === "error")   return <PreviewError message={err} />
  return (
    <article
      className="prose prose-sm dark:prose-invert max-w-3xl mx-auto p-6"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

function PdfPreview({ path }: { path: string }) {
  // Simplest workable preview: native browser PDF viewer in an iframe.
  // ADR D4 calls for PDF.js explicitly; that's slated for the next polish
  // pass when we want page navigation + text selection callbacks. For
  // Phase 17 the iframe is the right cost/value tradeoff and lets us hold
  // the bundle under 500 KB gz.
  const src = "/api/files/raw?path=" + encodeURIComponent(path)
  return (
    <iframe
      title={path}
      src={src}
      className="w-full h-full bg-muted"
    />
  )
}

function BinaryPreview({ path, ext }: { path: string; ext: string }) {
  const url = "/api/files/raw?path=" + encodeURIComponent(path)
  if (["png", "jpg", "jpeg", "gif", "webp", "svg"].includes(ext)) {
    return (
      <div className="h-full flex items-center justify-center bg-muted/30 p-6">
        <img src={url} alt={path} className="max-w-full max-h-full" />
      </div>
    )
  }
  return (
    <div className="p-6 max-w-md mx-auto text-center text-sm text-muted-foreground">
      No inline preview for <span className="font-mono">.{ext || "?"}</span> yet.
      <div className="mt-3">
        <a className="underline" href={url} target="_blank" rel="noreferrer">Open raw file ↗</a>
      </div>
    </div>
  )
}

function PreviewLoading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
      <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden /> {label}
    </div>
  )
}

function PreviewError({ message }: { message: string }) {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Alert variant="destructive" role="alert">
        <AlertCircle className="w-4 h-4" aria-hidden />
        <AlertTitle>Couldn't preview this file</AlertTitle>
        <AlertDescription className="break-words">{message}</AlertDescription>
      </Alert>
    </div>
  )
}

function useTextFile(path: string): { state: "loading" | "ok" | "error"; body: string | null } {
  const [state, setState] = useState<"loading" | "ok" | "error">("loading")
  const [body, setBody] = useState<string | null>(null)
  useEffect(() => {
    let cancelled = false
    setState("loading"); setBody(null)
    ;(async () => {
      try {
        const r = await fetch("/api/files/text?path=" + encodeURIComponent(path))
        if (!r.ok) {
          let detail: unknown = r.statusText
          try { detail = (await r.json()).detail } catch { /* ignore */ }
          throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail))
        }
        const j = await r.json() as { content: string }
        if (cancelled) return
        setBody(j.content)
        setState("ok")
      } catch (e) {
        if (cancelled) return
        setBody(e instanceof Error ? e.message : String(e))
        setState("error")
      }
    })()
    return () => { cancelled = true }
  }, [path])
  return { state, body }
}

const TEXTISH = new Set([
  "txt", "log", "json", "yml", "yaml", "toml", "ini", "csv", "tsv",
  "ts", "tsx", "js", "jsx", "py", "rs", "go", "rb", "sh", "bash", "zsh",
  "html", "css", "scss", "sql", "env", "gitignore", "gitkeep",
])
function isTextish(ext: string) { return TEXTISH.has(ext) }

function formatBytes(n: number): string {
  if (n < 1024) return n + " B"
  if (n < 1024 * 1024) return (n / 1024).toFixed(0) + " KB"
  return (n / (1024 * 1024)).toFixed(1) + " MB"
}
