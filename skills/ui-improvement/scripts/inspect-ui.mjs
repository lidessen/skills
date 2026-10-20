import { createRequire } from "node:module";
import { resolve } from "node:path";
import { writeFile } from "node:fs/promises";
import { inspectElement, locate } from "./inspect-element.mjs";
import { probeUI } from "./probe-ui.mjs";
const usage =
  "bun /path/to/inspect-ui.mjs --url URL --target CSS_OR_JSON_ADDRESS [--frame CSS] [--width 1440] [--focus yes] [--trial yes] [--screenshot FILE] [--padding 20] [--out FILE] [--channel chrome]";
const args = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  if (key === "--help") {
    console.log(usage);
    process.exit(0);
  }
  if (
    ![
      "--url",
      "--target",
      "--frame",
      "--focus",
      "--trial",
      "--screenshot",
      "--padding",
      "--out",
      "--channel",
      "--width",
    ].includes(key) ||
    !process.argv[i + 1]
  )
    throw Error(usage);
  args[key.slice(2)] = process.argv[i + 1];
}
if (!args.url || !args.target) throw Error(usage);
const url = new URL(args.url);
if (!["http:", "https:"].includes(url.protocol)) throw Error("Use an authorized preview URL.");
for (const flag of ["focus", "trial"])
  if (args[flag] && args[flag] !== "yes") throw Error(`--${flag} accepts yes or omission`);
const padding = Number(args.padding || 0);
if (!Number.isFinite(padding) || padding < 0) throw Error("padding must be nonnegative");
const width = Number(args.width || 1440);
if (!Number.isInteger(width) || width < 1 || width > 10000)
  throw Error("width must be an integer between 1 and 10000");
const address = args.target.startsWith("[") ? JSON.parse(args.target) : args.target;
const { chromium } = createRequire(resolve(process.cwd(), "package.json"))("@playwright/test");
const browser = await chromium.launch({
  headless: true,
  ...(args.channel ? { channel: args.channel } : {}),
});
try {
  const page = await browser.newPage({ viewport: { width, height: 960 } });
  await page.goto(url.href);
  await page.evaluate(() => document.fonts.ready);
  const context = args.frame ? page.frameLocator(args.frame) : page;
  const target = locate(context, address);
  if (args.focus) await target.focus();
  const result = await inspectElement(target, {
    trial: args.trial === "yes",
    screenshot: args.screenshot ? { path: args.screenshot, padding } : null,
  });
  // Module users can evaluate probeUI in their selected Frame; avoid mixing iframe coordinates here.
  result.relations = args.frame ? null : await page.evaluate(probeUI, { scope: address });
  const output = JSON.stringify(result, null, 2) + "\n";
  if (args.out) {
    await writeFile(args.out, output);
    console.log(
      JSON.stringify({
        output: args.out,
        box: result.facts.box,
        margin: ["Top", "Right", "Bottom", "Left"].map((k) => result.facts.computed["margin" + k]),
        padding: ["Top", "Right", "Bottom", "Left"].map(
          (k) => result.facts.computed["padding" + k],
        ),
        actionability: result.actionability,
        capture: result.capture,
      }),
    );
  } else process.stdout.write(output);
} finally {
  await browser.close();
}
