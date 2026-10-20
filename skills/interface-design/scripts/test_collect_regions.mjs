// Integration test: run with a Node/Bun environment that provides Playwright.
import { chromium } from "@playwright/test";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import assert from "node:assert/strict";
const collector = await readFile(new URL("./collect_regions.js", import.meta.url), "utf8");
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1000, height: 800 },
    deviceScaleFactor: 1,
  });
  await page.setContent(
    `<style>body{margin:0;background:white}.card{padding:16px;background:#eee;width:300px}button{height:28px} .hidden{opacity:0}.clip{width:30px;overflow:hidden;white-space:nowrap}</style><div class="card"><h1>Title</h1><p>Body text</p><button>Action</button><div class="hidden">Hidden</div><div class="clip">Clipped long text</div></div>`,
  );
  const before = await page.content();
  const data = await page.evaluate(collector + "\ncollectRegions()");
  assert.equal(await page.content(), before);
  assert.equal(data.regions.filter((r) => r.kind === "control").length, 1);
  assert.equal(data.regions.find((r) => r.kind === "control").box[3], 28);
  assert.equal(data.regions.filter((r) => r.kind === "text").length, 3);
  assert(data.regions.filter((r) => r.kind === "text").at(-1).box[2] <= 30);
  assert(!JSON.stringify(data).includes("Body text"));
  const url = process.argv[2],
    output = process.argv[3];
  if (url && output) {
    await page.goto(url);
    await page.locator("#story-root > *").first().waitFor();
    await page.evaluate(() => document.fonts.ready);
    const real = await page.evaluate(collector + "\ncollectRegions()");
    assert(real.regions.some((r) => r.kind === "control"));
    await mkdir(output, { recursive: false });
    await writeFile(output + "/regions.json", JSON.stringify(real, null, 2));
    await page.screenshot({ path: output + "/original.png" });
    console.log(JSON.stringify({ output, regions: real.regions.length, warnings: real.warnings }));
  }
  console.log(
    "PASS: unchanged DOM, atomic controls, actual dimensions, hidden text exclusion, overflow clipping, no text export",
  );
} finally {
  await browser.close();
}
