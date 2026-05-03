# V2_SETUP.md — Spinning up v0.2.0's separate repos + Netlify site

**Status:** Handoff doc. Each step ends with what to do and what success looks like.
**Audience:** Milan, with Claude alongside in a future session.
**Goal:** End with `ultimatejobassist-v2.netlify.app` live and serving the placeholder, and with `ultimate-job-assistant-v2` (canonical) + `ultimate-job-assistant-v2-public` (deploy-source) wired up exactly like the v1 pair, ready for Phase 17 to fill in.

---

## Why this exists

v0.1.x ships at `ultimatejobassist.netlify.app`, backed by:
- canonical: `sharmingmilan/ultimate-job-assistant` (private)
- deploy-source: `sharmingmilan/ultimate-job-assistant-public` (private)

v0.2.0 (web app, BYOK, inner-circle audience) gets its own pair so:
- nothing on the v1 site moves while v0.2.0 is in flight
- v0.2.0's branch life on the existing canonical (`dev/v0.2.0`) gets promoted to `main` on a fresh canonical, simplifying git workflow
- once v0.2.0 stabilizes we decide whether to retire one site or run both permanently (open question, parked)

---

## Prereqs

You'll need:

- A logged-in browser session for github.com (your `sharmingmilan` account)
- A logged-in browser session for app.netlify.com
- ~20 minutes of your time
- Claude open in this session (or a fresh one with `dev/v0.2.0` checked out)

---

## Step 1 — Create the two new GitHub repos (you, ~3 min)

Both PRIVATE. Empty (no README, no .gitignore, no license — Claude pushes the initial commit).

1. Open https://github.com/new
2. Name: **`ultimate-job-assistant-v2`** — Description: "Ultimate Job Assistant v0.2.0 — local web app + skills (canonical, private)" — Visibility: **Private** — Initialize: **none of the boxes** — Click **Create repository**
3. Repeat for **`ultimate-job-assistant-v2-public`** — Description: "Ultimate Job Assistant v0.2.0 — sanitized deploy-source for Netlify (private)" — Visibility: **Private** — Initialize: **none** — Create

**Done when:** both repos exist as empty private repos. Note the URLs:
- `https://github.com/sharmingmilan/ultimate-job-assistant-v2`
- `https://github.com/sharmingmilan/ultimate-job-assistant-v2-public`

---

## Step 2 — Generate two fine-grained PATs (you, ~5 min)

Same model as v1: one PAT for the v2 canonical's git remote (so you can push), one PAT scoped only to v2 deploy-source for auto-sync.

### PAT A — v2 canonical write access

1. https://github.com/settings/personal-access-tokens/new
2. Token name: `uja-v2-canonical-rw` — Expiration: 1 year (or your preference) — Repository access: **Only select repositories** → pick `ultimate-job-assistant-v2`
3. Permissions → Repository permissions:
   - **Contents:** Read and write
   - **Metadata:** Read (auto-selected)
   - **Pull requests:** Read and write
   - **Workflows:** Read and write *(needed if we add CI later — set now to avoid round-tripping)*
   - **Actions:** Read and write
   - **Administration:** Read and write *(only needed if you want Claude to manage repo settings via API; skip if unsure)*
4. Generate. **Copy the token now** — GitHub shows it once.

### PAT B — v2 deploy-source write access (for auto-sync from v2 canonical)

1. New token: `uja-v2-public-write` — Expiration: 1 year — Only select repositories: `ultimate-job-assistant-v2-public`
2. Permissions → Repository:
   - **Contents:** Read and write
3. Generate, copy.

**Done when:** you have two PAT strings stashed somewhere safe (1Password, etc.).

---

## Step 3 — Push v0.2.0's current state to v2 canonical (Claude, ~2 min)

Claude does this in a fresh `/tmp` clone using PAT A. Tell Claude: "Push current dev/v0.2.0 contents to ultimate-job-assistant-v2 as its main branch using this PAT: <PAT A>".

The exact commands Claude will run:

```bash
cd /tmp && git clone --branch dev/v0.2.0 \
  https://x-access-token:<PAT_A>@github.com/sharmingmilan/ultimate-job-assistant.git uja-v2-init
cd uja-v2-init
git remote rename origin v1-origin
git remote add origin https://x-access-token:<PAT_A>@github.com/sharmingmilan/ultimate-job-assistant-v2.git
git branch -m main           # rename dev/v0.2.0 -> main
git push origin main
```

