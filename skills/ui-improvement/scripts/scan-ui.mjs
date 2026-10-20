import { createRequire } from "node:module";
import { resolve } from "node:path";
import { writeFile } from "node:fs/promises";
import { probeUI, probeChildFrames } from "./probe-ui.mjs";

const usage =
  "Run from a project with Playwright installed: bun /path/to/scan-ui.mjs --url URL --widths 1440,950,390 [--scope CSS] [--focus CSS] [--out FILE] [--channel chrome] [--playwright-module PATH]";
const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  if (key === "--help") {
    console.log(usage);
    process.exit(0);
  }
  if (
    ![
      "--url",
      "--widths",
      "--scope",
      "--focus",
      "--out",
      "--channel",
      "--playwright-module",
    ].includes(key) ||
    !process.argv[i + 1]
  )
    throw new Error(usage);
  options[key.slice(2)] = process.argv[i + 1];
}
if (!options.url || !options.widths) throw new Error(usage);
const url = new URL(options.url);
if (!["http:", "https:"].includes(url.protocol))
  throw new Error("Use an authorized HTTP(S) preview URL.");
const widths = options.widths.split(",").map(Number);
if (widths.some((n) => !Number.isInteger(n) || n < 1 || n > 10000))
  throw new Error("Widths must be integers between 1 and 10000.");
const require = createRequire(resolve(process.cwd(), "package.json"));
const { chromium } = require(
  options["playwright-module"] ? resolve(options["playwright-module"]) : "@playwright/test",
);
const browser = await chromium.launch({
  headless: true,
  ...(options.channel ? { channel: options.channel } : {}),
});
const results = [];
try {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 960 } });
    try {
      await page.goto(url.href, { waitUntil: "load" });
      await page.evaluate(() => document.fonts.ready);
      const initial = await page.evaluate(probeUI, { scope: options.scope || "body" });
      let focused = null;
      if (options.focus) {
        await page.locator(options.focus).focus();
        focused = await page.evaluate(probeUI, { scope: options.scope || "body" });
      }
      const frames = await probeChildFrames(page);
      results.push({ url: url.href, width, initial, focused, frames });
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}
const output = JSON.stringify(results, null, 2) + "\n";
if (options.out) {
  await writeFile(options.out, output);
  console.log(
    JSON.stringify(
      {
        output: options.out,
        viewports: results.map((r) => ({
          width: r.width,
          extraX: r.initial.document.extraX,
          controls: r.initial.controls.length,
          coverage: r.initial.coverage,
          paintNotMeasured: r.initial.controls
            .filter((control) => control.nativeParts)
            .map((control) => ({
              address: control.address,
              appearance: control.appearance,
              arrowGeometry: control.nativeParts.arrowGeometry,
              popupGeometry: control.nativeParts.popupGeometry,
            })),
          focusCandidates: r.focused?.candidates || [],
          frames: r.frames.map((f) => ({
            url: f.url,
            status: f.status,
            controls: f.facts?.controls.length,
            extraX: f.facts?.document.extraX,
            paintNotMeasured: f.facts?.controls
              .filter((control) => control.nativeParts)
              .map((control) => ({
                address: control.address,
                appearance: control.appearance,
                arrowGeometry: control.nativeParts.arrowGeometry,
                popupGeometry: control.nativeParts.popupGeometry,
              })),
          })),
        })),
      },
      null,
      2,
    ),
  );
} else process.stdout.write(output);
