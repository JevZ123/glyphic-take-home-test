import { defineConfig } from '@playwright/test';

export default defineConfig({

    testDir: 'tests',
    timeout: 30000,
    retries: 1,
    use: {
      headless: true,
      baseURL: process.env.BASE_URL || 'http://localhost:3000',
    },
    testMatch: ['**/*.test.ts'],
  });
  