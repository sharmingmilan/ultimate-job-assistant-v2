// Smoke test for an Ultimate Job Assistant interview-prep PWA build.
// Usage:
//   node smoke_test.cjs <built_dir>
// Spins up a local server, loads the page in headless Chromium, asserts:
//   - no pageerror events
//   - no console errors
//   - bundle is brace-balanced
//   - key UI strings render after Babel compiles the JSX
//   - SQL editor responds to typing
//   - manifest.json is valid

const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const BUILD_DIR = process.argv[2];
if (!BUILD_DIR) {
  console.error("usage: node smoke_test.cjs <built_dir>");
  process.exit(2);
}
if (!fs.existsSync(path.join(BUILD_DIR, "index.html"))) {
  console.error(`No index.html in ${BUILD_DIR}`);
  process.exit(2);
}

// ---- 1. Brace-balance check on index.html JSX block ----
const html = fs.readFileSync(path.join(BUILD_DIR, "index.html"), "utf8");
const open = (html.match(/\{/g) || []).length;
const close = (html.match(/\}/g) || []).length;
if (open !== close) {
  console.error(`FAIL: brace imbalance in index.html: { = ${open}, } = ${close}`);
  process.exit(1);
}
console.log(`  brace balance: { = ${open}, } = ${close}  OK`);

// ---- 2. Bundle size check ----
const size = fs.statSync(path.join(BUILD_DIR, "index.html")).size;
if (size > 400_000) {
  console.error(`FAIL: index.html exceeds 400 KB (${size} bytes)`);
  process.exit(1);
}
console.log(`  bundle size: ${size.toLocaleString()} bytes  OK`);

// ---- 3. Validate manifest.json ----
let manifest;
try {
  manifest = JSON.parse(fs.readFileSync(path.join(BUILD_DIR, "manifest.json"), "utf8"));
  if (!manifest.name || !Array.isArray(manifest.icons) || manifest.icons.length === 0) {
    console.error(`FAIL: manifest missing required keys`);
    process.exit(1);
  }
  console.log(`  manifest.json: name="${manifest.name}", ${manifest.icons.length} icons  OK`);
} catch (e) {
  console.error(`FAIL: manifest.json invalid: ${e.message}`);
  process.exit(1);
}

// ---- 4. Spin up a static server and run the page ----
const PORT = 8765 + Math.floor(Math.random() * 200);
const server = http.createServer((req, res) => {
  let p = path.join(BUILD_DIR, decodeURIComponent(req.url.split("?")[0]));
  if (req.url === "/" || req.url === "") p = path.join(BUILD_DIR, "index.html");
  if (fs.existsSync(p) && fs.statSync(p).isFile()) {
    const ext = path.extname(p);
    const types = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".png": "image/png", ".css": "text/css" };
    res.writeHead(200, { "Content-Type": types[ext] || "application/octet-stream" });
    fs.createReadStream(p).pipe(res);
  } else {
    res.writeHead(404);
    res.end("404");
  }
});

server.listen(PORT, async () => {
  const url = `http://127.0.0.1:${PORT}/`;
  console.log(`  serving from ${url}`);

  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const page = await ctx.newPage();

  const errors = [];
  page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      const t = msg.text();
      // Ignore known-benign console noise from CDN scripts
      if (t.includes("favicon") || t.includes("Service Worker registration")) return;
      errors.push(`console.error: ${t}`);
    }
  });

  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  } catch (e) {
    console.error(`FAIL: page load failed: ${e.message}`);
    server.close();
    await browser.close();
    process.exit(1);
  }

  // Give Babel-standalone a moment to compile JSX
  await page.waitForTimeout(2000);

  // Wait for the app to render (sidebar topic count or "Came" header)
  try {
    await page.waitForSelector("text=/Multi-Table Joins|Came|Topics/", { timeout: 8000 });
  } catch (_) {
    // continue; we'll inspect what we can
  }

  // ---- 5. Diagnostics ----
  // NOTE: innerText applies CSS text-transform; textContent gives raw text.
  // The footer heading uses uppercase styling so we check textContent.
  const diag = await page.evaluate(() => ({
    title: document.title,
    rootHasContent: document.querySelector("#root") && document.querySelector("#root").innerText.length > 50,
    rootText: document.querySelector("#root") ? document.querySelector("#root").innerText.slice(0, 500) : "",
    buttonCount: document.querySelectorAll("button").length,
    hasTopicTitle: !!document.querySelector("h1"),
    hasFooter: document.body.textContent.includes("Built on these citations"),
    hasCitations: document.body.textContent.includes("Sweller") || document.body.textContent.includes("Roediger"),
    hasReact: typeof window.React !== "undefined",
    hasContent: typeof window.__CONTENT__ !== "undefined",
  }));

  console.log(`  page title: "${diag.title}"`);
  console.log(`  root has content: ${diag.rootHasContent}`);
  console.log(`  buttons rendered: ${diag.buttonCount}`);
  console.log(`  React loaded: ${diag.hasReact}`);
  console.log(`  __CONTENT__ injected: ${diag.hasContent}`);
  console.log(`  has citation footer: ${diag.hasFooter}`);
  console.log(`  has scholarly citations: ${diag.hasCitations}`);

  // ---- 6. Test interactivity on an EDITABLE textarea ----
  // Worked-example editors are read-only by design. Saw + Conquered editors are not.
  // Find by aria-label pattern.
  let interactionOK = false;
  try {
    // Saw phase: aria-label="saw attempt 0"; Conquered: "conquered attempt 0"
    const ta = await page.$("textarea[aria-label*='attempt']");
    if (ta) {
      await ta.click();
      await page.keyboard.type("SELECT 1");
      const val = await ta.inputValue();
      interactionOK = val.includes("SELECT 1");
      console.log(`  editable textarea interactivity: ${interactionOK ? "OK" : "FAIL — input not registered"}`);
    } else {
      console.log(`  editable textarea interactivity: SKIPPED (no editable textarea found)`);
    }
  } catch (e) {
    console.log(`  editable textarea interactivity: ERROR ${e.message}`);
  }

  await browser.close();
  server.close();

  // ---- 7. Verdict ----
  console.log("");
  if (errors.length > 0) {
    console.error("FAIL: page errors detected:");
    errors.forEach((e) => console.error(`  - ${e}`));
    process.exit(1);
  }
  if (!diag.rootHasContent) {
    console.error("FAIL: #root has no content (React did not mount)");
    console.error(`  root text snippet: ${JSON.stringify(diag.rootText)}`);
    process.exit(1);
  }
  if (!diag.hasFooter || !diag.hasCitations) {
    console.error(`FAIL: citation footer/text missing (footer=${diag.hasFooter}, citations=${diag.hasCitations})`);
    process.exit(1);
  }
  if (!diag.hasContent) {
    console.error("FAIL: __CONTENT__ not injected");
    process.exit(1);
  }
  if (!interactionOK) {
    console.error("FAIL: editable textarea did not accept typed input");
    process.exit(1);
  }
  console.log("ALL CHECKS PASS");
  process.exit(0);
});
