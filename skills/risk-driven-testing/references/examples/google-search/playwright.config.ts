// The test runner owns the browser, context and page for each test.
// The default Chrome channel launches an independent browser without using an existing session.
import { defineConfig } from 'playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  timeout: 60_000,
  fullyParallel: false,
  reporter: [['list']],
  use: {
    headless: true,
    channel: process.env.RDT_CHANNEL ?? 'chrome',
    viewport: { width: 1280, height: 800 },
  },
});
