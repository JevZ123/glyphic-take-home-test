import { test, expect } from '@playwright/test';

// Sanity check if the system can identify call participants from call transcript
test('Test Glyphic <> Onfido', async ({ page }) => {
        await page.goto('/');
        await page.getByText('Glyphic <> Onfido11/11/2024,').click();
        await page.getByLabel('Type your question...').click();
        await page.getByLabel('Type your question...').fill('who are the main parties involved in this call?');
        await page.getByRole('button', { name: 'Send' }).click();

        const element = page.locator('p:has-text("Devang Agrawal")');
        const containsSecondText = await element.evaluate((el) => {
          const text = el.textContent || '';
          return text.includes('Theo Blake');
        });
      
        expect(containsSecondText).toBe(true);
}); 
