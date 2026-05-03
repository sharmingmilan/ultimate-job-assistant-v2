/**
 * First-launch onboarding. Surfaces when /api/health says the project root
 * is not configured. Walks the user through (a) setting the project root
 * and (b) pasting the API key. The host's keystore.set_api_key tests the
 * connection before persisting, so a bad key is rejected here.
 */
import { useState } from "react"
import { Loader2, FolderOpen, KeyRound, ArrowRight, CheckCircle2 } from "lucide-react"
import { api, ApiError } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function Onboarding({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState<"root" | "key" | "done">("root")
  const [projectRoot, setProjectRoot] = useState("")
  const [apiKey, setApiKey] = useState("")
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  async function submitRoot() {
    setBusy(true); setErr(null)
    try {
      await api.setProjectRoot(projectRoot.trim())
      setStep("key")
    } catch (e) {
      setErr(e instanceof ApiError ? String(e.detail) : String(e))
    } finally {
      setBusy(false)
    }
  }

  async function submitKey() {
    setBusy(true); setErr(null)
    try {
      await api.setKey(apiKey.trim(), true)
      setStep("done")
    } catch (e) {
      setErr(e instanceof ApiError ? String(e.detail) : String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-xl mx-auto py-12 px-6">
        <div className="mb-8 flex items-center gap-3">
          <span aria-hidden className="inline-block w-10 h-10 rounded-lg bg-brand-gradient" />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Welcome to UJA</h1>
            <p className="text-sm text-muted-foreground">Two quick steps and you're set up.</p>
          </div>
        </div>

        <ol className="mb-6 flex items-center gap-2 text-xs">
          <Pip done={step !== "root"} active={step === "root"} label="1. Project folder" />
          <ArrowRight className="w-3 h-3 text-muted-foreground" aria-hidden />
          <Pip done={step === "done"} active={step === "key"} label="2. API key" />
          <ArrowRight className="w-3 h-3 text-muted-foreground" aria-hidden />
          <Pip done={step === "done"} active={step === "done"} label="Ready" />
        </ol>

        {step === "root" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><FolderOpen className="w-4 h-4" /> Pick your project folder</CardTitle>
              <CardDescription>
                Paste the absolute path to your Ultimate Job Assistant folder.
                The host can only read or write inside this folder — nothing else.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="root">Project root</Label>
                <Input
                  id="root"
                  autoFocus
                  placeholder="/Users/you/Documents/Ultimate Job Assistant"
                  value={projectRoot}
                  onChange={(e) => setProjectRoot(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && projectRoot.trim() && submitRoot()}
                />
              </div>
              {err && <ErrorAlert message={err} />}
              <div className="flex justify-end">
                <Button onClick={submitRoot} disabled={!projectRoot.trim() || busy}>
                  {busy && <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden />}
                  Continue
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === "key" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><KeyRound className="w-4 h-4" /> Paste your Anthropic API key</CardTitle>
              <CardDescription>
                Stored in your OS keychain. The key never leaves your machine and is
                redacted from server logs. We test it with one short request before saving.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="key">Anthropic API key</Label>
                <Input
                  id="key"
                  type="password"
                  autoFocus
                  placeholder="sk-ant-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && apiKey.trim() && submitKey()}
                />
              </div>
              {err && <ErrorAlert message={err} />}
              <div className="flex justify-between">
                <Button variant="ghost" onClick={() => setStep("root")} disabled={busy}>Back</Button>
                <Button onClick={submitKey} disabled={!apiKey.trim() || busy}>
                  {busy && <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden />}
                  Save and test
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === "done" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="w-5 h-5" /> All set
              </CardTitle>
              <CardDescription>You're ready to chat. The first conversation starts in the Chat tab.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={onComplete}>Open the app</Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

function Pip({ done, active, label }: { done: boolean; active: boolean; label: string }) {
  return (
    <span
      className={[
        "inline-flex items-center px-2 py-1 rounded-full border",
        done ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300" :
        active ? "border-brand-sky/40 bg-brand-sky/10 text-foreground" :
        "border-border bg-card text-muted-foreground",
      ].join(" ")}
    >
      {label}
    </span>
  )
}

function ErrorAlert({ message }: { message: string }) {
  return (
    <Alert variant="destructive" role="alert">
      <AlertTitle>That didn't work</AlertTitle>
      <AlertDescription className="break-words">{message}</AlertDescription>
    </Alert>
  )
}
