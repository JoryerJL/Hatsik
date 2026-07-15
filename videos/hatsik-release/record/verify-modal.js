// Verify the landing "Ver cómo funciona" modal opens and the video plays.
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.goto('http://localhost:8765/', { waitUntil: 'networkidle' });
    await page.evaluate(() => { const d = document.getElementById('djDebug'); if (d) d.style.display = 'none'; });
    await page.click('#how-it-works-btn');
    await page.waitForTimeout(2500);
    const state = await page.evaluate(() => {
        const m = document.getElementById('how-it-works-modal');
        const v = document.getElementById('how-it-works-video');
        return {
            modalVisible: !m.classList.contains('hidden'),
            currentTime: v.currentTime,
            paused: v.paused,
            videoW: v.videoWidth, videoH: v.videoHeight,
            src: v.currentSrc.split('/').pop(),
        };
    });
    console.log('modal state:', JSON.stringify(state));
    await page.screenshot({ path: 'probe/modal-open.png' });
    // close via Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(400);
    const closed = await page.evaluate(() => ({
        hidden: document.getElementById('how-it-works-modal').classList.contains('hidden'),
        paused: document.getElementById('how-it-works-video').paused,
    }));
    console.log('after escape:', JSON.stringify(closed));
    await browser.close();
})();
