// Probe: what resolution does CDP screencast deliver under different setups?
const { chromium } = require('playwright');

async function probe(label, launchArgs, contextOpts) {
    const browser = await chromium.launch({ headless: true, args: launchArgs });
    const context = await browser.newContext(contextOpts);
    const page = await context.newPage();
    const cdp = await context.newCDPSession(page);
    let reported = false;
    cdp.on('Page.screencastFrame', async e => {
        if (!reported) {
            reported = true;
            const buf = Buffer.from(e.data, 'base64');
            // JPEG SOF parsing is overkill — use the metadata
            console.log(`${label}: deviceWidth=${e.metadata.deviceWidth} deviceHeight=${e.metadata.deviceHeight} bytes=${buf.length}`);
        }
        await cdp.send('Page.screencastFrameAck', { sessionId: e.sessionId }).catch(() => {});
    });
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 90, maxWidth: 2160, maxHeight: 3840 });
    await page.goto('https://hatsik.jjjl.dev/login/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    const vp = await page.evaluate(() => `${innerWidth}x${innerHeight} dpr=${devicePixelRatio}`);
    console.log(`${label}: CSS viewport ${vp}`);
    await browser.close();
}

(async () => {
    await probe('A(dsf2-context)', [], { viewport: { width: 540, height: 960 }, deviceScaleFactor: 2, isMobile: true });
    await probe('B(force-dsf-flag)', ['--force-device-scale-factor=2', '--window-size=540,1040'], { viewport: null });
    await probe('C(force-dsf+high-dpi-surface)', ['--force-device-scale-factor=2', '--window-size=540,1040', '--high-dpi-support=1'], { viewport: null });
})();
