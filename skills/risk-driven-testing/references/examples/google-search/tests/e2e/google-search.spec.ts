// Behavior: ../../specs/stories/google-search.yaml. Local tests intercept every network request.
import { test, expect } from 'playwright/test';
import { runStory, FIRST_QUERY, SECOND_QUERY } from './flows/google-search.ts';
import { installStubRoutes } from './fixtures/google-search-seam.ts';
import * as actions from './actions/google-search.ts';

test.describe('SEAM local replay', () => {
  test('same links rendered after the new document response can reach the docs', async ({ page }) => {
    const searches: string[] = [];
    page.on('request', request => {
      const url = new URL(request.url());
      if (url.hostname === 'www.google.com' && url.pathname === '/search') {
        searches.push(url.searchParams.get('q') ?? '');
      }
    });
    await installStubRoutes(page);
    await runStory(page, 1_000);
    expect(searches).toEqual([FIRST_QUERY, SECOND_QUERY]);
    await expect(page).toHaveURL('https://playwright.dev/docs/locators');
  });

  test('opens the official result when another link has the same text', async ({ page }) => {
    await installStubRoutes(page, { duplicateLocatorText: true });
    await runStory(page, 1_000);
    await expect(page).toHaveURL('https://playwright.dev/docs/locators');
  });

  test('pushState and changed old links do not establish a new search', async ({ page }) => {
    const searches: string[] = [];
    page.on('request', request => {
      const url = new URL(request.url());
      if (url.hostname === 'www.google.com' && url.pathname === '/search') {
        searches.push(url.searchParams.get('q') ?? '');
      }
    });
    await installStubRoutes(page, { frozen: true });
    await actions.openGoogleHome(page);
    expect(await actions.submitSearch(page, FIRST_QUERY, 2_000)).toBe(true);
    const before = await actions.resultLinks(page);
    expect(await actions.submitSearch(page, SECOND_QUERY, 1_000)).toBe(false);
    expect(new URL(page.url()).searchParams.get('q')).toBe(SECOND_QUERY);
    await expect(page).toHaveTitle(`${SECOND_QUERY} - Google Search`);
    const after = await actions.resultLinks(page);
    expect(after.length).toBeGreaterThan(before.length);
    expect(after.some(actions.isLocatorsDocLink)).toBe(true);
    expect(searches).toEqual([FIRST_QUERY]);
  });

  test('an unrelated page on the official domain is not a documentation result', async ({ page }) => {
    await installStubRoutes(page, { unrelatedFirstResults: true });
    await expect(runStory(page, 1_000)).rejects.toThrow('Search results include a page relevant to Playwright browser automation documentation');
  });

  test('full flow reports insufficient refresh evidence as unknown', async ({ page }) => {
    await installStubRoutes(page, { frozen: true });
    await runStory(page, 1_000);
  });

  test('empty result area remains unknown', async ({ page }) => {
    await installStubRoutes(page, { emptySecondResults: true });
    await runStory(page, 1_000);
  });
});

test('real Google flow', async ({ page }) => {
  test.skip(process.env.RDT_REAL !== '1', 'Real Google replay requires explicit opt-in');
  await runStory(page);
});
