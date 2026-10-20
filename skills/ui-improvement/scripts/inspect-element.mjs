/** Pass directly to locator.evaluate(elementFacts). No clicks, focus or screenshots. */
export function elementFacts(el, { maxTextNodes = 200, maxLineRects = 500 } = {}) {
  const doc = el.ownerDocument,
    win = doc.defaultView;
  const style = win.getComputedStyle(el),
    rect = el.getBoundingClientRect();
  const round = (n) => Math.round(n * 100) / 100;
  const box = (r) =>
    Object.fromEntries(
      ["x", "y", "width", "height", "left", "right", "top", "bottom"].map((k) => [k, round(r[k])]),
    );
  const properties = [
    "display",
    "position",
    "boxSizing",
    "marginTop",
    "marginRight",
    "marginBottom",
    "marginLeft",
    "paddingTop",
    "paddingRight",
    "paddingBottom",
    "paddingLeft",
    "borderTopWidth",
    "borderRightWidth",
    "borderBottomWidth",
    "borderLeftWidth",
    "borderRadius",
    "width",
    "height",
    "minWidth",
    "minHeight",
    "maxWidth",
    "maxHeight",
    "fontFamily",
    "fontSize",
    "fontWeight",
    "lineHeight",
    "letterSpacing",
    "color",
    "backgroundColor",
    "backgroundImage",
    "appearance",
    "backgroundPositionX",
    "backgroundPositionY",
    "backgroundSize",
    "backgroundRepeat",
    "boxShadow",
    "outlineWidth",
    "outlineOffset",
    "outlineStyle",
    "overflowX",
    "overflowY",
    "whiteSpace",
    "textOverflow",
    "textWrap",
    "alignItems",
    "justifyContent",
    "gap",
    "transform",
    "opacity",
    "pointerEvents",
  ];
  const describe = (node) =>
    node ? { tag: node.localName, id: node.id || null, role: node.getAttribute("role") } : null;
  const parent = (node) => node.assignedSlot || node.parentElement || node.getRootNode().host;
  const related = (hit) => {
    for (let n = hit; n; n = parent(n)) if (n === el) return true;
    return false;
  };
  const hitAt = (x, y) => {
    let hit = doc.elementFromPoint(x, y);
    while (hit?.shadowRoot?.elementFromPoint) {
      const inner = hit.shadowRoot.elementFromPoint(x, y);
      if (!inner || inner === hit) break;
      hit = inner;
    }
    return hit;
  };
  const points = [
    [0.5, 0.5],
    [0.25, 0.25],
    [0.75, 0.25],
    [0.25, 0.75],
    [0.75, 0.75],
  ].map(([x, y]) => ({
    x: round(rect.left + rect.width * x),
    y: round(rect.top + rect.height * y),
  }));
  const hitTests = points.map((p) => {
    if (p.x < 0 || p.y < 0 || p.x >= win.innerWidth || p.y >= win.innerHeight)
      return { ...p, status: "outside-current-viewport" };
    const hit = hitAt(p.x, p.y);
    return {
      ...p,
      status: related(hit) ? "target-or-composed-descendant" : "other-hit-target",
      hit: describe(hit),
    };
  });
  const walker = doc.createTreeWalker(el, win.NodeFilter.SHOW_TEXT);
  const fragments = [];
  let textNodes = 0,
    rects = 0,
    characters = 0,
    truncated = false;
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (
      !node.textContent.trim() ||
      node.parentElement.closest("input,textarea,select,option,script,style")
    )
      continue;
    if (textNodes >= maxTextNodes) {
      truncated = true;
      break;
    }
    textNodes++;
    characters += node.textContent.length;
    const range = doc.createRange();
    range.selectNodeContents(node);
    for (const r of range.getClientRects()) {
      if (rects >= maxLineRects) {
        truncated = true;
        break;
      }
      if (!r.width || !r.height) continue;
      rects++;
      fragments.push(box(r));
    }
    if (truncated) break;
  }
  const svgs = (el.localName === "svg" ? [el] : [...el.querySelectorAll("svg")])
    .slice(0, 20)
    .map((svg) => {
      try {
        const b = svg.getBBox(),
          matrix = svg.getScreenCTM(),
          corners = matrix
            ? [
                [b.x, b.y],
                [b.x + b.width, b.y],
                [b.x, b.y + b.height],
                [b.x + b.width, b.y + b.height],
              ].map(([x, y]) => new win.DOMPoint(x, y).matrixTransform(matrix))
            : [];
        const view = svg.viewBox.baseVal;
        return {
          box: box(svg.getBoundingClientRect()),
          viewBox: { x: view.x, y: view.y, width: view.width, height: view.height },
          fillBBox: { x: b.x, y: b.y, width: b.width, height: b.height },
          viewportCorners: corners.map((p) => ({ x: round(p.x), y: round(p.y) })),
          bboxMode:
            "Default getBBox: fill geometry, not verified stroke/filter/mask or optical weight",
        };
      } catch (error) {
        return { unavailable: error.message };
      }
    });
  const ancestors = [];
  for (let n = parent(el), i = 0; n && i < 4; n = parent(n), i++) {
    const s = win.getComputedStyle(n);
    ancestors.push({
      ...describe(n),
      box: box(n.getBoundingClientRect()),
      display: s.display,
      overflowX: s.overflowX,
      overflowY: s.overflowY,
      transform: s.transform,
    });
  }
  const animations = el.getAnimations({ subtree: true }).map((a) => ({
    playState: a.playState,
    pending: a.pending,
    timing: a.effect?.getComputedTiming()
      ? {
          duration: a.effect.getComputedTiming().duration,
          iterations: a.effect.getComputedTiming().iterations,
          progress: a.effect.getComputedTiming().progress,
        }
      : null,
  }));
  return {
    element: describe(el),
    url: doc.URL,
    coordinateSpace: "This document viewport CSS pixels",
    box: box(rect),
    computed: Object.fromEntries(properties.map((k) => [k, style[k]])),
    scroll: {
      left: el.scrollLeft,
      top: el.scrollTop,
      clientWidth: el.clientWidth,
      clientHeight: el.clientHeight,
      scrollWidth: el.scrollWidth,
      scrollHeight: el.scrollHeight,
    },
    ancestors,
    text: {
      characters,
      textNodes,
      fragments,
      truncated,
      limits:
        "Range boxes, not ink; no input/textarea/select contents; light DOM under target only",
    },
    svg: { items: svgs, truncated: el.querySelectorAll("svg").length > 20 },
    hitTests,
    animations,
    limits: [
      "Pointer hit tests exclude pointer-events:none painting and sample only five current points.",
      "Frame-local geometry does not establish outer-frame visibility.",
      "SVG fill boxes and Range fragments are not optical balance or painted-pixel proof.",
      "Animation inventory does not cover every JS/canvas/media effect.",
    ],
  };
}

