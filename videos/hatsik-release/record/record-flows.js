// Record Hatsik product flows on production as separate vertical clips.
// Uses CDP Page.startScreencast to capture at device pixels (dsf 2 → 1080x1920),
// then assembles each clip into an .mp4 with ffmpeg using real frame timestamps.
// Login happens off-camera via storage-state.json (never recorded).
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'https://hatsik.jjjl.dev';
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
        this.frames = []; // { file, ts } — ts is epoch seconds from CDP
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
        // Capture loop: CDP screencast ignores deviceScaleFactor, but
        // captureScreenshot with clip.scale=2 renders true 1080x1920 frames (~20fps).
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
                    await new Promise(r => setTimeout(r, 50)); // navigation in flight
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
        const t0 = this.frames[0].ts; // epoch seconds
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
            t: Math.round(e.epoch - t0 * 1000), // ms since first frame
            type: e.type, label: e.label,
            // click coords are CSS px on a 540x960 viewport; multiply by 2 for 1080x1920 output px
            x: e.x, y: e.y,
        }));
        fs.writeFileSync(path.join(CLIPS, `${this.name}.events.json`),
            JSON.stringify({ scale: 2, viewport: VIEWPORT, frames: this.frames.length, events }, null, 2));
        fs.rmSync(this.framesDir, { recursive: true, force: true });
        console.log(`  [${this.name}] saved → ${out} (${this.frames.length} frames)`);
    }
}

(async () => {
    fs.mkdirSync(CLIPS, { recursive: true });
    const browser = await chromium.launch({ headless: true });
    const state = {};

    // ── Beat 1: Crear evento ─────────────────────────────────────
    {
        const b = new Beat('clip-01-crear-evento', browser);
        const page = await b.start();
        await page.goto(`${BASE_URL}/events/`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);
        await b.click('main a[href="/events/create/"]', 'Crear evento (dashboard)');
        await page.waitForURL('**/events/create/', { timeout: 15000 });
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(600);
        await b.type('#id_name', 'Asado de Fin de Año', 'nombre del evento');
        await b.click('#id_event_date', 'fecha');
        await page.fill('#id_event_date', '2026-08-15');
        await page.waitForTimeout(500);
        await b.type('#id_description', 'Carne, carbon y buena compania', 'descripción');
        await b.click('button[type="submit"]:has-text("Crear Evento")', 'Crear Evento (submit)');
        await page.waitForURL(/\/events\/[0-9a-f-]{36}\/$/, { timeout: 20000 });
        await page.waitForLoadState('networkidle');
        state.eventUrl = page.url();
        await b.note(`event created: ${state.eventUrl}`);
        await page.waitForTimeout(1500);
        await page.mouse.wheel(0, 500);
        await page.waitForTimeout(1200);
        await b.finish();
    }

    // ── Beat 2: Añadir ítems ─────────────────────────────────────
    {
        const b = new Beat('clip-02-anadir-items', browser);
        const page = await b.start();
        await page.goto(state.eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(800);
        const items = [
            { name: 'Carne para asar', qty: '3', unit: 'kg' },
            { name: 'Carbon', qty: '2', unit: 'bags' },
            { name: 'Cerveza', qty: '24', unit: 'pieces' },
        ];
        for (const item of items) {
            await b.click('text=Añadir ítem', `Añadir ítem (${item.name})`);
            await page.locator('#id_name').waitFor({ state: 'visible', timeout: 10000 });
            await page.waitForTimeout(400);
            await b.type('#id_name', item.name, `ítem: ${item.name}`);
            await b.type('#id_quantity_total', item.qty, 'cantidad');
            await b.click('#id_unit', 'unidad');
            await page.selectOption('#id_unit', item.unit);
            await page.waitForTimeout(400);
            await b.click('button[type="submit"]:has-text("Añadir ítem")', 'guardar ítem');
            await page.locator('#id_name').waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
            await page.waitForTimeout(900);
        }
        await b.note('items added');
        await page.waitForTimeout(1200);
        await b.finish();
    }

    // ── Beat 3: Compartir link + QR ──────────────────────────────
    {
        const b = new Beat('clip-03-compartir', browser);
        const page = await b.start();
        await page.goto(state.eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(800);
        await b.click('a:has-text("Invitar amigos")', 'Invitar amigos');
        await page.waitForURL('**/share/', { timeout: 15000 });
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1200);
        await b.click('#copy-link-btn', 'Copiar link');
        await page.waitForTimeout(1600); // "¡Copiado!" feedback visible
        const qr = page.locator('img[src*="qr"]').first();
        await qr.scrollIntoViewIfNeeded().catch(() => {});
        const qrBox = await qr.boundingBox().catch(() => null);
        if (qrBox) b.log('note', 'qr visible', Math.round(qrBox.x + qrBox.width / 2), Math.round(qrBox.y + qrBox.height / 2));
        await page.waitForTimeout(2200);
        await b.finish();
    }

    // ── Beat 4: Asignarse ítems ("tomar") ────────────────────────
    {
        const b = new Beat('clip-04-tomar', browser);
        const page = await b.start();
        await page.goto(state.eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);
        await b.click('button:has-text("Asignarme")', 'Asignarme (Carne)');
        await page.locator('input[name="quantity_assigned"]').waitFor({ state: 'visible', timeout: 10000 });
        await page.waitForTimeout(400);
        await b.type('input[name="quantity_assigned"]', '3', 'cantidad a llevar');
        await b.click('button:has-text("Confirmar")', 'Confirmar');
        await page.waitForTimeout(1500);
        await b.click('button:has-text("Asignarme")', 'Asignarme (siguiente ítem)');
        await page.locator('input[name="quantity_assigned"]').waitFor({ state: 'visible', timeout: 10000 });
        await page.waitForTimeout(400);
        await b.type('input[name="quantity_assigned"]', '12', 'cantidad a llevar');
        await b.click('button:has-text("Confirmar")', 'Confirmar');
        await page.waitForTimeout(1800);
        await b.finish();
    }

    // ── Beat 5: Marcar como comprado ─────────────────────────────
    {
        const b = new Beat('clip-05-comprado', browser);
        const page = await b.start();
        await page.goto(state.eventUrl, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);
        await b.click('button[title="Marcar como comprado"]', 'Marcar como comprado (1)');
        await page.waitForTimeout(2000);
        const second = page.locator('button[title="Marcar como comprado"]').first();
        if (await second.isVisible().catch(() => false)) {
            await b.click('button[title="Marcar como comprado"]', 'Marcar como comprado (2)');
            await page.waitForTimeout(2000);
        }
        await page.mouse.wheel(0, -800);
        await page.waitForTimeout(1500);
        await b.note('progress visible');
        await page.waitForTimeout(1000);
        await b.finish();
    }

    fs.writeFileSync(path.join(CLIPS, 'state.json'), JSON.stringify(state, null, 2));
    await browser.close();
    console.log('\nAll clips recorded.');
})().catch(err => { console.error(err); process.exit(1); });
