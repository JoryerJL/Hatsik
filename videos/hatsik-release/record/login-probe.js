// Probe: login against production, persist session state, report account/dashboard status.
// Never records video — keeps the email off-camera.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'https://hatsik.jjjl.dev';
const EMAIL = process.env.HATSIK_EMAIL;
const PASSWORD = process.env.HATSIK_PASSWORD;
const OUT = path.join(__dirname, '..', 'probe');
const STATE = path.join(__dirname, '..', 'storage-state.json');

(async () => {
    fs.mkdirSync(OUT, { recursive: true });
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 540, height: 960 },
        deviceScaleFactor: 2,
        isMobile: true,
        hasTouch: true,
    });
    const page = await context.newPage();

    await page.goto(`${BASE_URL}/login/`, { waitUntil: 'networkidle' });
    await page.fill('#id_email', EMAIL);
    await page.fill('#id_password', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');

    console.log('URL after login:', page.url());
    const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 400));
    console.log('---- body snippet ----');
    console.log(bodyText);
    console.log('----------------------');

    if (page.url().includes('/events/')) {
        const eventLinks = await page.$$eval('a[href^="/events/"]', as =>
            as.map(a => ({ href: a.getAttribute('href'), text: a.innerText.replace(/\s+/g, ' ').trim().slice(0, 60) }))
        );
        console.log('Event links on dashboard:', JSON.stringify(eventLinks, null, 2));
    }

    await page.screenshot({ path: path.join(OUT, 'after-login.png'), fullPage: false });
    await context.storageState({ path: STATE });
    console.log('Storage state saved.');
    await browser.close();
})();
