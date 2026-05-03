/**
 * Chat tab — the primary surface.
 *
 *   left:   conversation sidebar (lists /api/conversations)
 *   right:  message stream + composer
 *
 * Streams /api/chat as SSE. Renders text / tool_use (collapsed) /
 * tool_result blocks. Pending change-sets and pending questions show
 * inline cards (Phase 17 ships them as placeholders that POST to a stub
 * endpoint Phase 17.5 will wire). Keyboard: cmd+enter sends; esc cancels
 * the in-flight request.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { Plus, MessageSquare, Loader2, Send, AlertCircle, Wrench, ChevronRight, ChevronDown } from "lucide-react"
import { api, ApiError, streamChat } from "@/lib/api"
import type { ChatEvent, ConversationSummary, MessageRow } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface RenderedBlock {
  type: "text" | "tool_use" | "tool_result"
  id?: string                // for tool_use / tool_result correlation
  name?: string
  input?: unknown
  text?: string
  is_error?: boolean
  content?: unknown
}

interface ChatRow {
  id: string                  // local id; not persisted
  role: "user" | "assistant"
  blocks: RenderedBlock[]
  pending?: boolean           // assistant row that's still streaming
}

export function ChatTab() {
  const [convs, setConvs] = useState<ConversationSummary[] | null>(null)
  const [convsErr, setConvsErr] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [rows, setRows] = useState<ChatRow[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [streamErr, setStreamErr] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const abortRef = useRef<AbortController | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  // Tracks which conversation the in-flight stream is writing to. The load-
  // history useEffect skips fetching when activeId matches this ref, so the
  // `conversation` SSE event firing setActiveId mid-stream doesn't wipe the
  // in-flight asstRow with a stale DB read. Cleared in send()'s finally.
  const streamingConvIdRef = useRef<string | null>(null)

  const loadConvs = useCallback(async () => {
    try {
      const r = await api.listConversations()
      setConvs(r.conversations)
      setConvsErr(null)
    } catch (e) {
      setConvsErr(e instanceof ApiError ? String(e.detail) : String(e))
    }
  }, [])

  useEffect(() => { loadConvs() }, [loadConvs])

  // Load message history when switching conversations.
  useEffect(() => {
    if (!activeId) { setRows([]); return }
    if (streamingConvIdRef.current === activeId) return  // stream owns this conv right now; do not wipe in-flight rows
    let cancelled = false
    setHistoryLoading(true)
    api.getConversation(activeId)
      .then(({ messages }) => {
        if (cancelled) return
        setRows(messagesToRows(messages))
      })
      .catch((e) => { if (!cancelled) setStreamErr(String(e?.message ?? e)) })
      .finally(() => { if (!cancelled) setHistoryLoading(false) })
    return () => { cancelled = true }
  }, [activeId])

  // Auto-scroll to bottom on new content.
  useEffect(() => {
    if (!scrollRef.current) return
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [rows])

  // Cleanup any in-flight stream on unmount.
  useEffect(() => () => abortRef.current?.abort(), [])

  const startNew = () => {
    abortRef.current?.abort()
    setActiveId(null)
    setRows([])
    setStreamErr(null)
    setInput("")
  }

  async function send() {
    const text = input.trim()
    if (!text || streaming) return
    setInput("")
    setStreamErr(null)

    const userRow: ChatRow = { id: crypto.randomUUID(), role: "user", blocks: [{ type: "text", text }] }
    const asstRowId = crypto.randomUUID()
    const asstRow: ChatRow = { id: asstRowId, role: "assistant", blocks: [], pending: true }
    setRows((prev) => [...prev, userRow, asstRow])

    const ac = new AbortController()
    abortRef.current = ac
    setStreaming(true)

    let assignedConvId = activeId

    try {
      await streamChat({
        conversation_id: activeId ?? undefined,
        message: text,
        signal: ac.signal,
        onEvent: (ev: ChatEvent) => handleEvent(ev, asstRowId, (cid) => {
          streamingConvIdRef.current = cid  // set BEFORE setActiveId so the load-history skip-check sees it
          assignedConvId = cid
          setActiveId(cid)
        }),
      })
      // Refresh sidebar — title may have been auto-set from the first message.
      loadConvs()
    } catch (e) {
      if (ac.signal.aborted) {
        setStreamErr("Cancelled.")
      } else if (e instanceof ApiError && e.status === 409) {
        setStreamErr(`Setup needed: ${String(e.detail)}. Open Settings to fix.`)
      } else {
        setStreamErr(e instanceof Error ? e.message : String(e))
      }
    } finally {
      streamingConvIdRef.current = null  // clear in-flight marker; future history loads run normally again
      setStreaming(false)
      setRows((prev) => prev.map((r) => r.id === asstRowId ? { ...r, pending: false } : r))
      // If we just created a brand-new conversation, make sure the sidebar shows it.
      if (assignedConvId && assignedConvId !== activeId) loadConvs()
    }
  }

  function handleEvent(ev: ChatEvent, asstRowId: string, onConv: (id: string) => void) {
    if (ev.type === "conversation") { onConv(ev.conversation_id); return }
    if (ev.type === "iteration") return
    if (ev.type === "error") { setStreamErr(ev.error); return }
    if (ev.type === "end_turn") return

    setRows((prev) => prev.map((r) => {
      if (r.id !== asstRowId) return r
      const blocks = [...r.blocks]
      if (ev.type === "text") {
        // Coalesce consecutive text deltas into the same block for cleaner rendering.
        const last = blocks[blocks.length - 1]
        if (last && last.type === "text") {
          blocks[blocks.length - 1] = { ...last, text: (last.text ?? "") + ev.text }
        } else {
          blocks.push({ type: "text", text: ev.text })
        }
      } else if (ev.type === "tool_use") {
        blocks.push({ type: "tool_use", id: ev.id, name: ev.name, input: ev.input })
      } else if (ev.type === "tool_result") {
        blocks.push({ type: "tool_result", id: ev.tool_use_id, name: ev.name, is_error: ev.is_error, content: ev.content })
      }
      return { ...r, blocks }
    }))
  }

  function onComposerKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault(); send()
    } else if (e.key === "Escape" && streaming) {
      e.preventDefault(); abortRef.current?.abort()
    }
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 border-r flex-col bg-card/30">
        <div className="p-3 border-b flex items-center justify-between">
          <span className="text-xs uppercase tracking-wide text-muted-foreground font-medium">Conversations</span>
          <Button size="sm" variant="ghost" onClick={startNew} className="h-7 px-2">
            <Plus className="w-4 h-4 mr-1" aria-hidden /> New
          </Button>
        </div>
        <ScrollArea className="flex-1">
          {convsErr ? (
            <div className="p-3 text-xs text-destructive">{convsErr}</div>
          ) : convs === null ? (
            <SidebarSkeleton />
          ) : convs.length === 0 ? (
            <div className="p-4 text-xs text-muted-foreground">
              No conversations yet. Send your first message to start one.
            </div>
          ) : (
            <ul className="py-1">
              {convs.map((c) => (
                <li key={c.id}>
                  <button
                    onClick={() => setActiveId(c.id)}
                    className={cn(
                      "w-full text-left px-3 py-2 text-sm hover:bg-accent/50 transition-colors flex items-start gap-2",
                      activeId === c.id && "bg-accent text-accent-foreground",
                    )}
                  >
                    <MessageSquare className="w-3.5 h-3.5 mt-0.5 flex-none text-muted-foreground" aria-hidden />
                    <span className="flex-1 min-w-0">
                      <span className="block truncate">{c.title || "(untitled)"}</span>
                      <span className="block text-[11px] text-muted-foreground truncate">
                        {formatRelative(c.updated_at)}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </ScrollArea>
      </aside>

      {/* Stream + composer */}
      <section className="flex-1 min-w-0 flex flex-col">
        <div ref={scrollRef} className="flex-1 overflow-auto">
          {historyLoading ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden /> Loading conversation…
            </div>
          ) : rows.length === 0 ? (
            <EmptyChat />
          ) : (
            <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 space-y-6">
              {rows.map((r) => <ChatRowView key={r.id} row={r} />)}
            </div>
          )}
          {streamErr && (
            <div className="max-w-3xl mx-auto px-4 md:px-6 pb-4">
              <Alert variant="destructive" role="alert">
                <AlertCircle className="w-4 h-4" aria-hidden />
                <AlertTitle>Stream error</AlertTitle>
                <AlertDescription className="break-words">{streamErr}</AlertDescription>
              </Alert>
            </div>
          )}
        </div>

        <div className="border-t bg-card/30">
          <div className="max-w-3xl mx-auto px-4 md:px-6 py-3">
            <div className="flex items-end gap-2">
              <Textarea
                rows={2}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onComposerKey}
                placeholder={activeId ? "Reply…" : "Start a new conversation…"}
                className="min-h-[3rem] resize-none"
                aria-label="Message"
                disabled={streaming}
              />
              <div className="flex flex-col gap-1">
                {streaming ? (
                  <Button onClick={() => abortRef.current?.abort()} variant="secondary" aria-label="Cancel (esc)">
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" aria-hidden /> Cancel
                  </Button>
                ) : (
                  <Button onClick={send} disabled={!input.trim()} aria-label="Send (cmd+enter)">
                    <Send className="w-4 h-4 mr-1" aria-hidden /> Send
                  </Button>
                )}
                <kbd className="text-[10px] text-muted-foreground font-mono text-center">⌘↩</kbd>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function EmptyChat() {
  const examples = [
    "Run the orchestrator for a new role at Anthropic",
    "Summarize the open applications in tracker.md",
    "Decode the JD I just dropped in decoded-jds/",
  ]
  return (
    <div className="h-full flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-4 w-12 h-12 rounded-xl bg-brand-gradient" aria-hidden />
        <h2 className="text-lg font-semibold tracking-tight">Start a conversation</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          The agent has file tools scoped to your project root, plus the eight UJA skills.
          Try one of these to warm up:
        </p>
        <ul className="mt-4 space-y-1.5 text-sm text-left">
          {examples.map((s) => (
            <li key={s} className="px-3 py-2 rounded-md border bg-card text-card-foreground">
              <span className="text-muted-foreground mr-1">›</span>{s}
            </li>
          ))}
        </ul>
        <p className="mt-6 text-xs text-muted-foreground">
          Press <kbd className="font-mono">⌘↩</kbd> to send, <kbd className="font-mono">esc</kbd> to cancel.
        </p>
      </div>
    </div>
  )
}

