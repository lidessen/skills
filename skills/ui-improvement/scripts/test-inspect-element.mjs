import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { resolve, join } from "node:path";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { elementFacts, inspectElement, locate } from "./inspect-element.mjs";

const { chromium } = createRequire(resolve(process.cwd(), "package.json"))("@playwright/test");
const browser = await chromium.launch({ channel: "chrome", headless: true });
const directory = await mkdtemp(join(tmpdir(), "ui-inspector-test-"));
const dimensions = async (path) => {
  const png = await readFile(path);
  return [png.readUInt32BE(16), png.readUInt32BE(20)];
};
try {
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  await page.setContent(`<style>
    body{margin:0}#target{position:absolute;left:100px;top:100px;width:120px;height:40px;margin:0;padding:8px 12px;box-sizing:border-box}
    #overlay{position:absolute;left:100px;top:100px;width:120px;height:40px;background:#fff;z-index:2}
    #sample{position:absolute;left:300px;top:100px;width:80px}
  </style><button id="target">Save</button><div id="overlay"></div>
  <div id="sample">Two lines of ordinary visible text.<input value="private input"><textarea>private textarea</textarea>
    <svg width="40" height="40" viewBox="0 0 20 20"><rect x="2" y="3" width="10" height="8"/></svg>
  </div><div id="component"></div><script>window.clicks=0;document.querySelector('#target').onclick=()=>window.clicks++</script>`);
  const target = page.locator("#target");
  const blocked = await inspectElement(target, { trial: true });
  assert.equal(blocked.actionability.ready, false);
  assert.equal(
    blocked.facts.hitTests.every((p) => p.hit.id === "overlay"),
    true,
  );
  assert.equal(await page.evaluate(() => window.clicks), 0);
  assert.equal(blocked.semantics, null);
  await page.locator("#overlay").evaluate((el) => (el.style.pointerEvents = "none"));
  const passThrough = await inspectElement(target, { trial: true });
  assert.equal(passThrough.actionability.ready, true);
  assert.equal(
    passThrough.facts.hitTests.every((p) => p.status === "target-or-composed-descendant"),
    true,
  );
  assert.equal(await page.evaluate(() => window.clicks), 0);
  // Pointer routing can pass even while an opaque decorative overlay still paints above the control.
  assert.equal(
    passThrough.facts.limits.some((s) => s.includes("pointer-events:none")),
    true,
  );
  const sample = await page.locator("#sample").evaluate(elementFacts);
  assert.equal(sample.text.fragments.length > 1, true);
  assert.equal(sample.text.characters, "Two lines of ordinary visible text.".length);
  assert.equal(JSON.stringify(sample).includes("private input"), false);
  assert.equal(JSON.stringify(sample).includes("private textarea"), false);
  assert.deepEqual(sample.svg.items[0].fillBBox, { x: 2, y: 3, width: 10, height: 8 });
  assert.equal(sample.svg.items[0].viewportCorners.length, 4);
  await page.evaluate(() => {
    document.querySelector("#component").attachShadow({ mode: "open" }).innerHTML =
      '<button id="inside">Inner</button>';
  });
  const inner = await inspectElement(locate(page, ["#component", "#inside"]));
  assert.equal(
    inner.facts.hitTests.every((p) => p.status === "target-or-composed-descendant"),
    true,
  );
  assert.equal(inner.facts.ancestors[0].id, "component");

  const exactPath = join(directory, "element.png");
  const paddedPath = join(directory, "padded.png");
  await inspectElement(target, { screenshot: { path: exactPath } });
  const padded = await inspectElement(target, { screenshot: { path: paddedPath, padding: 20 } });
  assert.deepEqual(await dimensions(exactPath), [120, 40]);
  assert.deepEqual(await dimensions(paddedPath), [160, 80]);
  assert.deepEqual(padded.capture.clip, { x: 80, y: 80, width: 160, height: 80 });
  assert.equal(padded.facts.computed.paddingLeft, "12px");
  assert.equal(padded.facts.computed.marginTop, "0px");
  await target.evaluate((el) => {
    el.style.left = "2px";
    el.style.top = "3px";
  });
  const edgePath = join(directory, "edge.png");
  const edge = await inspectElement(target, { screenshot: { path: edgePath, padding: 20 } });
  assert.deepEqual(edge.capture.clip, { x: 0, y: 0, width: 142, height: 63 });
  assert.deepEqual(await dimensions(edgePath), [142, 63]);

  // Run the actual command against a preview, including Shadow selection and frame crops.
  const server = Bun.serve({
    hostname: "127.0.0.1",
    port: 0,
    fetch: (req) =>
      new Response(
        new URL(req.url).pathname === "/child"
          ? '<style>body{margin:0}button{position:absolute;left:10px;top:15px;width:80px;height:30px}</style><button id="frame-button">Frame</button>'
          : '<div id="host"></div><script>document.querySelector("#host").attachShadow({mode:"open"}).innerHTML="<button id=inner>Shadow</button>"</script><iframe id="frame" style="position:absolute;left:200px;top:100px;width:200px;height:100px;border:0" src="/child"></iframe>',
        { headers: { "content-type": "text/html" } },
      ),
  });
  try {
    const script = fileURLToPath(new URL("./inspect-ui.mjs", import.meta.url));
    const invoke = async (extra) => {
      const child = Bun.spawn(
        [process.execPath, script, "--url", server.url.href, "--channel", "chrome", ...extra],
        { stdout: "pipe", stderr: "pipe" },
      );
      const [out, err, exit] = await Promise.all([
        new Response(child.stdout).text(),
        new Response(child.stderr).text(),
        child.exited,
      ]);
      assert.equal(exit, 0, err);
      return JSON.parse(out);
    };
    const shadow = await invoke(["--target", '["#host","#inner"]']);
    assert.equal(shadow.facts.element.id, "inner");
    assert.equal(shadow.relations.controls[0].address[0], "#host");
    const framePath = join(directory, "frame.png");
    const frame = await invoke([
      "--target",
      "#frame-button",
      "--frame",
      "#frame",
      "--screenshot",
      framePath,
      "--padding",
      "10",
    ]);
    assert.equal(frame.facts.box.x, 10);
    assert.equal(frame.facts.box.y, 15);
    assert.equal(frame.relations, null);
    assert.deepEqual(frame.capture.clip, { x: 200, y: 105, width: 100, height: 50 });
    assert.deepEqual(await dimensions(framePath), [100, 50]);
  } finally {
    server.stop(true);
  }
  console.log(
    "Element inspector: real obstruction vs pass-through painting, trial without click, private-value omission, Range/SVG, Shadow hit testing, actual crop dimensions and CLI frame coordinates passed.",
  );
} finally {
  await browser.close();
  await rm(directory, { recursive: true, force: true });
}
