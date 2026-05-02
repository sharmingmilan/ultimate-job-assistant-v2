# Netflix SQL Prep — Deployment Guide

## What's in this folder

- `index.html` — the entire app (React + your content, loads React/Tailwind/Babel from CDNs)
- `manifest.json` — tells iPhone it's a web app, not a website
- `sw.js` — service worker that caches everything for offline use
- `icon-192.png` / `icon-512.png` — app icons for the home screen

All five files must sit at the **root** of your deployment, not in a subfolder.

## Deploying to Vercel (5 minutes, free, no account setup needed)

1. Go to **https://vercel.com/new** and sign in with GitHub, GitLab, or email
2. Click **"Deploy"** in the top nav, then **"Drag and drop a folder"** (you may need to click "Import Third-Party Git Repository" first and look for the drop zone)
   - Alternatively: use the Vercel CLI (`npm i -g vercel` then `vercel` in this folder)
3. Drag all five files from this folder onto the Vercel drop zone
4. Hit **Deploy**. In about 30 seconds you'll get a URL like `netflix-prep-abc123.vercel.app`
5. Open that URL in Safari on your iPhone

## Installing on iPhone

1. Open the Vercel URL in **Safari** (must be Safari, not Chrome)
2. Tap the **Share** button (the box with the up arrow at the bottom)
3. Scroll down and tap **"Add to Home Screen"**
4. Name it what you want, tap **Add**
5. The app now lives on your home screen with the Netflix-red "N" icon

## What works offline

Once you've loaded the app at least once, the service worker caches everything. You can use it on a plane, on the subway, anywhere. Your progress saves to the browser's localStorage and stays on your device only.

## If localStorage gets cleared

iOS Safari may clear web app data after about 7 days of no use. To avoid this:
- Open the app at least once every few days leading up to your interview
- Or, after each study session, open Safari's Share menu and note that progress persists

## Deleting after the interview

Go to Vercel dashboard → your project → Settings → Delete Project. That's it.

## Troubleshooting

**App shows "Loading…" forever**
- Hard refresh: in Safari, pull down from the top while on the page
- Check that all CDN scripts loaded (needs internet on first load)

**Styles look broken**
- Tailwind CDN needs ~2 seconds to scan and generate classes; wait a beat

**Can't Add to Home Screen**
- Must be Safari (not Chrome, Firefox, or any other browser)
- Must be on HTTPS (Vercel is always HTTPS, so this is automatic)
