/**
 * Thin client for the FastAPI host. All endpoints live on the same origin
 * in production (FastAPI mounts dist/ at "/"), and on :5173 with a vite
 * proxy in dev (see vite.config.ts).
 */

export interface HealthResponse {
  ok: boolean
  version: string
  project_root_configured: boolean
}

export interface ConfigResponse {
  project_root: string | null
  schema_version: number
}

export interface KeyStatusResponse {
  has_key: boolean
  using_memory_fallback: boolean
}

export interface ConversationSummary {
  id: string
  title: string
  started_at: string
  updated_at: string
  message_count?: number
}

export interface MessageRow {
  id: string
  conversation_id: string
  role: "user" | "assistant" | "system" | "tool"
  content: unknown        // list-of-blocks (Anthropic shape) or string
  created_at: string
  seq: number
}

export class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail))
    this.status = status
    this.detail = detail
    this.name = "ApiError"
  }
}

async function jsonOrThrow<T>(res: Response): Promise<T> {
  let body: unknown = null
  try { body = await res.json() } catch { /* tolerate empty/non-json */ }
  if (!res.ok) {
    const detail = (body as { detail?: unknown } | null)?.detail ?? body ?? res.statusText
    throw new ApiError(res.status, detail)
  }
  return body as T
}

export const api = {
  health: () => fetch("/api/health").then(r => jsonOrThrow<HealthResponse>(r)),
  getConfig: () => fetch("/api/config").then(r => jsonOrThrow<ConfigResponse>(r)),
  setProjectRoot: (project_root: string) =>
    fetch("/api/config/project-root", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ project_root }),
    }).then(r => jsonOrThrow<ConfigResponse>(r)),
  getKeyStatus: () => fetch("/api/auth/key").then(r => jsonOrThrow<KeyStatusResponse>(r)),
  setKey: (api_key: string, test_connection = true) =>
    fetch("/api/auth/key", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ api_key, test_connection }),
    }).then(r => jsonOrThrow<KeyStatusResponse>(r)),
  deleteKey: () =>
    fetch("/api/auth/key", { method: "DELETE" }).then(r => jsonOrThrow<KeyStatusResponse>(r)),

  listConversations: () =>
    fetch("/api/conversations").then(r =>
      jsonOrThrow<{ conversations: ConversationSummary[]; count: number }>(r),
    ),
  getConversation: (id: string) =>
    fetch(`/api/conversations/${encodeURIComponent(id)}`).then(r =>
      jsonOrThrow<{ conversation: ConversationSummary; messages: MessageRow[] }>(r),
    ),

  // Phase 17.5 — close the human-in-the-loop.
  approveChange: (id: string) =>
    fetch(`/api/changes/${encodeURIComponent(id)}/approve`, { method: "POST" }).then(r =>
      jsonOrThrow<{
        change_id: string
        status: string
        conversation_id: string
        paths_written: Array<{ path: string; action: string }>
        count: number
      }>(r),
    ),
  rejectChange: (id: string) =>
    fetch(`/api/changes/${encodeURIComponent(id)}/reject`, { method: "POST" }).then(r =>
      jsonOrThrow<{ change_id: string; status: string; conversation_id: string }>(r),
    ),
  answerQuestion: (id: string, answer: string) =>
    fetch(`/api/questions/${encodeURIComponent(id)}/answer`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ answer }),
    }).then(r =>
      jsonOrThrow<{ question_id: string; status: string; conversation_id: string }>(r),
    ),
}

/* ------------------------------------------------------------------ *
 * SSE chat stream
 * ------------------------------------------------------------------ */

export type ChatEvent =
  | { type: "conversation"; conversation_id: string }
  | { type: "iteration"; n: number; messages_so_far: number }
  | { type: "text"; text: string }
  | { type: "tool_use"; id: string; name: string; input: unknown }
  | { type: "tool_result"; tool_use_id: string; name: string; is_error: boolean; content: unknown }
  | { type: "end_turn"; stop_reason: string }
  | { type: "error"; error: string }

export interface ChatStreamOptions {
  conversation_id?: string
  message: string
  signal?: AbortSignal
  onEvent: (ev: ChatEvent) => void
}

/** Streams /api/chat as SSE. Resolves when the server closes the stream
 *  (typically after `end_turn` or `error`). Throws on network failure or
 *  non-2xx response. */
export async function streamChat(opts: ChatStreamOptions): Promise<void> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "content-type": "application/json", accept: "text/event-stream" },
    body: JSON.stringify({
      conversation_id: opts.conversation_id ?? null,
      message: opts.message,
    }),
    signal: opts.signal,
  })
  if (!res.ok || !res.body) {
    let detail: unknown = res.statusText
    try { detail = (await res.json()).detail ?? detail } catch { /* ignore */ }
    throw new ApiError(res.status, detail)
  }

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  let buf = ""
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buf += value
    // Parse complete SSE messages — separated by a blank line.
    let idx
    while ((idx = buf.indexOf("\n\n")) !== -1) {
      const raw = buf.slice(0, idx)
      buf = buf.slice(idx + 2)
      const ev = parseSseBlock(raw)
      if (ev) opts.onEvent(ev)
    }
  }
}

function parseSseBlock(raw: string): ChatEvent | null {
  let event = "message"
  const dataLines: string[] = []
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim()
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim())
  }
  if (dataLines.length === 0) return null
  const dataStr = dataLines.join("\n")
  try {
    const parsed = JSON.parse(dataStr) as Record<string, unknown>
    return { type: event, ...parsed } as ChatEvent
  } catch {
    return { type: "text", text: dataStr } as ChatEvent
  }
}
