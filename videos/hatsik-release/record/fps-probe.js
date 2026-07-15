// Probe: sustained Page.captureScreenshot rate at dsf=2 (1080x1920 jpeg)
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 540, height: 960 }, deviceScaleFactor: 2, isMobile: true,
    });
    const page = await context.newPage();
    const cdp = await context.newCDPSession(page);
    await page.goto('https://hatsik.jjjl.dev/', { waitUntil: 'networkidle' });

    // animate something: slow scroll while capturing
    const scroll = (async () => {
        for (let i = 0; i < 30; i++) { await page.mouse.wheel(0, 60); await page.waitForTimeout(100); }
    })();

    const t0 = Date.now();
    let n = 0, bytes = 0, w = 0;
    while (Date.now() - t0 < 3000) {
        const { data } = await cdp.send('Page.captureScreenshot', {
            format: 'jpeg', quality: 85, optimizeForSpeed: true,
            clip: { x: 0, y: 0, width: 540, height: 960, scale: 2 },
        });
        const buf = Buffer.from(data, 'base64');
        bytes += buf.length; n++;
        if (n === 1) {
            // JPEG SOF0/SOF2 width scan
            for (let i = 2; i < buf.length - 9; i++) {
                if (buf[i] === 0xFF && (buf[i + 1] === 0xC0 || buf[i + 1] === 0xC2)) {
                    w = `${buf.readUInt16BE(i + 7)}x${buf.readUInt16BE(i + 5)}`; break;
                }
            }
        }
    }
    await scroll;
    console.log(`captured ${n} frames in 3s → ${(n / 3).toFixed(1)} fps, avg ${(bytes / n / 1024).toFixed(0)} KB, size ${w}`);
    await browser.close();
})();
