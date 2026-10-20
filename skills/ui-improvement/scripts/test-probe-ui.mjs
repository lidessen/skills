import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { probeUI, checkpoint, probeChildFrames } from "./probe-ui.mjs";
const { chromium } = createRequire(resolve(process.cwd(), "package.json"))("@playwright/test");
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  await page.setContent(`<style>
    #bad{display:flex;align-items:center;gap:0} select{outline:0}
    select:focus-visible{outline:2px solid green;outline-offset:4px}
    #table{width:200px;height:80px;overflow:auto} #table div{width:600px;height:400px}
    #clipped{width:100px;overflow:hidden;white-space:nowrap}
    #hidden{display:none} #offscreen{position:absolute;top:1000px}
  </style><label id="bad">Progress<select id="choice"><option>Unread</option><option>Reading</option></select></label>
  <div id="table"><div>Intentional wide scrollable content</div></div>
  <div id="clipped">This complete long sentence is clipped by its container.</div>
  <input id="hidden" value="secret"><label>Draft<textarea id="draft">private draft</textarea></label>
  <div style="visibility:hidden"><button id="restored" style="visibility:visible">Visible descendant</button></div>
  <button id="offscreen">Later</button><div id="shadow" style="display:contents"></div><iframe srcdoc="<button>Inner</button>"></iframe>`);
  await page.evaluate(
    () =>
      (document.querySelector("#shadow").attachShadow({ mode: "open" }).innerHTML =
        "<button>Shadow action</button>"),
  );
  const initial = await page.evaluate(probeUI);
  assert.equal(
    initial.controls.some((c) => c.locator === "#restored"),
    true,
  );
  assert.equal(
    initial.controls.some((c) => c.locator === "#hidden"),
    false,
  );
  assert.equal(
    initial.controls.some((c) => c.locator === "#offscreen"),
    true,
  );
  assert.equal(initial.controls.find((c) => c.locator === "#choice").labels[0].text, "Progress");
  assert.equal(initial.candidates.length, 0); // no focus means no focus-state claim
  assert.equal(initial.overflow.find((c) => c.locator === "#table").kind, "scrollable");
  assert.equal(
    initial.overflow.find((c) => c.locator === "#clipped").kind,
    "inspect-clipping-or-expansion",
  );
  assert.equal(initial.coverage.shadowHosts, 1);
  assert.equal(initial.coverage.frames, 1);
  assert.equal(JSON.stringify(initial).includes("private draft"), false);
  assert.equal(
    initial.controls.find((c) => c.locator === "#choice").nativeParts.arrowGeometry,
    "unavailable",
  );
  await page.locator("#choice").focus();
  const focused = await page.evaluate(probeUI);
  assert.equal(
    focused.candidates.some((c) => c.locator === "#choice"),
    true,
  );
  await page.addStyleTag({ content: "#bad{gap:16px}" });
  const separated = await page.evaluate(probeUI);
  assert.equal(
    separated.candidates.some((c) => c.locator === "#choice"),
    false,
  );
  const contentWidth = separated.controls.find((c) => c.locator === "#choice").nativeParts
    .contentWidthBeforeNativeParts;
  await page.addStyleTag({ content: "#choice{transform:scale(2)}" });
  const transformed = await page.evaluate(probeUI);
  assert.equal(
    transformed.controls.find((c) => c.locator === "#choice").nativeParts
      .contentWidthBeforeNativeParts,
    contentWidth,
  );
  assert.equal((await page.evaluate(probeUI, { maxElements: 2 })).coverage.truncated, true);
  await assert.rejects(() => page.evaluate(probeUI, { scope: "#missing" }), /Scope not found/);
  await page.locator("#draft").fill("explicitly selected draft");
  await page.locator("#table").evaluate((el) => (el.scrollTop = 90));
  const state = await checkpoint(page, { fields: ["#draft"], scrollers: ["#table"] });
  assert.equal(state.fields["#draft"], "explicitly selected draft");
  assert.equal(state.scrollers["#table"].top, 90);
  assert.deepEqual((await checkpoint(page)).fields, {});
  // Repeated component-local IDs must remain addressable, including deep focus and explicit values.
  await page.setContent('<div id="first"></div><div id="second"></div>');
  await page.evaluate(() => {
    for (const id of ["first", "second"]) {
      document.getElementById(id).attachShadow({ mode: "open" }).innerHTML =
        '<label>Draft<input id="entry" value="private shadow value"></label><button id="action">Save</button>';
    }
  });
  await page.locator("#second").locator("#entry").focus();
  const shadow = await page.evaluate(probeUI);
  const entries = shadow.controls.filter((c) => c.tag === "input");
  assert.deepEqual(
    entries.map((c) => c.address),
    [
      ["#first", "#entry"],
      ["#second", "#entry"],
    ],
  );
  assert.equal(entries.find((c) => c.address[0] === "#second").focused, true);
  assert.equal(entries.find((c) => c.address[0] === "#first").focused, false);
  assert.equal(JSON.stringify(shadow).includes("private shadow value"), false);
  await assert.rejects(() => page.evaluate(probeUI, { scope: "#entry" }), /Ambiguous selector/);
  assert.equal((await page.evaluate(probeUI, { scope: ["#second", "#entry"] })).controls.length, 1);
  const selected = await checkpoint(page, { fields: [["#second", "#entry"]] });
  assert.equal(selected.fields['["#second","#entry"]'], "private shadow value");
  assert.equal(selected.activeElement, "entry");

  // A same-origin frame's facts stay local; a different port is a different origin.
  const other = Bun.serve({
    hostname: "127.0.0.1",
    port: 0,
    fetch: () =>
      new Response('<button id="foreign">Other origin</button>', {
        headers: { "content-type": "text/html" },
      }),
  });
  const host = Bun.serve({
    hostname: "127.0.0.1",
    port: 0,
    fetch: (req) =>
      new Response(
        new URL(req.url).pathname === "/child"
          ? '<style>body{margin:0}button{position:absolute;left:10px;top:15px}</style><button id="inner">Inner</button>'
          : `<iframe name="same" style="position:absolute;left:200px;top:100px" src="/child"></iframe><iframe name="foreign" src="${other.url}"></iframe><iframe name="opaque" sandbox="allow-scripts" srcdoc="<button>Sandboxed</button>"></iframe>`,
        { headers: { "content-type": "text/html" } },
      ),
  });
  try {
    await page.goto(host.url.href);
    await page.frameLocator('iframe[name="opaque"]').locator("button").waitFor();
    const opaqueFrame = await (
      await page.locator('iframe[name="opaque"]').elementHandle()
    ).contentFrame();
    assert.equal(await opaqueFrame.evaluate(() => window.origin), "null");
    const frames = await probeChildFrames(page);
    const same = frames.find((f) => f.name === "same");
    assert.equal(same.status, "probed");
    assert.equal(same.facts.controls.find((c) => c.locator === "#inner").box.x, 10);
    assert.equal(same.facts.controls.find((c) => c.locator === "#inner").box.y, 15);
    assert.equal(
      frames.find((f) => f.name === "foreign").status,
      "omitted-cross-origin-or-unapproved-parent",
    );
    assert.equal(
      frames.find((f) => f.name !== "same" && f.name !== "foreign").status,
      "omitted-cross-origin-or-unapproved-parent",
    );
  } finally {
    host.stop(true);
    other.stop(true);
  }
  console.log(
    "Browser probes: focus relation, intentional scroll, clipping, privacy, Shadow addresses/deep focus/checkpoints and independent frame coverage passed.",
  );
} finally {
  await browser.close();
}
