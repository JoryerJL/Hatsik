// Probe D: Emulation.setDeviceMetricsOverride with scale=2 → screencast frame size?
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch({ headless: true, args: ['--window-size=1100,1960'] });
    const context = await browser.newContext({ viewport: null });
    const page = await context.newPage();
    const cdp = await context.newCDPSession(page);
    await cdp.send('Emulation.setDeviceMetricsOverride', {
        width: 540, height: 960, deviceScaleFactor: 2, mobile: true, scale: 2,
    });
    let saved = false;
    cdp.on('Page.screencastFrame', async e => {
        if (!saved) {
            saved = true;
            fs.writeFileSync('probe/frame-d.jpg', Buffer.from(e.data, 'base64'));
            console.log(`metadata: deviceWidth=${e.metadata.deviceWidth} deviceHeight=${e.metadata.deviceHeight}`);
        }
        await cdp.send('Page.screencastFrameAck', { sessionId: e.sessionId }).catch(() => {});
    });
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 90, maxWidth: 2160, maxHeight: 3840 });
    await page.goto('https://hatsik.jjjl.dev/login/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    console.log('CSS viewport:', await page.evaluate(() => `${innerWidth}x${innerHeight} dpr=${devicePixelRatio}`));
    // Verify click mapping still works in CSS px: click the email input and report focus
    await page.click('#id_email');
    console.log('focused:', await page.evaluate(() => document.activeElement.id));
    await browser.close();
})();
