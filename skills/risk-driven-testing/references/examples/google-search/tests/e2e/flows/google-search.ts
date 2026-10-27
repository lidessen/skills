// Behavior: ../../../specs/stories/google-search.yaml. The caller owns the supplied page.
import { test, expect } from 'playwright/test';
import type { Page } from 'playwright';
import * as actions from '../actions/google-search.ts';

export const FIRST_QUERY = 'Playwright documentation';
export const SECOND_QUERY = 'Playwright locators documentation';

export async function runStory(page: Page, timeout = 30_000): Promise<void> {
  // Context: start on Google with a usable search box.
  const homeBlocked = await actions.openGoogleHome(page);
  if (homeBlocked) test.skip(true, `BLOCKED: ${homeBlocked}`);
  expect(actions.isGoogleHome(page.url())).toBe(true);
  await expect(actions.searchBox(page)).toBeVisible();

  // Search for Playwright documentation.
  const firstNavigation = await actions.submitSearch(page, FIRST_QUERY, timeout);
  const firstBlocked = await actions.detectInterruption(page);
  if (firstBlocked) test.skip(true, `BLOCKED: ${firstBlocked}`);
  if (!firstNavigation) test.skip(true, 'UNKNOWN: no successful main-document response for the first query');
  await expect(actions.searchBox(page)).toHaveValue(FIRST_QUERY);
  expect(new URL(page.url()).searchParams.get('q')).toBe(FIRST_QUERY);
  const firstLinks = await actions.resultLinks(page, timeout);
  if (firstLinks.length === 0) test.skip(true, 'UNKNOWN: no first-search result links observed');
  await expect.poll(async () => (await actions.resultLinks(page, timeout)).some(actions.isDocsLink), {
    timeout,
    message: 'Search results include a page relevant to Playwright browser automation documentation',
  }).toBe(true);

  // Replace the entire query and submit again.
  const secondNavigation = await actions.submitSearch(page, SECOND_QUERY, timeout);
  const secondBlocked = await actions.detectInterruption(page);
  if (secondBlocked) test.skip(true, `BLOCKED: ${secondBlocked}`);
  if (!secondNavigation) test.skip(true, 'UNKNOWN: no successful main-document response for the second query');
  await expect(actions.searchBox(page)).toHaveValue(SECOND_QUERY);
  expect(new URL(page.url()).searchParams.get('q')).toBe(SECOND_QUERY);
  const links = await actions.resultLinks(page, timeout);
  if (links.length === 0) test.skip(true, 'UNKNOWN: no result links observed in the new document');
  await expect.poll(async () => (await actions.resultLinks(page, timeout)).some(actions.isLocatorsDocLink), {
    timeout,
    message: 'Updated results include Playwright locator documentation',
  }).toBe(true);

  // Open the official result and check the destination and its content.
  expect(await actions.openLocatorsDoc(page), 'Open the locator documentation result').toBe(true);
  expect(actions.isPlaywrightDevHost(page.url())).toBe(true);
  const headings = (await page.locator('h1, h2, h3').allTextContents()).join(' | ');
  const body = await page.locator('body').innerText();
  expect(/locator/i.test(headings) && /getByRole\(|getByTestId\(|getByLabel\(|\.locator\(/i.test(body) &&
    (body.match(/locator/gi) || []).length >= 3,
    'The page describes how to use Playwright locators').toBe(true);
}
