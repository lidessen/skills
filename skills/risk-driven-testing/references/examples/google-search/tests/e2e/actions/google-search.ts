import { errors, type Page } from 'playwright';

export const GOOGLE_HOME = 'https://www.google.com/';
const DEFAULT_TIMEOUT = 30_000;

export interface ResultLink {
  href: string;
  rawHref: string | null;
  text: string;
}

export function searchBox(page: Page) {
  return page.getByRole('combobox', { name: 'Search' });
}

function isHost(url: string, host: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' && parsed.hostname.replace(/^www\./, '') === host;
  } catch {
    return false;
  }
}

export const isGoogleHome = (url: string) => isHost(url, 'google.com');
export const isPlaywrightDevHost = (url: string) => isHost(url, 'playwright.dev');

export function isDocsLink(link: ResultLink): boolean {
  return (isPlaywrightDevHost(link.href) && /^\/docs(?:\/|$)/.test(new URL(link.href).pathname)) ||
    (link.href.startsWith('https://') && /playwright/i.test(link.text) && /documentation|\bdocs\b/i.test(link.text));
}

export function isLocatorsDocLink(link: ResultLink): boolean {
  return isPlaywrightDevHost(link.href) && /locator/i.test(link.href + ' ' + link.text);
}

export async function detectInterruption(page: Page): Promise<string | null> {
  if (new URL(page.url()).pathname.startsWith('/sorry')) return 'Google traffic verification page';
  const text = (await page.locator('body').innerText()).slice(0, 8000);
  if (/unusual traffic|not a robot/i.test(text)) return 'Google traffic verification page';
  if (/before you continue/i.test(text) || new URL(page.url()).hostname === 'consent.google.com') {
    return 'Google consent page';
  }
  return null;
}

export async function openGoogleHome(page: Page): Promise<string | null> {
  await page.goto(GOOGLE_HOME, { waitUntil: 'domcontentloaded' });
  return detectInterruption(page);
}

// A new main-document response bound to this query proves a fresh document was loaded.
// Same-document URL changes and changes to the old links cannot prove it.
export async function submitSearch(page: Page, query: string, timeout = DEFAULT_TIMEOUT): Promise<boolean> {
  const box = searchBox(page);
  await box.waitFor({ state: 'visible', timeout });
  await box.fill(query);
  const response = page.waitForResponse(candidate => {
    const request = candidate.request();
    const url = new URL(candidate.url());
    return request.isNavigationRequest() && request.frame() === page.mainFrame() &&
      ((url.hostname.replace(/^www\./, '') === 'google.com' && url.pathname === '/search' &&
        url.searchParams.get('q') === query) || url.pathname.startsWith('/sorry') ||
        url.hostname === 'consent.google.com');
  }, { timeout }).catch((error: unknown) => {
    if (error instanceof errors.TimeoutError) return null;
    throw error;
  });
  const [navigation] = await Promise.all([response, box.press('Enter')]);
  if (!navigation) return false;
  await page.waitForLoadState('domcontentloaded', { timeout });
  if (await detectInterruption(page)) return false;
  if (!navigation.ok()) throw new Error(`Search navigation failed with HTTP ${navigation.status()}`);
  return new URL(navigation.url()).searchParams.get('q') === query && page.url() === navigation.url();
}

// Resolve Google's redirect links before checking the destination host.
export async function resultLinks(page: Page, timeout = DEFAULT_TIMEOUT): Promise<ResultLink[]> {
  try {
    await page.locator('#search a[href]').first().waitFor({ state: 'attached', timeout });
  } catch (error: unknown) {
    if (error instanceof errors.TimeoutError) return [];
    throw error;
  }
  return page.locator('#search a[href]').evaluateAll(anchors => {
    const links: Array<{ href: string; rawHref: string | null; text: string }> = [];
    for (const anchor of anchors) {
      if (!(anchor instanceof HTMLAnchorElement)) continue;
      const target = new URL(anchor.href);
      let href = target.href;
      if (target.hostname === 'google.com' || target.hostname.endsWith('.google.com')) {
        if (target.pathname !== '/url' || !target.searchParams.get('q')) continue;
        href = target.searchParams.get('q') as string;
      }
      if (!href.startsWith('https://')) continue;
      links.push({ href, rawHref: anchor.getAttribute('href'), text: (anchor.innerText || anchor.textContent || '').trim() });
    }
    return links;
  });
}

export async function openLocatorsDoc(page: Page): Promise<boolean> {
  const target = (await resultLinks(page)).find(isLocatorsDocLink);
  if (!target?.rawHref) return false;
  // Select by the inspected href so another result with identical text cannot shadow it.
  for (const anchor of await page.locator('#search a[href]').elementHandles()) {
    if (await anchor.getAttribute('href') !== target.rawHref) continue;
    await anchor.click();
    await page.waitForURL(url => isPlaywrightDevHost(url.toString()));
    await page.waitForLoadState('domcontentloaded');
    return true;
  }
  return false;
}
