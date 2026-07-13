const { chromium } = require('playwright');
const path = require('path');

const BASE_URL = 'http://localhost:8000';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'static', 'img', 'screenshots');

const EMAIL = 'maria@demo.hatsik.com';
const PASSWORD = 'Demo2026!';

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 1000 },
        deviceScaleFactor: 2,
    });
    const page = await context.newPage();

    // Login
    await page.goto(`${BASE_URL}/login/`);
    await page.fill('input[name="email"]', EMAIL);
    await page.fill('input[name="password"]', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');

    // Find event
    const links = await page.locator('a').all();
    let eventHref = null;
    for (const link of links) {
        const href = await link.getAttribute('href');
        if (href && href.match(/\/events\/[a-f0-9-]+\/$/)) {
            eventHref = href;
            break;
        }
    }

    if (!eventHref) {
        console.log('❌ No event found');
        await browser.close();
        return;
    }

    // Go to share page
    await page.goto(`${BASE_URL}${eventHref}share/`);
    await page.waitForLoadState('networkidle');

    // Hide debug toolbar and sidebar
    await page.evaluate(() => {
        const djDebug = document.getElementById('djDebug');
        if (djDebug) djDebug.style.display = 'none';

        // Hide the sidebar and header to focus on the card
        const sidebar = document.querySelector('aside');
        if (sidebar) sidebar.style.display = 'none';

        const headers = document.querySelectorAll('header');
        headers.forEach(h => h.style.display = 'none');

        // Remove margin-left from main content
        const mainWrap = document.querySelector('.md\\:ml-64');
        if (mainWrap) mainWrap.style.marginLeft = '0';
    });

    // Replace localhost URL with production URL
    await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.value && input.value.includes('localhost')) {
                input.value = 'https://hatsik.com/events/join/a8f2c4...';
            }
        });
    });

    // Overlay logo on QR center
    await page.evaluate(() => {
        // Find the QR image (it's an <img> with a base64 or qr-related src)
        const allImgs = document.querySelectorAll('img');
        let qrImg = null;
        allImgs.forEach(img => {
            const rect = img.getBoundingClientRect();
            // QR codes are typically square and around 150-300px
            if (rect.width > 120 && rect.width < 350 && Math.abs(rect.width - rect.height) < 10) {
                qrImg = img;
            }
        });

        if (qrImg) {
            const parent = qrImg.parentElement;
            parent.style.position = 'relative';
            parent.style.display = 'inline-block';

            const logoDiv = document.createElement('div');
            logoDiv.style.position = 'absolute';
            logoDiv.style.top = '50%';
            logoDiv.style.left = '50%';
            logoDiv.style.transform = 'translate(-50%, -50%)';
            logoDiv.style.width = '52px';
            logoDiv.style.height = '52px';
            logoDiv.style.borderRadius = '10px';
            logoDiv.style.backgroundColor = 'white';
            logoDiv.style.padding = '6px';
            logoDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.12)';
            logoDiv.style.display = 'flex';
            logoDiv.style.alignItems = 'center';
            logoDiv.style.justifyContent = 'center';

            const logoImg = document.createElement('img');
            logoImg.src = '/static/img/logo.png';
            logoImg.style.width = '40px';
            logoImg.style.height = '40px';
            logoImg.style.borderRadius = '6px';
            logoDiv.appendChild(logoImg);
            parent.appendChild(logoDiv);
        }
    });

    await page.waitForTimeout(500);

    // Take a full page screenshot first, then we'll crop
    // Get the invite card bounding box
    const clip = await page.evaluate(() => {
        // Find the card by looking for the "Invitar amigos" heading
        const headings = [...document.querySelectorAll('h1, h2, h3, strong, b')];
        let heading = headings.find(h => h.textContent.trim().includes('Invitar amigos'));

        if (heading) {
            // Walk up to find the card container (rounded border div)
            let container = heading.parentElement;
            for (let i = 0; i < 8; i++) {
                if (!container) break;
                const style = getComputedStyle(container);
                const rect = container.getBoundingClientRect();
                // Look for a container that's card-sized (400-800px wide)
                if (rect.width > 400 && rect.width < 900 && rect.height > 400) {
                    return {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    };
                }
                container = container.parentElement;
            }
        }

        // Fallback - crop the center of the page
        return null;
    });

    if (clip) {
        const pad = 24;
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, '07-share-event.png'),
            clip: {
                x: Math.max(0, clip.x - pad),
                y: Math.max(0, clip.y - pad),
                width: clip.width + pad * 2,
                height: clip.height + pad * 2,
            },
        });
        console.log(`✅ Captured card: ${clip.width.toFixed(0)}x${clip.height.toFixed(0)}`);
    } else {
        // Fallback: center of page without sidebar (sidebar hidden)
        await page.screenshot({
            path: path.join(SCREENSHOT_DIR, '07-share-event.png'),
            clip: { x: 160, y: 20, width: 680, height: 820 },
        });
        console.log('✅ Captured (fallback center crop)');
    }

    await browser.close();
})();