function SidebarSkeleton() {
  return (
    <ul className="p-2 space-y-1.5" aria-busy="true" aria-label="Loading conversations">
      {Array.from({ length: 6 }).map((_, i) => (
        <li key={i} className="h-9 rounded-md bg-muted/40 animate-pulse" />
      ))}
    </ul>
  )
}

function ChatRowView({ row }: { row: ChatRow }) {
  return (
    <article className={cn("flex gap-3", row.role === "user" ? "justify-end" : "")}>
      {row.role === "assistant" && (
        <div aria-hidden className="flex-none w-7 h-7 rounded-md bg-brand-gradient mt-1" />
      )}
      <div className={cn(
        "max-w-[85%] space-y-2",
        row.role === "user" && "bg-secondary text-secondary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5",
        row.role === "assistant" && "rounded-2xl rounded-tl-sm",
      )}>
        {row.blocks.length === 0 && row.pending && (
          <span className="inline-flex items-center text-sm text-muted-foreground">
            <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" aria-hidden /> Thinking…
          </span>
        )}
        {row.blocks.map((b, i) => <BlockView key={i} block={b} />)}
      </div>
    </article>
  )
}

function BlockView({ block }: { block: RenderedBlock }) {
  if (block.type === "text") {
    return <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{block.text}</p>
  }
  if (block.type === "tool_use") {
    return (
      <ToolUseCard
        name={block.name ?? "(unknown)"}
        input={block.input}
        // Render the change-set / question card if this is one of the
        // human-in-the-loop primitives.
        special={
          block.name === "propose_changes" ? "change_set" :
          block.name === "ask_user"        ? "question"  :
          undefined
        }
      />
    )
  }
  // tool_result
  return (
    <ToolResultCard
      name={block.name ?? "(unknown)"}
      isError={block.is_error ?? false}
      content={block.content}
    />
  )
}

