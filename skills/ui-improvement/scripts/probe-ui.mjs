/** Serializable, read-only browser function: await page.evaluate(probeUI, options).
 * No screenshots, clicks, focus changes, form values or style mutations.
 */
export function probeUI({ scope = "body", maxElements = 5000 } = {}) {
  if (!Number.isInteger(maxElements) || maxElements < 1)
    throw new Error("maxElements must be a positive integer");
  const deepElements = (start) => {
    const result = [start];
    for (let i = 0; i < result.length; i++) {
      result.push(...result[i].children);
      if (result[i].shadowRoot) result.push(...result[i].shadowRoot.children);
    }
    return result;
  };
  const resolve = (address) => {
    if (Array.isArray(address)) {
      let current = document;
      for (const [i, part] of address.entries()) {
        const matches = current.querySelectorAll(part);
        if (matches.length !== 1)
          throw new Error(`Address segment must match one element: ${part}`);
        current = i === address.length - 1 ? matches[0] : matches[0].shadowRoot;
        if (!current) throw new Error(`Open Shadow root unavailable: ${part}`);
      }
      return current;
    }
    const matches = deepElements(document.documentElement).filter((el) => el.matches(address));
    if (matches.length > 1) throw new Error(`Ambiguous selector; use explicit address: ${address}`);
    return matches[0];
  };
  const root = resolve(scope);
  if (!root) throw new Error(`Scope not found: ${scope}`);
  const round = (n) => Math.round(n * 100) / 100;
  const box = (r) =>
    Object.fromEntries(
      ["x", "y", "width", "height", "left", "right", "top", "bottom"].map((k) => [k, round(r[k])]),
    );
  const localSelector = (el) => {
    if (el === document.documentElement) return "html";
    if (el.id && el.getRootNode().querySelectorAll(`#${CSS.escape(el.id)}`).length === 1)
      return `#${CSS.escape(el.id)}`;
    const parts = [];
    for (let node = el; node && node !== document.documentElement; node = node.parentElement) {
      if (node.id) {
        parts.unshift(`#${CSS.escape(node.id)}`);
        break;
      }
      const siblings = [...(node.parentElement || node.getRootNode()).children].filter(
        (n) => n.tagName === node.tagName,
      );
      parts.unshift(`${node.localName}:nth-of-type(${siblings.indexOf(node) + 1})`);
    }
    return parts.join(" > ");
  };
  const addressOf = (el) => {
    const host = el.getRootNode().host;
    return [...(host ? addressOf(host) : []), localSelector(el)];
  };
  const locator = (el) => addressOf(el).join(" >> ");
  const composedParent = (el) => el.assignedSlot || el.parentElement || el.getRootNode().host;
  const styledVisible = (el) => {
    if (getComputedStyle(el).visibility !== "visible") return false;
    for (let n = el; n; n = composedParent(n)) {
      const s = getComputedStyle(n);
      if (s.display === "none" || Number(s.opacity) === 0) return false;
    }
    return true;
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    return !!(r.width && r.height && el.getClientRects().length && styledVisible(el));
  };
  const textBoxes = (label, control) => {
    const walker = document.createTreeWalker(label, NodeFilter.SHOW_TEXT);
    const boxes = [],
      words = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.textContent.trim() || control.contains(node) || !styledVisible(node.parentElement))
        continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      words.push(node.textContent.trim());
      for (const r of range.getClientRects()) if (r.width && r.height) boxes.push(box(r));
    }
    return { boxes, text: words.join(" ").replace(/\s+/g, " ").slice(0, 80) };
  };
  const distance = (a, b) =>
    Math.hypot(
      Math.max(a.left - b.right, b.left - a.right, 0),
      Math.max(a.top - b.bottom, b.top - a.bottom, 0),
    );
  const all = deepElements(root);
  const examined = all.slice(0, maxElements);
  const elements = examined.filter(visible);
  const controls = [],
    overflow = [],
    scrollers = [],
    candidates = [];
  const shadows = examined.filter((el) => el.shadowRoot).length;
  const frames = examined.filter((el) => el.localName === "iframe").length;
  for (const el of elements) {
    const s = getComputedStyle(el),
      r = el.getBoundingClientRect(),
      id = locator(el);
    const extraX = el.scrollWidth - el.clientWidth,
      extraY = el.scrollHeight - el.clientHeight;
    if (extraX > 1 && el.clientWidth > 0)
      overflow.push({
        locator: id,
        extraX,
        overflowX: s.overflowX,
        box: box(r),
        kind: ["auto", "scroll"].includes(s.overflowX)
          ? "scrollable"
          : "inspect-clipping-or-expansion",
      });
    if (
      (extraY > 1 && ["auto", "scroll"].includes(s.overflowY)) ||
      (extraX > 1 && ["auto", "scroll"].includes(s.overflowX))
    )
      scrollers.push({
        locator: id,
        scrollTop: el.scrollTop,
        scrollLeft: el.scrollLeft,
        clientHeight: el.clientHeight,
        scrollHeight: el.scrollHeight,
        overflowX: s.overflowX,
        overflowY: s.overflowY,
      });
    if (
      !el.matches(
        'button,a[href],input:not([type="hidden"]),select,textarea,[role="button"],[role="combobox"],[role="radio"],[role="tab"]',
      )
    )
      continue;
    const labels = [...(el.labels || [])].map((label) => {
      const content = textBoxes(label, el);
      return {
        locator: locator(label),
        text: content.text,
        fontSize: getComputedStyle(label).fontSize,
        textBoxes: content.boxes,
      };
    });
    let active = document.activeElement;
    while (active?.shadowRoot?.activeElement) active = active.shadowRoot.activeElement;
    const focused = active === el;
    const outlineExtent =
      s.outlineStyle === "none"
        ? 0
        : Math.max(0, parseFloat(s.outlineWidth) + parseFloat(s.outlineOffset));
    const gaps = labels.flatMap((label) => label.textBoxes.map((b) => round(distance(b, r))));
    const control = {
      locator: id,
      address: addressOf(el),
      tag: el.localName,
      role: el.getAttribute("role"),
      box: box(r),
      fontSize: s.fontSize,
      lineHeight: s.lineHeight,
      padding: [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft],
      border: [s.borderTopWidth, s.borderRightWidth, s.borderBottomWidth, s.borderLeftWidth],
      appearance: s.appearance,
      transform: s.transform,
      labels,
      labelGap: gaps.length ? Math.min(...gaps) : null,
      focused,
      focusVisible: el.matches(":focus-visible"),
      outline: {
        width: s.outlineWidth,
        offset: s.outlineOffset,
        style: s.outlineStyle,
        extent: round(outlineExtent),
      },
      outsideViewportX: r.left < 0 || r.right > innerWidth,
      declaredName: {
        ariaLabel: el.getAttribute("aria-label"),
        ariaLabelledby: el.getAttribute("aria-labelledby"),
        title: el.getAttribute("title"),
      },
      state: {
        disabled: el.matches(":disabled"),
        ariaDisabled: el.getAttribute("aria-disabled"),
        ariaExpanded: el.getAttribute("aria-expanded"),
        checked: "checked" in el ? el.checked : null,
        invalid: el.getAttribute("aria-invalid"),
      },
    };
    if (el.localName === "select") {
      const canvas = document.createElement("canvas"),
        context = canvas.getContext("2d");
      context.font = `${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
      const text = el.selectedOptions[0]?.textContent || "";
      control.nativeParts = {
        arrowGeometry: "unavailable",
        popupGeometry: "unavailable",
        optionCount: el.options.length,
        selectedTextWidthEstimate: round(context.measureText(text).width),
        contentWidthBeforeNativeParts: round(
          el.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight),
        ),
        estimateCaveat:
          "Untransformed layout CSS pixels, not native glyph bounds; arrow reservation unknown.",
      };
    }
    control.layoutGroups = [];
    for (
      let parent = composedParent(el), depth = 0;
      parent && depth < 3;
      parent = composedParent(parent), depth++
    ) {
      const style = getComputedStyle(parent);
      if (!["flex", "inline-flex", "grid", "inline-grid"].includes(style.display)) continue;
      control.layoutGroups.push({
        locator: locator(parent),
        display: style.display,
        gap: style.gap,
        alignItems: style.alignItems,
        children: [...parent.children].filter(visible).map((child) => ({
          locator: locator(child),
          box: box(child.getBoundingClientRect()),
          fontSize: getComputedStyle(child).fontSize,
        })),
      });
    }
    controls.push(control);
    if (focused && control.labelGap !== null && outlineExtent > control.labelGap)
      candidates.push({
        kind: "focus-outline-near-label",
        locator: id,
        evidence: { labelGap: control.labelGap, outlineExtent: round(outlineExtent) },
        interpretation:
          "Bounding outline reaches label text space; check shape and intended grouping. Not a universal spacing violation.",
      });
  }
  const documentWidth = Math.max(
    document.documentElement.scrollWidth,
    document.body?.scrollWidth || 0,
  );
  return {
    viewport: { width: innerWidth, height: innerHeight },
    coordinateSpace: "viewport CSS pixels",
    document: {
      width: documentWidth,
      extraX: Math.max(0, documentWidth - innerWidth),
      scrollX,
      scrollY,
    },
    coverage: {
      scope,
      examined: Math.min(all.length, maxElements),
      total: all.length,
      truncated: all.length > maxElements,
      shadowHosts: shadows,
      shadowContents: "Open roots enumerated; see truncated for node coverage",
      closedShadowHosts: "unknown",
      frames,
    },
    controls,
    overflow,
    scrollers,
    candidates,
    limits: [
      "Current DOM state only; offscreen elements included, occlusion not reconstructed.",
      "Closed shadow roots are unknown; frame contents require their own probe and coordinate space.",
      "Native control internal arrow/menu geometry, optical baselines and visual harmony are not measurable here.",
      "Scrollable overflow can be intentional; focus overlap is a candidate, not an automatic repair.",
    ],
  };
}

/** Explicitly requested fields only; may contain user data. No interaction. */
export async function checkpoint(page, { fields = [], scrollers = [] } = {}) {
  return page.evaluate(
    ({ fields, scrollers }) => {
      const read = (selector) => {
        let root = document,
          el;
        const parts = Array.isArray(selector) ? selector : [selector];
        if (!parts.length) throw new Error("Checkpoint address cannot be empty");
        for (const [index, part] of parts.entries()) {
          const matches = root.querySelectorAll(part);
          if (matches.length !== 1)
            throw new Error(`Checkpoint selector must match one element: ${part}`);
          el = matches[0];
          if (index < parts.length - 1) {
            root = el.shadowRoot;
            if (!root) throw new Error(`Open Shadow root unavailable: ${part}`);
          }
        }
        return el;
      };
      const key = (selector) => (Array.isArray(selector) ? JSON.stringify(selector) : selector);
      let active = document.activeElement;
      while (active?.shadowRoot?.activeElement) active = active.shadowRoot.activeElement;
      return {
        window: { x: scrollX, y: scrollY },
        activeElement: active?.id || active?.tagName,
        fields: Object.fromEntries(
          fields.map((selector) => {
            const el = read(selector);
            return [key(selector), "value" in el ? el.value : el.textContent];
          }),
        ),
        scrollers: Object.fromEntries(
          scrollers.map((selector) => {
            const el = read(selector);
            return [
              key(selector),
              {
                top: el.scrollTop,
                left: el.scrollLeft,
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight,
              },
            ];
          }),
        ),
      };
    },
    { fields, scrollers },
  );
}

/** Same-origin child frames, independently measured in their own coordinate spaces. */
export async function probeChildFrames(page, options = {}) {
  const permitted = new Set([page.mainFrame()]),
    results = [];
  let origin;
  try {
    origin = new URL(page.url()).origin;
  } catch {
    origin = null;
  }
  const pending = page.frames().filter((f) => f !== page.mainFrame());
  while (pending.length) {
    const index = pending.findIndex(
      (f) => f.parentFrame() === page.mainFrame() || !pending.includes(f.parentFrame()),
    );
    if (index < 0) break;
    const frame = pending.splice(index, 1)[0],
      url = frame.url();
    const inherited = url === "about:blank" || url === "about:srcdoc";
    let frameOrigin;
    try {
      frameOrigin = new URL(url).origin;
    } catch {
      frameOrigin = null;
    }
    if (
      !permitted.has(frame.parentFrame()) ||
      (!inherited && (!origin || frameOrigin !== origin))
    ) {
      results.push({
        url,
        name: frame.name(),
        status: "omitted-cross-origin-or-unapproved-parent",
      });
      continue;
    }
    try {
      // about:srcdoc/blank can inherit or become opaque through sandboxing.
      // URL equality alone does not establish this document's effective origin.
      const effectiveOrigin = await frame.evaluate(() => window.origin);
      if (!origin || origin === "null" || effectiveOrigin !== origin) {
        results.push({
          url,
          name: frame.name(),
          status: "omitted-cross-origin-or-unapproved-parent",
        });
        continue;
      }
      permitted.add(frame);
      results.push({
        url,
        name: frame.name(),
        status: "probed",
        facts: await frame.evaluate(probeUI, options),
      });
    } catch (error) {
      results.push({ url, name: frame.name(), status: "unavailable", error: error.message });
    }
  }
  return results;
}