**Done when:** `ultimate-job-assistant-v2` shows the same files as the current `dev/v0.2.0` branch on the v1 canonical — including `host/`, `start-uja.sh`, `start-uja.bat`, the new `V2_SETUP.md`, etc. Open https://github.com/sharmingmilan/ultimate-job-assistant-v2 to confirm.

---

## Step 4 — Add PAT B as a secret on v2 canonical (you, ~1 min)

For the eventual auto-sync workflow.

1. https://github.com/sharmingmilan/ultimate-job-assistant-v2/settings/secrets/actions
2. **New repository secret** → Name: `PUBLIC_REPO_TOKEN` → Secret: paste PAT B → **Add secret**

**Done when:** `PUBLIC_REPO_TOKEN` appears in the secrets list (only the name is shown, never the value).

---

## Step 5 — First sync to v2 deploy-source (Claude, ~3 min)

In a fresh /tmp clone of v2 canonical's main, Claude runs the v2 sync script (`scripts/sync_to_public_v2.py`, included in this commit). The script:

- Walks v2 canonical with the v2 ALLOWLIST (now includes `host/`, `start-uja.sh`, `start-uja.bat`)
- Runs the existing PII scanner over the diff in STRICT mode
- Drops EXCLUDE_DST entries (same as v1)
- Pushes the sanitized result to `ultimate-job-assistant-v2-public`'s main branch

Tell Claude: "Run scripts/sync_to_public_v2.py for the first time with PAT B for deploy-source push."

**Done when:** `ultimate-job-assistant-v2-public` contains the sanitized v2 contents and the PII scan reports clean.

---

## Step 6 — Wire Netlify (you, ~5 min)

1. Open https://app.netlify.com/start
2. **Import from Git** → **GitHub** → authorize Netlify if prompted (it already has access from v1's setup, but may need to add the new repo)
3. Pick `ultimate-job-assistant-v2-public`
4. Build settings:
   - **Branch to deploy:** `main`
   - **Base directory:** *(leave empty)*
   - **Build command:** *(leave empty — netlify.toml in the repo handles it)*
   - **Publish directory:** *(leave empty — netlify.toml sets `website`)*
5. Click **Deploy site**
6. After the first deploy lands (~30 sec), site settings → **Change site name** → set to `ultimatejobassist-v2`
7. Visit `https://ultimatejobassist-v2.netlify.app` — should render the placeholder ("v0.2.0 — Phase 17 in progress")

**Done when:** the URL responds with the placeholder page and the noindex meta tag is present (view-source).

---

## Step 7 — Install pre-push hook on v2 canonical (you, ~1 min)

Per the v1 strategy (branch protection is Pro-gated). The hook installer ships in `scripts/install-hooks.sh`. After cloning v2 canonical for any work session, run once:

```bash
cd ultimate-job-assistant-v2
bash scripts/install-hooks.sh
```

**Done when:** `git config --get core.hooksPath` returns a path that resolves to the project's hooks dir, OR `.git/hooks/pre-push` exists.

---

## Step 8 — (Deferred until Phase 16+) Auto-sync workflow

Once we're past Phase 15 + 16 and the v2 canonical is settling down, port `.github/workflows/auto-sync-to-public.yml` from v1 to v2 canonical and update the workflow comments + the deploy-source repo URL.

**Note from v1:** fine-grained PATs cannot write workflow files (.github/workflows/*) even with Workflows: write. If we hit that limitation again, you'll need to add the workflow file via GitHub web UI manually — that's a 2-minute paste.

This step is **not required to ship Phase 15 / 16**. The v2 site can stay statically-rendered from manual syncs until v0.2.0 is closer to release.

---

## Open question parked here

**What does the v2 site actually serve once Phase 17 lands?**

Options to revisit then:
- (a) Mirror v1's design but with `start-uja.sh` instructions instead of "open in Cowork."
- (b) Live demo: ship a build of the React frontend pointing at a hosted backend (would require operator infra — out of scope for inner-circle BYOK).
- (c) Marketing-only landing: "v0.2.0 is here, download the zip, follow QUICKSTART."

Decision deferred until Phase 17 ships and we can see screenshots.

---

## Cleanup (after the v2 setup is verified working)

The `dev/v0.2.0` branch on v1 canonical is now redundant — its contents live as `main` on v2 canonical. Once v2 is confirmed healthy (a few days of use), delete:

```bash
# from the v1 canonical
git push origin --delete dev/v0.2.0
```

This is optional — leaving the branch dormant on v1 doesn't cost anything.

---

*End of V2_SETUP.md.*