function ToolUseCard({
  name, input, special,
}: { name: string; input: unknown; special?: "change_set" | "question" }) {
  const [open, setOpen] = useState(special !== undefined)
  return (
    <div className="text-sm border rounded-md bg-card">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-accent/30 rounded-md"
        aria-expanded={open}
      >
        {open ? <ChevronDown className="w-3.5 h-3.5" aria-hidden /> : <ChevronRight className="w-3.5 h-3.5" aria-hidden />}
        <Wrench className="w-3.5 h-3.5 text-muted-foreground" aria-hidden />
        <span className="font-mono text-xs">{name}</span>
        {special === "change_set" && <span className="ml-auto text-xs text-amber-600 dark:text-amber-400">awaiting approval</span>}
        {special === "question" && <span className="ml-auto text-xs text-brand-pink">question for you</span>}
      </button>
      {open && (
        <div className="px-3 pb-3 border-t">
          {special === "change_set" ? (
            <PendingChangeSet input={input} />
          ) : special === "question" ? (
            <PendingQuestion input={input} />
          ) : (
            <pre className="mt-2 text-[12px] font-mono whitespace-pre-wrap text-muted-foreground overflow-auto max-h-64">
              {safeJson(input)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

function ToolResultCard({ name, isError, content }: { name: string; isError: boolean; content: unknown }) {
  const [open, setOpen] = useState(isError)
  return (
    <div className={cn("text-sm border rounded-md", isError ? "border-destructive/50 bg-destructive/5" : "bg-muted/30")}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full px-3 py-1.5 flex items-center gap-2 text-left rounded-md hover:bg-accent/30"
        aria-expanded={open}
      >
        {open ? <ChevronDown className="w-3.5 h-3.5" aria-hidden /> : <ChevronRight className="w-3.5 h-3.5" aria-hidden />}
        <span className={cn("font-mono text-xs", isError && "text-destructive")}>
          {isError ? "↳ error from " : "↳ result from "}{name}
        </span>
      </button>
      {open && (
        <pre className="px-3 pb-3 text-[12px] font-mono whitespace-pre-wrap overflow-auto max-h-72">
          {safeJson(content)}
        </pre>
      )}
    </div>
  )
}

function PendingChangeSet({ input }: { input: unknown }) {
  const obj = (input ?? {}) as { changes?: Array<{ path: string; before?: string; after?: string; delete?: boolean }>; summary?: string }
  const changes = obj.changes ?? []
  return (
    <div className="mt-2 space-y-2">
      {obj.summary && <p className="text-sm text-muted-foreground">{obj.summary}</p>}
      <ul className="space-y-2">
        {changes.map((c, i) => (
          <li key={i} className="border rounded-md overflow-hidden">
            <div className="px-2 py-1 bg-muted/40 text-xs font-mono flex items-center gap-2">
              <span className="text-muted-foreground">{c.delete ? "DELETE" : c.before === undefined ? "NEW" : "EDIT"}</span>
              <span>{c.path}</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-border">
              <pre className="p-2 text-[12px] font-mono diff-del bg-card whitespace-pre-wrap overflow-auto max-h-56">
                {c.before ?? "(empty)"}
              </pre>
              <pre className="p-2 text-[12px] font-mono diff-add bg-card whitespace-pre-wrap overflow-auto max-h-56">
                {c.after ?? "(deleted)"}
              </pre>
            </div>
          </li>
        ))}
      </ul>
      <div className="flex justify-end gap-2 pt-1">
        <Button variant="outline" size="sm" disabled>
          Reject
        </Button>
        <Button size="sm" disabled title="Approval endpoint ships in Phase 17.5">
          Approve all
        </Button>
      </div>
      <p className="text-[11px] text-muted-foreground text-right">
        Approval endpoint wires up in Phase 17.5; the change-set is saved as pending in the meantime.
      </p>
    </div>
  )
}

function PendingQuestion({ input }: { input: unknown }) {
  const obj = (input ?? {}) as { question?: string; options?: string[] }
  return (
    <div className="mt-2 space-y-2">
      <p className="text-sm">{obj.question ?? "(no question text)"}</p>
      {obj.options && obj.options.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {obj.options.map((opt, i) => (
            <Button key={i} size="sm" variant="outline" disabled>{opt}</Button>
          ))}
        </div>
      ) : (
        <Textarea rows={2} placeholder="Type your answer in the composer below and press send." disabled />
      )}
      <p className="text-[11px] text-muted-foreground">
        Question persists in <span className="font-mono">pending_questions</span> until you reply in the composer.
      </p>
    </div>
  )
}

/* ------------------------------------------------------------------ *
 * Helpers
 * ------------------------------------------------------------------ */

function messagesToRows(messages: MessageRow[]): ChatRow[] {
  const out: ChatRow[] = []
  for (const m of messages) {
    if (m.role !== "user" && m.role !== "assistant") continue
    let blocks: RenderedBlock[]
    if (typeof m.content === "string") {
      blocks = [{ type: "text", text: m.content }]
    } else if (Array.isArray(m.content)) {
      blocks = (m.content as Array<Record<string, unknown>>).map((b) => {
        const bt = (b.type ?? "text") as RenderedBlock["type"] | "tool_use" | "tool_result" | "text"
        if (bt === "tool_use") return { type: "tool_use", id: String(b.id ?? ""), name: String(b.name ?? ""), input: b.input }
        if (bt === "tool_result") return {
          type: "tool_result",
          id: String(b.tool_use_id ?? ""),
          name: String(b.name ?? ""),
          is_error: Boolean(b.is_error),
          content: b.content,
        }
        return { type: "text", text: String(b.text ?? "") }
      })
    } else {
      blocks = [{ type: "text", text: safeJson(m.content) }]
    }
    out.push({ id: m.id, role: m.role, blocks })
  }
  return out
}

function safeJson(v: unknown): string {
  try {
    if (typeof v === "string") return v
    return JSON.stringify(v, null, 2)
  } catch {
    return String(v)
  }
}

function formatRelative(iso: string): string {
  try {
    const then = new Date(iso).getTime()
    const now = Date.now()
    const ms = now - then
    if (ms < 60_000) return "just now"
    if (ms < 3_600_000) return `${Math.floor(ms / 60_000)}m ago`
    if (ms < 86_400_000) return `${Math.floor(ms / 3_600_000)}h ago`
    return `${Math.floor(ms / 86_400_000)}d ago`
  } catch { return iso }
}
