/** Read-only browser function. Pass to the browser tool's evaluate API.
 * Coordinates are viewport CSS pixels; no DOM/style changes or text export.
 * Open the target frame as a standalone page when frame coordinates differ.
 */
function collectRegions() {
  const regions = [];
  const warnings = new Set();
  const controlSelector =
    'button,input:not([type="hidden"]),select,textarea,[role="button"],[role="tab"],[role="checkbox"],[role="switch"],[role="combobox"]';
  const mediaSelector = "img,svg,video,canvas,iframe";
  const solid = (color) => {
    const match = color.match(/^rgba?\(([^)]+)\)$/);
    if (!match) return null;
    const values = match[1].split(",").map(Number);
    if (values.length === 4 && values[3] < 1) return null;
    return (
      "#" +
      values
        .slice(0, 3)
        .map((v) => Math.round(v).toString(16).padStart(2, "0"))
        .join("")
    );
  };
  const add = (kind, rect, element, fill) => {
    let left = Math.max(0, rect.left),
      top = Math.max(0, rect.top);
    let right = Math.min(innerWidth, rect.right),
      bottom = Math.min(innerHeight, rect.bottom);
    for (let parent = element; parent; parent = parent.parentElement) {
      const style = getComputedStyle(parent),
        bounds = parent.getBoundingClientRect();
      if (style.display === "none" || style.visibility !== "visible" || Number(style.opacity) === 0)
        return;
      if (style.overflowX !== "visible") {
        left = Math.max(left, bounds.left + parent.clientLeft);
        right = Math.min(right, bounds.left + parent.clientLeft + parent.clientWidth);
      }
      if (style.overflowY !== "visible") {
        top = Math.max(top, bounds.top + parent.clientTop);
        bottom = Math.min(bottom, bounds.top + parent.clientTop + parent.clientHeight);
      }
    }
    if (right > left && bottom > top)
      regions.push({
        kind,
        box: [left, top, right - left, bottom - top],
        ...(fill ? { fill } : {}),
      });
  };
  for (const element of document.body.querySelectorAll("*")) {
    if (!(element instanceof HTMLElement || element instanceof SVGElement)) continue;
    if (element.closest('script,style,noscript,[aria-hidden="true"]')) continue;
    // Media and native controls are atomic; do not paint their inner markup twice.
    if (element.parentElement?.closest(mediaSelector + "," + controlSelector)) continue;
    const style = getComputedStyle(element),
      rect = element.getBoundingClientRect();
    if (element.shadowRoot) warnings.add("Shadow DOM contents omitted");
    if (style.transform !== "none") warnings.add("Transformed elements use axis-aligned bounds");
    if (element.matches(mediaSelector)) {
      add("media", rect, element);
      continue;
    }
    if (element.matches(controlSelector)) {
      add("control", rect, element);
      continue;
    }
    const fill = solid(style.backgroundColor);
    if (fill) add("surface", rect, element, fill);
    if (style.backgroundImage !== "none") {
      add("media", rect, element);
      warnings.add("Background images represented as media bounds");
    }
    for (const node of element.childNodes) {
      if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const line of range.getClientRects()) add("text", line, element);
    }
  }
  return {
    image_size: [innerWidth, innerHeight],
    background:
      solid(getComputedStyle(document.body).backgroundColor) ||
      solid(getComputedStyle(document.documentElement).backgroundColor) ||
      "#ffffff",
    coordinate_space: "viewport CSS pixels",
    regions,
    warnings: [
      ...warnings,
      "Controls are atomic blocks: their labels are not included in text view",
      "Pseudo-elements, occlusion and complex clip paths are not reconstructed",
    ],
  };
}