/** Use an existing Page/Frame and an explicit CSS/Shadow address. */
export function locate(context, address) {
  const parts = Array.isArray(address) ? address : [address];
  if (!parts.length) throw new Error("Element address cannot be empty");
  let result = context.locator(parts[0]);
  for (const part of parts.slice(1)) result = result.locator(part);
  return result;
}

/** Optional operations are explicit: trial may scroll; capture may scroll and waits. */
export async function inspectElement(
  locator,
  { trial = false, semantics = false, screenshot = null } = {},
) {
  let actionability = null;
  if (trial) {
    try {
      await locator.click({ trial: true, timeout: 1500 });
      actionability = { ready: true };
    } catch (error) {
      actionability = { ready: false, error: error.message.slice(0, 1800) };
    }
  }
  let capture = null;
  if (screenshot) {
    const padding = screenshot.padding ?? 0;
    if (!Number.isFinite(padding) || padding < 0)
      throw new Error("Screenshot padding must be nonnegative");
    if (!padding) {
      await locator.screenshot({ path: screenshot.path });
      capture = { path: screenshot.path, kind: "element" };
    } else {
      await locator.scrollIntoViewIfNeeded();
      const bounds = await locator.boundingBox();
      if (!bounds) throw new Error("Element has no screenshot bounds");
      const page = locator.page(),
        v =
          page.viewportSize() ||
          (await page.evaluate(() => ({ width: innerWidth, height: innerHeight })));
      const x = Math.max(0, bounds.x - padding),
        y = Math.max(0, bounds.y - padding);
      const clip = {
        x,
        y,
        width: Math.min(v.width, bounds.x + bounds.width + padding) - x,
        height: Math.min(v.height, bounds.y + bounds.height + padding) - y,
      };
      if (clip.width <= 0 || clip.height <= 0)
        throw new Error("Element remains outside screenshot viewport");
      await page.screenshot({ path: screenshot.path, clip });
      capture = { path: screenshot.path, kind: "viewport-crop", clip };
    }
  }
  const facts = await locator.evaluate(elementFacts);
  const aria = semantics ? await locator.ariaSnapshot() : null;
  return {
    facts,
    actionability,
    semantics:
      aria === null
        ? null
        : { source: "Playwright DOM-computed ARIA snapshot; may contain values", snapshot: aria },
    capture,
  };
}
