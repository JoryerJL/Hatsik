// Re-record beats 4 & 5 against the already-created event (clips/state.json).
// Beat 4: claim Carbon (2 bags) and Cerveza (24 pieces), each scoped to its item card.
// Beat 5: purchase both assignments → event progress reaches 100%.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const CLIPS = path.join(__dirname, '..', 'clips');
const { eventUrl } = JSON.parse(fs.readFileSync(path.join(CLIPS, 'state.json'), 'utf8'));

// Reuse the Beat class and helpers by requiring the recorder in library mode is
// overkill for two beats — duplicate the minimal harness instead.
const shared = require('./record-flows-lib');

(async () => {
    const browser = await chromium.launch({ headless: true });

    {
        const b = new shared.Beat('clip-04-tomar', browser);
        const page = await b.start();
        await page.goto(eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);

        const claims = [
            { item: 'Carbon', qty: '2' },
            { item: 'Cerveza', qty: '24' },
        ];
        for (const c of claims) {
            const row = `[id^="item-row"]:has-text("${c.item}")`;
            await b.click(`${row} button:has-text("Asignarme")`, `Asignarme (${c.item})`);
            await page.locator('input[name="quantity_assigned"]').waitFor({ state: 'visible', timeout: 10000 });
            await page.waitForTimeout(400);
            const qtyInput = 'input[name="quantity_assigned"]';
            await b.click(qtyInput, `focus:cantidad (${c.item})`);
            await page.fill(qtyInput, '');
            b.log('type-start', `cantidad ${c.qty}`);
            await page.locator(qtyInput).first().pressSequentially(c.qty, { delay: 90 });
            b.log('type-end', `cantidad ${c.qty}`);
            await b.click('button:has-text("Confirmar")', `Confirmar (${c.item})`);
            await page.locator('input[name="quantity_assigned"]').waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
            await page.waitForTimeout(1400);
        }
        await page.waitForTimeout(1000);
        await b.finish();
    }

    {
        const b = new shared.Beat('clip-05-comprado', browser);
        const page = await b.start();
        await page.goto(eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);
        for (let i = 1; i <= 2; i++) {
            const btn = 'button[title="Marcar como comprado"]';
            const visible = await b.page.locator(btn).first().isVisible().catch(() => false);
            if (!visible) break;
            await b.click(btn, `Marcar como comprado (${i})`);
            await page.waitForTimeout(2000);
        }
        // Ease back to the top so the 100% progress bar is the closing shot.
        for (let i = 0; i < 8; i++) { await page.mouse.wheel(0, -300); await page.waitForTimeout(120); }
        await page.waitForTimeout(600);
        await b.note('progress 100%');
        await page.waitForTimeout(1600);
        await b.finish();
    }

    await browser.close();
    console.log('\nBeats 4 & 5 re-recorded.');
})().catch(err => { console.error(err); process.exit(1); });
