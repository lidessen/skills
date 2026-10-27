// Local stub pages and routes for the projection's isolated tests. All network requests are
// intercepted: Google and Playwright pages use local HTML; all other requests are aborted.
//
// Scenarios check that a new document response, rather than a change to the link set, is the
// refresh evidence: identical links after navigation are valid; changes to old links following
// pushState are not. An empty second result list leaves the observation unknown.
import type { Page } from 'playwright';

export interface SeamOptions {
  /** The second submission updates the URL, title and old list without navigating. */
  frozen?: boolean;
  /** Return an empty result list on the second search. */
  emptySecondResults?: boolean;
  /** First result points to an unrelated page on the official domain. */
  unrelatedFirstResults?: boolean;
  /** A different site has a result with the same visible text as the locator docs. */
  duplicateLocatorText?: boolean;
  /** Hidden official results precede a visible locator documentation result. */
  hiddenDuplicateLocator?: boolean;
}

const HOME_HTML = `<!doctype html><html><head><title>Google</title></head><body>
<form action="/search" method="get">
  <input name="q" type="text" aria-label="Search" role="combobox" placeholder="Search">
  <input type="submit" value="Google Search">
</form>
</body></html>`;

/** The same results can legitimately appear after both search navigations. */
const RESULTS_LIST =
  '<a href="https://playwright.dev/docs/intro">Playwright documentation — browser automation</a>' +
  '<a href="https://playwright.dev/docs/locators">Locators | Playwright</a>';

/** Change the URL, title and old list without issuing the second search. */
const MUTATE_SCRIPT = `<script>
document.querySelector('form').addEventListener('submit', (event) => {
  event.preventDefault();
  const query = document.querySelector('input[name=q]').value;
  history.pushState(null, '', '/search?q=' + encodeURIComponent(query));
  document.title = query + ' - Google Search';
  setTimeout(() => {
    const a = document.createElement('a');
    a.href = 'https://playwright.dev/docs/api/class-locator';
    a.textContent = 'Locator API | Playwright';
    document.querySelector('#search').appendChild(a);
  }, 50);
});
</script>`;

function resultsHTML(query: string, opts: SeamOptions, searchCount: number): string {
  const q = escapeHtml(query);
  const form = `<form action="/search" method="get"><input name="q" type="text" aria-label="Search" role="combobox" value="${q}"></form>`;
  const duplicateLink = opts.duplicateLocatorText && searchCount >= 2
    ? '<a href="https://example.org/other">Locators | Playwright</a>'
    : '';
  const hiddenDuplicate = opts.hiddenDuplicateLocator && searchCount >= 2
    ? '<a hidden href="https://playwright.dev/docs/api/class-locator">Locator API | Playwright</a>' +
      '<a hidden href="https://playwright.dev/docs/locators">Locators | Playwright</a>'
    : '';
  const list = opts.unrelatedFirstResults && searchCount === 1
    ? '<a href="https://playwright.dev/unrelated">Careers</a>'
    : opts.emptySecondResults && searchCount >= 2 ? '' : duplicateLink + hiddenDuplicate + RESULTS_LIST;
  return `<!doctype html><html><head><title>${q} - Google Search</title></head><body>
${form}
<main id="search">${searchCount >= 2 && !opts.emptySecondResults ? '' : list}</main>
${searchCount >= 2 && !opts.emptySecondResults ? `<template id="delayed-results">${list}</template>
<script>setTimeout(() => document.querySelector('#search').append(
  document.querySelector('#delayed-results').content.cloneNode(true)), 500);</script>` : ''}
${opts.frozen ? MUTATE_SCRIPT : ''}
</body></html>`;
}

const LOCATORS_DOCS_HTML = `<!doctype html><html><head><title>Locators | Playwright</title></head><body>
<h1>Locators</h1>
<p>Playwright locator 用于定位页面元素：const locator = page.getByRole('link', { name: 'start' });</p>
<p>也可用 getByTestId()、getByLabel() 或 page.locator() 精确定位。</p>
<p>这就是 Playwright locator 的用法介绍。</p>
</body></html>`;

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** Stub Google and Playwright pages and abort all other requests. */
export async function installStubRoutes(page: Page, opts: SeamOptions = {}): Promise<void> {
  let searchCount = 0;
  await page.route('**/*', async (route) => {
    const url = new URL(route.request().url());
    const host = url.hostname.replace(/^www\./, '');
    if (host === 'google.com') {
      if (url.pathname === '/search') {
        searchCount += 1;
        await route.fulfill({
          status: 200,
          contentType: 'text/html',
          body: resultsHTML(url.searchParams.get('q') ?? '', opts, searchCount),
        });
      } else {
        await route.fulfill({ status: 200, contentType: 'text/html', body: HOME_HTML });
      }
      return;
    }
    if (host === 'playwright.dev') {
      await route.fulfill({ status: 200, contentType: 'text/html', body: LOCATORS_DOCS_HTML });
      return;
    }
    await route.abort();
  });
}
