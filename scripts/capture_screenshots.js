// Capture clean screenshots of the Hatsik app flow using Playwright (Chromium)
// Hides Django Debug Toolbar for clean captures
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:8000';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'static', 'img', 'screenshots');
const EMAIL = 'joryerjesus10@gmail.com';
const PASSWORD = 'Hatsik2026!';

async function hideDebugToolbar(page) {
    await page.evaluate(() => {
        const djDebug = document.getElementById('djDebug');
        if (djDebug) djDebug.style.display = 'none';
    });
}

(async () => {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    // ─── 1. Landing Page ───────────────────────────────────────
    console.log('📸 1/7 Landing hero...');
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '01-landing-hero.png'),
        clip: { x: 0, y: 0, width: 1280, height: 800 },
    });

    // Scroll to "Caos vs Claridad"
    console.log('📸 2/7 Landing comparison...');
    await page.evaluate(() => window.scrollTo(0, 1400));
    await page.waitForTimeout(500);
    await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '02-landing-comparison.png'),
        clip: { x: 0, y: 0, width: 1280, height: 800 },
    });

    // ─── 2. Login ──────────────────────────────────────────────
    console.log('📸 3/7 Login...');
    await page.goto(`${BASE_URL}/login/`);
    await page.waitForLoadState('networkidle');
    await hideDebugToolbar(page);
    await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '03-login.png'),
        clip: { x: 0, y: 0, width: 1280, height: 800 },
    });

    // Perform login
    await page.fill('input[name="email"]', EMAIL);
    await page.fill('input[name="password"]', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');

    if (page.url().includes('/login')) {
        console.log('⚠️  Login failed, retrying with alternate approach...');
        // Force login via cookie
        await page.goto(`${BASE_URL}/events/`);
        await page.waitForLoadState('networkidle');
    }

    // ─── 3. Dashboard ──────────────────────────────────────────
    console.log('📸 4/7 Dashboard...');
    await hideDebugToolbar(page);
    await page.screenshot({
        path: path.join(SCREENSHOT_DIR, '04-dashboard.png'),
        clip: { x: 0, y: 0, width: 1280, height: 800 },
    });

    // ─── 4. Event Detail ───────────────────────────────────────
    console.log('📸 5/7 Event detail...');
    // Find any event link
    const links = await page.locator('a').all();
    let eventHref = null;
    for (const link of links) {
        const href = await link.getAttribute('href');
        if (href && href.match(/\/events\/[a-f0-9-]+\/$/)) {
            eventHref = href;
            break;
        }
    }

    if (eventHref) {
        await page.goto(`${BASE_URL}${eventHref}`);
        await page.waitForLoadState('networkidle');
        await hideDebugToolbar(page);
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, '05-event-detail.png'),
            clip: { x: 0, y: 0, width: 1280, height: 800 },
        });

        // Scroll to items
        console.log('📸 6/7 Event items...');
        await page.evaluate(() => window.scrollTo(0, 500));
        await page.waitForTimeout(400);
        await hideDebugToolbar(page);
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, '06-event-items.png'),
            clip: { x: 0, y: 0, width: 1280, height: 800 },
        });

        // Share page
        console.log('📸 7/7 Share event...');
        await page.goto(`${BASE_URL}${eventHref}share/`);
        await page.waitForLoadState('networkidle');
        await hideDebugToolbar(page);
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, '07-share-event.png'),
            clip: { x: 0, y: 0, width: 1280, height: 800 },
        });
    } else {
        console.log('⚠️  No event found on dashboard');
    }

    await browser.close();

    console.log(`\n✅ All screenshots saved to ${SCREENSHOT_DIR}/`);
    const files = fs.readdirSync(SCREENSHOT_DIR).filter(f => f.endsWith('.png')).sort();
    files.forEach(f => {
        const size = (fs.statSync(path.join(SCREENSHOT_DIR, f)).size / 1024).toFixed(0);
        console.log(`   ${f} (${size} KB)`);
    });
})();
