// Shared recording harness: Beat = one clip captured via CDP captureScreenshot
// loop at clip.scale=2 (true 1080x1920 device pixels), assembled with ffmpeg.
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..');
const CLIPS = path.join(ROOT, 'clips');
const STATE = path.join(ROOT, 'storage-state.json');
const VIEWPORT = { width: 540, height: 960 };
const EMAIL = process.env.HATSIK_EMAIL || '';
const MASKED = 'demo@hatsik.app';

const INIT_SCRIPT = (email, masked) => `
(() => {
    const style = document.createElement('style');
    style.textContent = \`
        #__cursor { position: fixed; z-index: 2147483647; width: 30px; height: 30px;
            border-radius: 50%; background: rgba(181,29,12,.28); border: 2.5px solid rgba(181,29,12,.85);
            pointer-events: none; transform: translate(-50%,-50%); top:-100px; left:-100px;
            transition: width .15s, height .15s; box-shadow: 0 2px 10px rgba(0,0,0,.18); }
        .__ripple { position: fixed; z-index: 2147483646; border-radius: 50%;
            border: 3px solid rgba(181,29,12,.75); pointer-events: none;
            transform: translate(-50%,-50%); animation: __rip .5s ease-out forwards; }
        @keyframes __rip { from { width: 30px; height: 30px; opacity: 1; }
            to { width: 90px; height: 90px; opacity: 0; } }
    \`;
    const attach = () => {
        document.head.appendChild(style);
        const c = document.createElement('div'); c.id = '__cursor';
        document.body.appendChild(c);
        document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
        document.addEventListener('mousedown', e => {
            c.style.width = '22px'; c.style.height = '22px';
            const r = document.createElement('div'); r.className = '__ripple';
            r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
            document.body.appendChild(r); setTimeout(() => r.remove(), 600);
        }, true);
        document.addEventListener('mouseup', () => { c.style.width = '30px'; c.style.height = '30px'; }, true);
    };
    if (document.body) attach(); else document.addEventListener('DOMContentLoaded', attach);
    const EMAIL = ${JSON.stringify(email)};
    if (EMAIL) {
        const mask = (root) => {
            const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) {
                if (w.currentNode.nodeValue.includes(EMAIL))
                    w.currentNode.nodeValue = w.currentNode.nodeValue.split(EMAIL).join(${JSON.stringify(masked)});
            }
        };
        new MutationObserver(() => mask(document.body)).observe(document.documentElement, { childList: true, subtree: true, characterData: true });
        document.addEventListener('DOMContentLoaded', () => mask(document.body));
    }
})();
`;

function easeInOut(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

class Beat {
    constructor(name, browser) {
        this.name = name;
        this.browser = browser;
        this.events = [];
        this.frames = [];
        this.mouse = { x: 270, y: 200 };
        this.framesDir = path.join(CLIPS, `${name}-frames`);
    }
    async start() {
        fs.mkdirSync(this.framesDir, { recursive: true });
        this.context = await this.browser.newContext({
            viewport: VIEWPORT,
            deviceScaleFactor: 2,
            isMobile: true,
            hasTouch: true,
            storageState: STATE,
            permissions: ['clipboard-read', 'clipboard-write'],
        });
        await this.context.addInitScript(INIT_SCRIPT(EMAIL, MASKED));
        this.page = await this.context.newPage();
        this.page.on('dialog', d => d.accept());
        this.cdp = await this.context.newCDPSession(this.page);
        this.capturing = true;
        this.captureLoop = (async () => {
            while (this.capturing) {
                try {
                    const { data } = await this.cdp.send('Page.captureScreenshot', {
                        format: 'jpeg', quality: 90, optimizeForSpeed: true,
                        clip: { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height, scale: 2 },
                    });
                    const idx = this.frames.length;
                    const file = path.join(this.framesDir, `f${String(idx).padStart(6, '0')}.jpg`);
                    fs.writeFileSync(file, Buffer.from(data, 'base64'));
                    this.frames.push({ file, ts: Date.now() / 1000 });
                } catch {
                    await new Promise(r => setTimeout(r, 50));
                }
            }
        })();
        return this.page;
    }
    log(type, label, x = null, y = null) {
        this.events.push({ epoch: Date.now(), type, label, x, y });
        console.log(`  [${this.name}] ${type} ${label}${x !== null ? ` (${x},${y})` : ''}`);
    }
    async moveTo(x, y, ms = 450) {
        const from = { ...this.mouse };
        const steps = 18;
        for (let i = 1; i <= steps; i++) {
            const k = easeInOut(i / steps);
            await this.page.mouse.move(from.x + (x - from.x) * k, from.y + (y - from.y) * k);
            await this.page.waitForTimeout(ms / steps);
        }
        this.mouse = { x, y };
    }
    async click(locator, label) {
        const el = this.page.locator(locator).first();
        await el.waitFor({ state: 'visible', timeout: 15000 });
        await el.scrollIntoViewIfNeeded();
        await this.page.waitForTimeout(350);
        const box = await el.boundingBox();
        const x = box.x + box.width / 2, y = box.y + box.height / 2;
        await this.moveTo(x, y);
        await this.page.waitForTimeout(180);
        this.log('click', label, Math.round(x), Math.round(y));
        await this.page.mouse.down();
        await this.page.waitForTimeout(90);
        await this.page.mouse.up();
    }
    async type(locator, text, label) {
        await this.click(locator, `focus:${label}`);
        this.log('type-start', label);
        await this.page.locator(locator).first().pressSequentially(text, { delay: 55 });
        this.log('type-end', label);
    }
    async note(label) { this.log('note', label); }
    async finish() {
        await this.page.waitForTimeout(1200);
        this.log('end', 'clip end');
        this.capturing = false;
        await this.captureLoop;
        await this.context.close();

        if (this.frames.length < 2) throw new Error(`${this.name}: only ${this.frames.length} frames captured`);
        const t0 = this.frames[0].ts;
        const listFile = path.join(this.framesDir, 'list.txt');
        let list = '';
        for (let i = 0; i < this.frames.length; i++) {
            const dur = i < this.frames.length - 1
                ? Math.max(0.01, this.frames[i + 1].ts - this.frames[i].ts)
                : 1.0;
            list += `file '${this.frames[i].file}'\nduration ${dur.toFixed(4)}\n`;
        }
        list += `file '${this.frames[this.frames.length - 1].file}'\n`;
        fs.writeFileSync(listFile, list);
        const out = path.join(CLIPS, `${this.name}.mp4`);
        execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', listFile,
            '-fps_mode', 'vfr', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '18', out]);
        const events = this.events.map(e => ({
            t: Math.round(e.epoch - t0 * 1000),
            type: e.type, label: e.label,
            x: e.x, y: e.y, // CSS px on 540x960; multiply by 2 for 1080x1920 output px
        }));
        fs.writeFileSync(path.join(CLIPS, `${this.name}.events.json`),
            JSON.stringify({ scale: 2, viewport: VIEWPORT, frames: this.frames.length, events }, null, 2));
        fs.rmSync(this.framesDir, { recursive: true, force: true });
        console.log(`  [${this.name}] saved → ${out} (${this.frames.length} frames)`);
    }
}

module.exports = { Beat, CLIPS, VIEWPORT };
