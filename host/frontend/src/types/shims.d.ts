// mammoth ships a browser bundle but no type def for the deep import.
// We use a deep import so Vite tree-shakes the Node-only paths out.
declare module "mammoth/mammoth.browser.js" {
  export function convertToHtml(input: { arrayBuffer: ArrayBuffer }): Promise<{ value: string; messages: unknown[] }>
}
