const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

const DEFAULT_ROOT = 'E:\\今天又是美好的一天\\网易dd\\插件审核';
const SESSION = 'df-cms-chrome-default';
const API_BASE = 'https://ui-cms-api.opd.netease.com';
const AUTH_STATE_FILE = path.join(DEFAULT_ROOT, 'output', 'share-wa-review', 'df-cms-auth-state.json');
const USER_SOURCE = '\u7528\u6237\u53d1\u5e03';
const SHARE_REJECT_REASON = '\u914d\u7f6e\u5206\u4eab\u8bf7\u586b\u8be6\u7ec6\u5185\u5bb9\uff0c\u81ea\u7528\u8bf7\u6807\u6ce8\u81ea\u7528\u8f6c\u4e3a\u79c1\u5bc6\u5206\u4eab';
const WA_REJECT_REASON = '\u5b57\u7b26\u4e32\u4ecb\u7ecd\u76f8\u5173\u8bf7\u586b\u8be6\u7ec6\u5185\u5bb9\uff0c\u81ea\u7528\u8bf7\u6807\u6ce8\u81ea\u7528\u8f6c\u4e3a\u79c1\u5bc6\u5206\u4eab';
const GAME_TYPES = [
  { label: '正式服', value: 10001 },
  { label: '泰坦重铸', value: 2 },
  { label: '熊猫人之谜', value: 6 },
  { label: '燃烧的远征', value: 4 },
  { label: '经典怀旧服', value: 3 },
];
const SCOPES = [{ label: '公开分享', value: 'public' }, { label: '私密分享', value: 'private' }];
const STATES = [{ label: '待审核', value: 'init' }, { label: '机审失败', value: 'niv_failed' }];
const DEFAULT_AIGW_BASE_URL = 'https://aigw.ds.163.com';
const DEFAULT_IMAGE_REVIEW_MODEL = 'doubao-seed-2.0-mini';
const DEFAULT_IMAGE_REVIEW_BATCH_SIZE = 8;
const IMAGE_REVIEW_ENDPOINT_PATH = '/v1/chat/completions';
const DEFAULT_RETRY_IMAGE_MAX_SIDE = 1280;
const DEFAULT_RETRY_IMAGE_MAX_BYTES = 1536 * 1024;

function parseArgs(argv) {
  const out = { mode: 'report', root: DEFAULT_ROOT };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) out[key] = true;
      else { out[key] = next; i++; }
    }
  }
  return out;
}

function stamp() {
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function ensureDir(dir) { fs.mkdirSync(dir, { recursive: true }); }
function writeJson(file, data) { fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8'); }
function readJsonNoBom(file) {
  const text = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Cannot parse JSON ${file}: ${error.message}`);
  }
}
function stripHtml(s) { return String(s || '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim(); }
function truncate(s, n = 260) { s = String(s || ''); return s.length > n ? `${s.slice(0, n)}…` : s; }
function isTruthyArg(value) { return value === true || value === 'true' || value === '1' || value === 'yes'; }
function clampInt(value, fallback, min, max) {
  const n = Number.parseInt(String(value || ''), 10);
  if (!Number.isFinite(n)) return fallback;
  return Math.max(min, Math.min(max, n));
}
function redactSecretText(text) {
  return String(text || '').replace(/[A-Za-z0-9_\-]{24,}/g, '[redacted]');
}
function hasMeaning(s) {
  const t = stripHtml(s).replace(/[\s\p{P}\p{S}]/gu, '');
  if (!t) return false;
  if (/^\d+$/.test(t)) return false;
  if (/^(test|asdf|测试|占位|无|暂无|随便|111+|222+|123+)$/i.test(t)) return false;
  if (t.length <= 1) return false;
  if (/^(.)\1{2,}$/.test(t)) return false;
  return true;
}
function hasSelfUse(s) { return /(自用|自己用|个人用|私人|私用|备用|留档|专用|专供|朋友分享|给朋友分享|分享给朋友|给朋友用|好友分享|给好友分享|分享给好友|给好友用)/.test(stripHtml(s)); }
function hasOutwardShare(s) {
  const t = stripHtml(s).replace(/(朋友分享|给朋友分享|分享给朋友|给朋友用|好友分享|给好友分享|分享给好友|给好友用)/g, '');
  return /(分享出来|分享给|给别人用|分享版|共享|供大家|方便大家)/.test(t);
}
function hasSpecificShareContent(record) {
  const detail = stripHtml(record.fields?.detail);
  const update = stripHtml(record.fields?.updateDesc);
  const text = [record.title, record.fields?.brief, detail, update].map(stripHtml).join(' ');
  if (/(安装|更新|适配|适用|包含|插件|整合|配置|界面|动作条|团队|框架|姓名板|监控|WA|ElvUI|ELVUI|露露|NDUI|NAXX|副本|打团|天赋|版本|删除|文件夹|Cache|Interface|WTF)/i.test(text)) return true;
  if ((hasMeaning(detail) && detail.replace(/[\s\p{P}\p{S}]/gu, '').length >= 30) || (hasMeaning(update) && update.replace(/[\s\p{P}\p{S}]/gu, '').length >= 20)) return true;
  return false;
}
function scopeLabel(value) {
  if (value === 'public') return '公开分享';
  if (value === 'private') return '私密分享';
  return value || '';
}
function violationType(s) {
  const t = stripHtml(s);
  if (/(色情|裸聊|赌博|博彩|诈骗|外挂|黑产|账号交易|台独|独立建国|分裂国家)/.test(t)) return '违规敏感内容';
  return '';
}
function imageNote(record) {
  const total = (record.imageUrls || []).length;
  const niv = (record.nivFailedImgs || []).length;
  if (record.auditStateValue === 'niv_failed' && niv > 0) return `机审失败图片 ${niv} 张，需完整识别`;
  if (total > 0) return `图片 ${total} 张，待报告 contact sheet 核验`;
  return '无图片';
}

function suggest(record) {
  const text = [record.title, record.fields?.brief, record.fields?.detail, record.fields?.updateDesc].filter(Boolean).join('\n');
  const bad = violationType(text);
  if (bad) return { action: 'reject', reason: record.section === 'wa' ? WA_REJECT_REASON : SHARE_REJECT_REASON, issue: bad, executable: true };
  if (record.auditStateValue === 'niv_failed' && ((record.nivFailedImgs || []).length > 0 || (record.imageUrls || []).length > 0)) {
    return { action: 'manualConfirm', reason: '', issue: '机审失败需人工完整核验图文', executable: false };
  }
  if (record.section === 'share') {
    const titleOk = hasMeaning(record.title);
    const briefOk = hasMeaning(record.fields?.brief);
    const detailOk = hasMeaning(record.fields?.detail);
    const updateOk = hasMeaning(record.fields?.updateDesc);
    const meaningful = titleOk && briefOk && detailOk && updateOk;
    const meaningfulWithoutUpdate = titleOk && briefOk && detailOk;
    const selfUse = hasSelfUse(text);
    const outward = hasOutwardShare(text);
    if (record.scopeValue === 'public' && selfUse && !outward && hasSpecificShareContent(record)) return { action: 'autoPass', reason: '', issue: '', executable: true };
    if (record.scopeValue === 'public' && selfUse && !outward) return { action: 'transferPrivateThenPass', reason: '', issue: '公开分享说明简单但有自用/专用意图', executable: true };
    if (meaningful || meaningfulWithoutUpdate || (outward && detailOk)) return { action: 'autoPass', reason: '', issue: '', executable: true };
    if (record.scopeValue === 'private' && (selfUse || hasMeaning(record.title) || hasMeaning(record.fields?.brief))) return { action: 'autoPass', reason: '', issue: '', executable: true };
    return { action: 'reject', reason: SHARE_REJECT_REASON, issue: '配置分享内容不完整或无意义', executable: true };
  }
  const nameOk = hasMeaning(record.title);
  const briefOk = hasMeaning(record.fields?.brief);
  const detailText = stripHtml(record.fields?.detail);
  const detailOk = hasMeaning(detailText) && !/^!WA:/.test(detailText) && !/^\d+$/.test(detailText);
  const selfUse = hasSelfUse(text);
  const outward = hasOutwardShare(text);
  if (nameOk && briefOk && detailOk) return { action: 'autoPass', reason: '', issue: '', executable: true };
  if (record.scopeValue === 'public' && selfUse && !outward) return { action: 'transferPrivateThenPass', reason: '', issue: '公开 WA 说明简单但有自用/专用意图', executable: true };
  if (record.scopeValue === 'private' && (selfUse || (nameOk && briefOk))) return { action: 'autoPass', reason: '', issue: '', executable: true };
  return { action: 'reject', reason: WA_REJECT_REASON, issue: '字符串介绍相关不完整或无意义', executable: true };
}

function buildScanFunction() {
  return async () => {
    const API_BASE = 'https://ui-cms-api.opd.netease.com';
    const USER_SOURCE = '\u7528\u6237\u53d1\u5e03';
    const GAME_TYPES = [
      { label: '正式服', value: 10001 }, { label: '泰坦重铸', value: 2 }, { label: '熊猫人之谜', value: 6 }, { label: '燃烧的远征', value: 4 }, { label: '经典怀旧服', value: 3 },
    ];
    const SCOPES = [{ label: '公开分享', value: 'public' }, { label: '私密分享', value: 'private' }];
    const STATES = [{ label: '待审核', value: 'init' }, { label: '机审失败', value: 'niv_failed' }];
    const getJson = async path => {
      const r = await fetch(API_BASE + path, { credentials: 'include' });
      const text = await r.text();
      let json; try { json = JSON.parse(text); } catch (e) { json = { code: -1, msg: e.message, text: text.slice(0, 500) }; }
      return { status: r.status, json };
    };
    async function fetchAll(section, endpoint, params, listKeys) {
      const size = 50; let pageNo = 1; const out = []; const errors = []; let total = null;
      while (true) {
        const qs = new URLSearchParams();
        Object.entries({ ...params, page: pageNo, size }).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') qs.append(k, v); });
        const { status, json } = await getJson(endpoint + '?' + qs.toString());
        if (status !== 200 || json.code !== 0) { errors.push({ section, endpoint, params, status, json }); break; }
        const result = json.result || {}; let list = [];
        for (const key of listKeys) if (Array.isArray(result[key])) { list = result[key]; break; }
        total = result.count ?? result.total ?? list.length;
        out.push(...list);
        if (out.length >= total || list.length === 0 || pageNo > 20) break;
        pageNo++;
      }
      return { list: out, total, errors };
    }
    const combos = []; const shareItems = []; const waItems = []; const errors = [];
    for (const gt of GAME_TYPES) for (const scope of SCOPES) for (const st of STATES) {
      const share = await fetchAll('share', '/share-api/audit/list', { scope: scope.value, game_type: gt.value, audit_state: st.value }, ['shares', 'share_list', 'list']);
      const wa = await fetchAll('wa', '/wa-api/audit/list', { source: USER_SOURCE, scope: scope.value, game_type: gt.value, audit_state: st.value }, ['wa_list', 'waList', 'list']);
      combos.push({ section: 'share', gameType: gt.label, gameTypeValue: gt.value, scope: scope.label, scopeValue: scope.value, auditState: st.label, auditStateValue: st.value, count: share.list.length, total: share.total });
      combos.push({ section: 'wa', gameType: gt.label, gameTypeValue: gt.value, scope: scope.label, scopeValue: scope.value, auditState: st.label, auditStateValue: st.value, source: USER_SOURCE, count: wa.list.length, total: wa.total });
      errors.push(...share.errors, ...wa.errors);
      for (const item of share.list) shareItems.push({ combo: { gameType: gt.label, gameTypeValue: gt.value, scope: scope.label, scopeValue: scope.value, auditState: st.label, auditStateValue: st.value }, item });
      for (const item of wa.list) waItems.push({ combo: { gameType: gt.label, gameTypeValue: gt.value, scope: scope.label, scopeValue: scope.value, auditState: st.label, auditStateValue: st.value, source: USER_SOURCE }, item });
    }
    const records = [];
    for (const { combo, item } of shareItems) {
      records.push({ section: 'share', id: item.sn, title: item.title || item.name || '', account: item.account || item.userAccount || '', author: item.user_nick || item.userNick || '', combo, scopeValue: item.scope || combo.scopeValue, auditStateValue: item.audit_state || combo.auditStateValue, fields: { brief: item.brief_desc || item.briefDesc || '', detail: item.desc || '', updateDesc: item.update_desc || item.updateDesc || '' }, imageUrls: item.display_imgs || item.displayImgs || [], nivFailedImgs: item.niv_failed_imgs || item.nivFailedImgs || [], raw: item });
    }
    for (const { combo, item } of waItems) {
      const detailRes = await getJson('/wa-api/detail?sn=' + encodeURIComponent(item.sn));
      const d = detailRes.json.result || item;
      records.push({ section: 'wa', id: d.sn || item.sn, title: d.cms_name || d.name || item.name || '', account: d.author_account || item.author_account || item.authorAccount || '', author: d.author_nick || item.authorNick || '', combo, scopeValue: d.scope || combo.scopeValue, auditStateValue: d.audit_state || combo.auditStateValue, fields: { brief: d.cms_brief_desc || d.brief_desc || '', detail: d.cms_desc || d.desc || d.content || '', updateDesc: '' }, imageUrls: d.cms_display_imgs || d.display_imgs || item.displayImgs || [], nivFailedImgs: d.niv_failed_imgs || item.nivFailedImgs || [], raw: d, detailStatus: detailRes.status, detailCode: detailRes.json.code });
    }
    return { scannedCombos: combos.length, combos, records, errors, recordsCount: records.length, errorsCount: errors.length, scannedAt: new Date().toISOString() };
  };
}

function writePlaywrightFunction(fn, label, outDir, input) {
  ensureDir(outDir);
  const file = path.join(outDir, `${label}.pw.js`);
  let inputLine = '';
  let evaluateArgs = '';
  if (input !== undefined) {
    const inputFile = path.join(outDir, `${label}.input.json`);
    const compactInput = compactExecuteInput(input);
    writeJson(inputFile, compactInput);
    const encodedInput = Buffer.from(JSON.stringify(compactInput), 'utf8').toString('hex').replace(/../g, '%$&');
    inputLine = `  // Full input sidecar for audit: ${path.basename(inputFile)}\n  const input = JSON.parse(decodeURIComponent(${JSON.stringify(encodedInput)}));\n`;
    evaluateArgs = ', input';
  }
  fs.writeFileSync(file, `async page => {\n${inputLine}  return await page.evaluate(${fn.toString()}${evaluateArgs});\n}\n`, 'utf8');
  return file;
}

function runCli(args, options = {}) {
  const env = { ...process.env, ProgramFiles: 'C:\\Program Files', LOCALAPPDATA: 'C:\\Users\\N30846\\AppData\\Local', SystemDrive: 'C:' };
  return spawnSync('npx', ['--yes', '--package', '@playwright/mcp', 'playwright-cli', ...args], {
    cwd: DEFAULT_ROOT,
    env,
    encoding: 'utf8',
    maxBuffer: options.maxBuffer || 1024 * 1024 * 20,
  });
}

function runCliRaw(args, options = {}) {
  return runCli(['--raw', ...args], options);
}

function isBrowserNotOpenOutput(text) {
  return /Browser '[^']+' is not open|to start the browser session/i.test(String(text || ''));
}

function isAuthFailureScan(scan) {
  const errors = scan && Array.isArray(scan.errors) ? scan.errors : [];
  return errors.length > 0 && errors.every(error => error?.json?.code === 410 || /用户未登录|not logged/i.test(String(error?.json?.msg || '')));
}

function isFetchFailureOutput(text) {
  return /Failed to fetch/i.test(String(text || ''));
}

function parsePlaywrightResult(stdout, label, outDir) {
  const match = String(stdout || '').match(/### Result\s*\r?\n([\s\S]*?)\r?\n### Ran Playwright code/);
  if (!match) throw new Error(`Cannot parse Playwright result for ${label}. See ${path.join(outDir, `${label}.out`)}`);
  return JSON.parse(match[1]);
}

function runPlaywrightFunction(fn, label, outDir, input, options = {}) {
  const file = writePlaywrightFunction(fn, label, outDir, input);
  const args = ['-s=' + SESSION, 'run-code', '--filename', file];
  let res = runCli(args);
  fs.writeFileSync(path.join(outDir, `${label}.out`), `${res.stdout || ''}${res.stderr || ''}`, 'utf8');
  if (res.error) throw res.error;
  const text = `${res.stdout || ''}${res.stderr || ''}`;
  if (options.recoverAuth && (isBrowserNotOpenOutput(text) || isFetchFailureOutput(text))) {
    ensureAuthenticated(outDir);
    res = runCli(args);
    fs.writeFileSync(path.join(outDir, `${label}.out`), `${res.stdout || ''}${res.stderr || ''}`, 'utf8');
    if (res.error) throw res.error;
  }
  return parsePlaywrightResult(res.stdout || '', label, outDir);
}

function getStoredCredential(target = 'df-cms-review/tongyifeng') {
  const script = `
    $target = ${JSON.stringify(target)}
    if (Get-Command Get-StoredCredential -ErrorAction SilentlyContinue) {
      $cred = Get-StoredCredential -Target $target
      if ($cred) {
        $user = $cred.UserName
        $pass = $cred.GetNetworkCredential().Password
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        ConvertTo-Json @{ username = $user; password = $pass } -Compress
      }
    }
  `;
  const res = spawnSync('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script], { encoding: 'utf8', maxBuffer: 1024 * 1024 });
  if (res.status !== 0 || !String(res.stdout || '').trim()) return null;
  try {
    const parsed = JSON.parse(String(res.stdout).trim());
    if (parsed.username && parsed.password) return parsed;
  } catch (_) {}
  return null;
}

function getLoginCredentials() {
  const username = process.env.DF_CMS_USER;
  const password = process.env.DF_CMS_PASS;
  if (username && password) return { username, password, source: 'env' };
  const stored = getStoredCredential();
  if (stored) return { ...stored, source: 'credential-manager' };
  return null;
}

function probeAuth() {
  const code = `async page => {
    try {
      return await page.evaluate(async () => {
        const r = await fetch('${API_BASE}/share-api/audit/list?scope=public&game_type=10001&audit_state=init&page=1&size=1', { credentials: 'include' });
        const j = await r.json().catch(e => ({ code: -1, msg: e.message }));
        return { status: r.status, code: j.code, msg: j.msg || '', hasResult: !!j.result };
      });
    } catch (error) {
      return { status: 0, code: -1, msg: error.message || String(error), hasResult: false };
    }
  }`;
  const res = runCliRaw(['-s=' + SESSION, 'run-code', code], { maxBuffer: 1024 * 1024 });
  if (res.error || res.status !== 0) return { ok: false, output: `${res.stdout || ''}${res.stderr || ''}` };
  try {
    const json = JSON.parse(String(res.stdout || '').trim());
    return { ok: json.status === 200 && json.code === 0, json };
  } catch (_) {
    return { ok: false, output: res.stdout || '' };
  }
}

function ensureAuthenticated(outDir) {
  ensureDir(path.dirname(AUTH_STATE_FILE));
  let open = runCli(['-s=' + SESSION, 'open', 'https://df.cc.163.com']);
  if (open.error) throw open.error;
  if (fs.existsSync(AUTH_STATE_FILE)) {
    runCli(['-s=' + SESSION, 'state-load', AUTH_STATE_FILE]);
    runCliRaw(['-s=' + SESSION, 'goto', 'https://df.cc.163.com']);
  }
  let probe = probeAuth();
  if (probe.ok) return true;

  const credentials = getLoginCredentials();
  if (!credentials) {
    throw new Error('CMS login required: set DF_CMS_USER and DF_CMS_PASS or configure Windows Credential Manager target df-cms-review/tongyifeng');
  }

  runCliRaw(['-s=' + SESSION, 'goto', 'https://df.cc.163.com/addon/list']);
  runCliRaw(['-s=' + SESSION, 'fill', 'input[name="mesgid"]', credentials.username]);
  runCliRaw(['-s=' + SESSION, 'fill', 'input[name="mesgpw"]', credentials.password]);
  runCliRaw(['-s=' + SESSION, 'run-code', `async page => {
    await page.evaluate(() => {
      for (const sel of ['#mesg_id_for_remember','input[name=remember]','#mesg_id_for_privacy','input[name=privacy]']) {
        const el = document.querySelector(sel);
        if (el) {
          el.checked = true;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
    });
    const login = page.getByRole('button', { name: '登录' });
    if (await login.count()) await login.click();
    await page.waitForTimeout(1200);
    const agree = page.getByRole('button', { name: '同意' });
    if (await agree.count()) {
      await agree.click();
      await page.waitForTimeout(500);
      if (await login.count()) await login.click();
    }
    await page.waitForTimeout(5000);
    if (page.url().includes('/login/oauth/callback')) {
      await page.goto('https://df.cc.163.com', { waitUntil: 'domcontentloaded', timeout: 60000 });
    }
    return { url: page.url(), title: await page.title() };
  }`]);
  probe = probeAuth();
  if (!probe.ok) throw new Error('CMS auto login failed; verify DF_CMS_USER/DF_CMS_PASS or login manually');
  const save = runCliRaw(['-s=' + SESSION, 'state-save', AUTH_STATE_FILE]);
  if (save.error || save.status !== 0) {
    fs.writeFileSync(path.join(outDir || DEFAULT_ROOT, 'auth_state_save_failed.out'), `${save.stdout || ''}${save.stderr || ''}`, 'utf8');
  }
  return true;
}

function buildRecords(scan) {
  return scan.records.map(r => {
    const suggestion = suggest(r);
    return { ...r, suggestion, imageCheck: imageNote(r) };
  });
}

function safeName(s) { return String(s || '').replace(/[^a-zA-Z0-9_.-]+/g, '_').slice(0, 80) || 'item'; }
async function downloadImages(summary, outDir) {
  const imagesDir = path.join(outDir, 'images');
  ensureDir(imagesDir);
  const manifest = [];
  let index = 1;
  for (const record of summary.records) {
    for (const url of record.imageUrls || []) {
      if (!/^https?:\/\//i.test(url) || /\.zip(\?|$)/i.test(url)) continue;
      const extMatch = new URL(url).pathname.match(/\.([a-zA-Z0-9]{2,5})$/);
      const ext = extMatch ? extMatch[1].toLowerCase() : 'jpg';
      const fileName = `${String(index).padStart(3, '0')}_${record.section}_${safeName(record.id)}.${ext}`;
      const filePath = path.join(imagesDir, fileName);
      const entry = { index, id: record.id, section: record.section, title: record.title, url, file: filePath };
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const buffer = Buffer.from(await res.arrayBuffer());
        fs.writeFileSync(filePath, buffer);
        entry.bytes = buffer.length;
        entry.ok = true;
      } catch (e) {
        entry.ok = false;
        entry.error = e.message;
      }
      manifest.push(entry);
      index++;
    }
  }
  writeJson(path.join(outDir, 'images_manifest.json'), manifest);
  const cards = manifest.map(m => `<figure><a href="${m.url}"><img src="images/${path.basename(m.file)}" loading="lazy"></a><figcaption>#${m.index} ${escapeHtml(m.section)} ${escapeHtml(m.id)}<br>${escapeHtml(truncate(m.title, 80))}<br>${m.ok ? `${m.bytes || 0} bytes` : `FAILED: ${escapeHtml(m.error || '')}`}</figcaption></figure>`).join('\n');
  const html = `<!doctype html><meta charset="utf-8"><title>审核图片 Contact Sheet</title><style>body{font-family:Arial,"Microsoft YaHei",sans-serif;margin:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}figure{border:1px solid #ddd;padding:8px;margin:0;background:#fff}img{max-width:100%;max-height:220px;display:block;margin:auto}figcaption{font-size:12px;line-height:1.4;word-break:break-all;margin-top:6px}</style><h1>审核图片 Contact Sheet</h1><p>Generated: ${escapeHtml(summary.scannedAt)}</p><div class="grid">${cards}</div>`;
  fs.writeFileSync(path.join(outDir, 'contact_sheet.html'), html, 'utf8');
  writeVisualContactSheet(manifest, outDir);
  return manifest;
}
function escapeHtml(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

function writeVisualContactSheet(manifest, outDir) {
  const okImages = (manifest || []).filter(item => item.ok && item.file && fs.existsSync(item.file));
  const outPath = path.join(outDir, 'contact_sheet_visual.png');
  if (okImages.length === 0) return null;
  const manifestPath = path.join(outDir, 'images_manifest.json');
  const script = String.raw`
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

manifest_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
items = [item for item in json.loads(manifest_path.read_text(encoding='utf-8')) if item.get('ok') and item.get('file')]
thumb_w, thumb_h = 420, 260
label_h = 70
cols = 2
rows = max(1, (len(items) + cols - 1) // cols)
sheet = Image.new('RGB', (cols * thumb_w, rows * (thumb_h + label_h)), 'white')
draw = ImageDraw.Draw(sheet)
for idx, item in enumerate(items):
    image_path = Path(item['file'])
    if not image_path.exists():
        continue
    im = Image.open(image_path).convert('RGB')
    im.thumbnail((thumb_w, thumb_h))
    x = (idx % cols) * thumb_w
    y = (idx // cols) * (thumb_h + label_h)
    sheet.paste(im, (x + (thumb_w - im.width) // 2, y))
    label = f"{item.get('index', idx + 1):03d}_{item.get('section','')}_{item.get('id','')}"
    title = str(item.get('title', ''))[:48]
    draw.text((x + 8, y + thumb_h + 6), label[:58], fill=(0, 0, 0))
    draw.text((x + 8, y + thumb_h + 28), title, fill=(0, 0, 0))
out_path.parent.mkdir(parents=True, exist_ok=True)
sheet.save(out_path)
`;
  const pythonEnv = { ...process.env, PYTHONIOENCODING: 'utf-8' };
  let res = spawnSync('py', ['-3', '-c', script, manifestPath, outPath], { encoding: 'utf8', maxBuffer: 1024 * 1024, env: pythonEnv });
  if (res.status !== 0) res = spawnSync('python', ['-c', script, manifestPath, outPath], { encoding: 'utf8', maxBuffer: 1024 * 1024, env: pythonEnv });
  if (res.status !== 0) {
    fs.writeFileSync(path.join(outDir, 'contact_sheet_visual.error.txt'), `${res.stdout || ''}${res.stderr || ''}`, 'utf8');
    return null;
  }
  return outPath;
}

function getImageReviewConfig(options = {}) {
  const apiKey = String(options.apiKey || process.env.AIGW_API_KEY || '').trim();
  if (!apiKey) return null;
  const baseUrl = String(options.baseUrl || process.env.AIGW_BASE_URL || DEFAULT_AIGW_BASE_URL).replace(/\/+$/, '');
  return {
    apiKey,
    baseUrl,
    endpoint: options.endpoint || process.env.AIGW_IMAGE_REVIEW_URL || `${baseUrl}${IMAGE_REVIEW_ENDPOINT_PATH}`,
    model: options.model || process.env.AIGW_IMAGE_REVIEW_MODEL || DEFAULT_IMAGE_REVIEW_MODEL,
    batchSize: clampInt(options.batchSize || process.env.AIGW_IMAGE_REVIEW_BATCH_SIZE, DEFAULT_IMAGE_REVIEW_BATCH_SIZE, 1, 12),
    timeoutMs: clampInt(options.timeoutMs || process.env.AIGW_IMAGE_REVIEW_TIMEOUT_MS, 60000, 5000, 180000),
    retryImageMaxSide: clampInt(options.retryImageMaxSide || process.env.AIGW_IMAGE_REVIEW_RETRY_MAX_SIDE, DEFAULT_RETRY_IMAGE_MAX_SIDE, 320, 4096),
    retryImageMaxBytes: clampInt(options.retryImageMaxBytes || process.env.AIGW_IMAGE_REVIEW_RETRY_MAX_BYTES, DEFAULT_RETRY_IMAGE_MAX_BYTES, 128 * 1024, 8 * 1024 * 1024),
  };
}

function emitProgress(options, stage, data = {}) {
  if (typeof options?.onProgress !== 'function') return;
  try {
    options.onProgress({ stage, ...data });
  } catch (_) {}
}

function mimeTypeForFile(file) {
  const ext = path.extname(String(file || '')).toLowerCase();
  if (ext === '.png') return 'image/png';
  if (ext === '.gif') return 'image/gif';
  if (ext === '.webp') return 'image/webp';
  if (ext === '.bmp') return 'image/bmp';
  return 'image/jpeg';
}

function imageDataUrl(file) {
  const data = fs.readFileSync(file).toString('base64');
  return `data:${mimeTypeForFile(file)};base64,${data}`;
}

function parseModelJson(content) {
  let text = '';
  if (typeof content === 'string') text = content;
  else if (Array.isArray(content)) text = content.map(part => part.text || part.content || '').join('\n');
  else if (content && typeof content === 'object') text = JSON.stringify(content);
  text = text.trim().replace(/^```(?:json)?/i, '').replace(/```$/i, '').trim();
  try {
    return JSON.parse(text);
  } catch (_) {
    const start = text.indexOf('{');
    const end = text.lastIndexOf('}');
    if (start >= 0 && end > start) return JSON.parse(text.slice(start, end + 1));
    throw new Error('Model response is not valid JSON');
  }
}

function normalizeImageDecision(value) {
  const text = String(value || '').trim().toLowerCase();
  if (['pass', 'ok', 'safe', '通过', '无风险'].includes(text)) return 'pass';
  if (['reject', 'block', 'blocked', 'fail', '违规', '拒绝'].includes(text)) return 'reject';
  return 'uncertain';
}

function extractModelResults(body) {
  const content = body?.choices?.[0]?.message?.content || body?.choices?.[0]?.delta?.content || body?.output_text || body?.content;
  const parsed = typeof content === 'string' || Array.isArray(content) ? parseModelJson(content) : body;
  const rows = Array.isArray(parsed?.results) ? parsed.results : (Array.isArray(parsed) ? parsed : []);
  return rows.map(row => ({
    index: Number(row.index || row.image_index || row.id || 0),
    decision: normalizeImageDecision(row.decision || row.action || row.result),
    riskType: String(row.risk_type || row.riskType || ''),
    evidenceSummary: String(row.evidence_summary || row.evidenceSummary || row.reason || ''),
  })).filter(row => row.index > 0);
}

function hasCrossProductEvidence(text) {
  return /(明日方舟|终末地|原神|崩坏|星穹铁道|王者荣耀|和平精英|阴阳师|炉石传说)/i.test(String(text || ''));
}

function confidenceFlagsForDecision(row, mode) {
  const flags = [];
  const decision = normalizeImageDecision(row?.decision || row?.finalDecision);
  const evidence = String(row?.evidenceSummary || row?.evidence_summary || '');
  if (decision === 'pass' && mode === 'single' && !evidence.trim()) flags.push('empty_pass_evidence');
  if (decision === 'pass' && hasCrossProductEvidence(evidence)) flags.push('cross_product_description');
  return flags;
}

function applyConfidencePolicy(row, mode) {
  const flags = confidenceFlagsForDecision(row, mode);
  const next = { ...row, confidenceFlags: [...new Set([...(row.confidenceFlags || []), ...flags])] };
  if (flags.length && normalizeImageDecision(next.decision || next.finalDecision) === 'pass') {
    next.decision = 'uncertain';
    next.finalDecision = 'uncertain';
    next.riskType = next.riskType || '模型证据不足';
    next.evidenceSummary = next.evidenceSummary || (flags.includes('empty_pass_evidence') ? '模型返回通过但缺少可核查证据' : '模型描述疑似偏离魔兽/DD/WA上下文');
  }
  return next;
}

function buildImageReviewPrompt(items, mode) {
  const ids = items.map(item => `#${item.index} SN=${item.id || ''} section=${item.section || ''} title=${truncate(item.title || '', 60)}`).join('\n');
  return [
    '你是网易 DD 配置分享库和 WA 库的图片审核助手。',
    '审核目标：识别色情低俗、赌博诈骗、二维码/联系方式/站外引流、外挂黑产、账号交易、现实政治敏感、台独/分裂表达、无关广告等风险。',
    '这些图片应主要是魔兽世界、网易DD、WA字符串、配置分享、游戏界面截图或插件配置内容；如果你描述成其他游戏/产品，或无法确认上下文，请用 uncertain。',
    mode === 'batch' ? '当前图片是一张 contact sheet，请按每个编号分别判断。' : '当前图片是单图复核，请只判断这个编号。',
    '只输出 JSON，不要输出 Markdown。格式：{"results":[{"index":1,"decision":"pass|reject|uncertain","risk_type":"","evidence_summary":""}]}',
    '每个 pass 必须给出一句可核查证据，不能只写“无风险”；无法看清、小字/二维码/水印无法确认、动图内容不完整、边界不稳时 decision 用 uncertain。',
    '待审编号：',
    ids,
  ].join('\n');
}

async function fetchJsonWithTimeout(url, payload, config, fetchImpl) {
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timer = controller ? setTimeout(() => controller.abort(), config.timeoutMs) : null;
  const startedAt = Date.now();
  try {
    const response = await fetchImpl(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify(payload),
      signal: controller?.signal,
    });
    const text = await response.text();
    let body = {};
    try { body = text ? JSON.parse(text) : {}; } catch (_) { body = { raw_text: text }; }
    const durationMs = Date.now() - startedAt;
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}: ${body?.error?.message || body?.message || body?.raw_text || ''}`);
      error.status = response.status;
      error.body = body;
      error.durationMs = durationMs;
      throw error;
    }
    return { body, status: response.status, durationMs };
  } catch (error) {
    const next = new Error(redactSecretText(error.message || String(error)));
    next.status = error.status || 0;
    next.body = error.body || null;
    next.durationMs = error.durationMs || (Date.now() - startedAt);
    throw next;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function buildCallAudit(callId, config, mode, imageFile, items, status, body, durationMs, error) {
  return {
    callId,
    endpoint: config.endpoint,
    model: config.model,
    mode,
    file: imageFile,
    images: (items || []).map(item => ({ index: item.index, id: item.id, section: item.section, title: item.title || '' })),
    status: status || 0,
    responseId: body?.id || body?.data?.id || '',
    durationMs: durationMs || 0,
    resultCount: 0,
    error: error ? redactSecretText(error.message || String(error)) : '',
  };
}

async function callImageReviewModel(imageFile, items, mode, config, fetchImpl, callId) {
  const payload = {
    model: config.model,
    temperature: 0,
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: buildImageReviewPrompt(items, mode) },
          { type: 'image_url', image_url: { url: imageDataUrl(imageFile) } },
        ],
      },
    ],
  };
  const audit = buildCallAudit(callId, config, mode, imageFile, items);
  try {
    const response = await fetchJsonWithTimeout(config.endpoint, payload, config, fetchImpl);
    const rows = extractModelResults(response.body);
    audit.status = response.status;
    audit.responseId = response.body?.id || response.body?.data?.id || '';
    audit.durationMs = response.durationMs;
    audit.resultCount = rows.length;
    return { rows, audit };
  } catch (error) {
    audit.status = error.status || 0;
    audit.durationMs = error.durationMs || 0;
    audit.error = redactSecretText(error.message || String(error));
    return { rows: [], audit, error };
  }
}

function isRetryableImageReviewError(result) {
  const errorText = `${result?.error?.message || ''} ${result?.audit?.error || ''}`;
  return Boolean(result?.error) && (
    Number(result?.audit?.status || result?.error?.status || 0) === 0
    || /abort|timeout|timed out|network|fetch failed|socket|econnreset/i.test(errorText)
  );
}

function compressImageForModelRetry(imageFile, outDir, imageIndex, config) {
  const retryDir = path.join(outDir, 'image_model_batches', 'single_retry');
  ensureDir(retryDir);
  const outPath = path.join(retryDir, `${String(imageIndex || 'image').padStart(3, '0')}_${safeName(path.basename(imageFile, path.extname(imageFile)))}.jpg`);
  const script = String.raw`
import sys
from pathlib import Path
from PIL import Image

src = Path(sys.argv[1])
out = Path(sys.argv[2])
max_side = int(sys.argv[3])
max_bytes = int(sys.argv[4])
out.parent.mkdir(parents=True, exist_ok=True)
im = Image.open(src)
try:
    if getattr(im, 'is_animated', False):
        im.seek(0)
except Exception:
    pass
has_alpha = im.mode in ('RGBA', 'LA') or ('transparency' in im.info)
if has_alpha:
    rgba = im.convert('RGBA')
    bg = Image.new('RGBA', rgba.size, 'WHITE')
    bg.alpha_composite(rgba)
    im = bg.convert('RGB')
else:
    im = im.convert('RGB')
im.thumbnail((max_side, max_side))
quality = 85
while True:
    im.save(out, format='JPEG', quality=quality, optimize=True)
    if out.stat().st_size <= max_bytes or quality <= 55:
        break
    quality -= 10
print(str(out))
`;
  const pythonEnv = { ...process.env, PYTHONIOENCODING: 'utf-8' };
  let res = spawnSync('py', ['-3', '-c', script, imageFile, outPath, String(config.retryImageMaxSide), String(config.retryImageMaxBytes)], { encoding: 'utf8', maxBuffer: 1024 * 1024, env: pythonEnv });
  if (res.status !== 0) res = spawnSync('python', ['-c', script, imageFile, outPath, String(config.retryImageMaxSide), String(config.retryImageMaxBytes)], { encoding: 'utf8', maxBuffer: 1024 * 1024, env: pythonEnv });
  if (res.status !== 0 || !fs.existsSync(outPath)) {
    throw new Error(redactSecretText(`${res.stdout || ''}${res.stderr || ''}`.trim() || 'Failed to compress retry image'));
  }
  return outPath;
}

async function callSingleImageReviewWithRetry(image, config, fetchImpl, nextCallId, calls, outDir, options = {}) {
  const singleCallId = nextCallId('single');
  emitProgress(options, 'single_review', { index: image.index, id: image.id, retry: false });
  let selectedCallId = singleCallId;
  let selected = await callImageReviewModel(image.file, [image], 'single', config, fetchImpl, singleCallId);
  calls.push(selected.audit);
  if (isRetryableImageReviewError(selected)) {
    try {
      const retryFile = compressImageForModelRetry(image.file, outDir, image.index, config);
      const retryCallId = nextCallId('single_retry');
      emitProgress(options, 'single_review', { index: image.index, id: image.id, retry: true });
      const retry = await callImageReviewModel(retryFile, [image], 'single_retry', config, fetchImpl, retryCallId);
      retry.audit.retryOf = singleCallId;
      retry.audit.originalFile = image.file;
      retry.audit.compressed = true;
      calls.push(retry.audit);
      selected = retry;
      selectedCallId = retryCallId;
    } catch (error) {
      selected.error = selected.error || new Error(redactSecretText(error.message || String(error)));
      selected.audit.error = selected.audit.error || redactSecretText(error.message || String(error));
    }
  }
  return { callId: selectedCallId, result: selected };
}

function buildModelBatchSheets(manifest, outDir, batchSize) {
  const okImages = (manifest || []).filter(item => item.ok && item.file && fs.existsSync(item.file));
  if (okImages.length === 0) return { batches: [], imageInfo: {} };
  const batchDir = path.join(outDir, 'image_model_batches');
  ensureDir(batchDir);
  const manifestPath = path.join(batchDir, 'model_manifest_input.json');
  writeJson(manifestPath, okImages);
  const script = String.raw`
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

manifest_path = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
batch_size = int(sys.argv[3])
items = [item for item in json.loads(manifest_path.read_text(encoding='utf-8')) if item.get('ok') and item.get('file') and Path(item.get('file')).exists()]
out_dir.mkdir(parents=True, exist_ok=True)
thumb_w, thumb_h = 360, 220
label_h = 76
cols = 2
batches = []
image_info = {}
for start in range(0, len(items), batch_size):
    chunk = items[start:start + batch_size]
    rows = max(1, (len(chunk) + cols - 1) // cols)
    sheet = Image.new('RGB', (cols * thumb_w, rows * (thumb_h + label_h)), 'white')
    draw = ImageDraw.Draw(sheet)
    for idx, item in enumerate(chunk):
        image_path = Path(item['file'])
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        try:
            im = Image.open(image_path)
            width, height = im.size
            has_alpha = im.mode in ('RGBA', 'LA') or ('transparency' in im.info)
            image_info[str(item.get('index'))] = {
                'width': width,
                'height': height,
                'hasAlpha': bool(has_alpha),
                'aspectRatio': float(max(width, height)) / max(1, min(width, height)),
            }
            if has_alpha:
                bg = Image.new('RGBA', im.size, 'WHITE')
                bg.alpha_composite(im.convert('RGBA'))
                im = bg.convert('RGB')
            else:
                im = im.convert('RGB')
            im.thumbnail((thumb_w - 12, thumb_h - 12))
            sheet.paste(im, (x + (thumb_w - im.width) // 2, y + 6))
        except Exception as exc:
            image_info[str(item.get('index'))] = {'error': str(exc)}
            draw.text((x + 8, y + 40), 'IMAGE LOAD FAILED', fill=(160, 0, 0))
        draw.rectangle((x, y, x + thumb_w - 1, y + thumb_h + label_h - 1), outline=(210, 210, 210))
        label = f"#{item.get('index')} SN={item.get('id','')} {item.get('section','')}"
        title = str(item.get('title', ''))[:46]
        draw.text((x + 8, y + thumb_h + 8), label[:58], fill=(0, 0, 0))
        draw.text((x + 8, y + thumb_h + 30), title, fill=(0, 0, 0))
    batch_no = len(batches) + 1
    file_path = out_dir / f"model_contact_sheet_{batch_no:03d}.png"
    sheet.save(file_path)
    batches.append({'batchIndex': batch_no, 'file': str(file_path), 'items': chunk})
print(json.dumps({'batches': batches, 'imageInfo': image_info}, ensure_ascii=False))
`;
  const pythonEnv = { ...process.env, PYTHONIOENCODING: 'utf-8' };
  let res = spawnSync('py', ['-3', '-c', script, manifestPath, batchDir, String(batchSize)], { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024, env: pythonEnv });
  if (res.status !== 0) res = spawnSync('python', ['-c', script, manifestPath, batchDir, String(batchSize)], { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024, env: pythonEnv });
  if (res.status !== 0) {
    fs.writeFileSync(path.join(outDir, 'image_model_review.error.txt'), redactSecretText(`${res.stdout || ''}${res.stderr || ''}`), 'utf8');
    throw new Error('Failed to build model contact sheets');
  }
  return JSON.parse(res.stdout);
}

function needsSingleImageReview(image, initial, imageInfo, record) {
  const ext = path.extname(String(image.file || image.url || '')).toLowerCase();
  const info = imageInfo[String(image.index)] || {};
  const evidence = `${initial.riskType || ''} ${initial.evidenceSummary || ''}`;
  if (initial.decision !== 'pass') return true;
  if (record?.auditStateValue === 'niv_failed' || (record?.nivFailedImgs || []).length > 0) return true;
  if (['.gif', '.webp'].includes(ext)) return true;
  if (info.error || Number(info.width) < 80 || Number(info.height) < 80 || Number(info.aspectRatio) >= 4) return true;
  const cleanEvidence = stripHtml(evidence);
  if (!cleanEvidence || /^(无风险|未见风险|未见违规|正常|ok|pass)$/i.test(cleanEvidence.trim())) return true;
  const riskEvidence = cleanEvidence.replace(/(未见|没有|无)[^，。；;]*(二维码|QR|联系方式|微信|QQ|VX|群|水印|广告|引流|站外|网址|链接)[^，。；;]*/ig, '');
  return /(小字|文字|看不清|无法确认|模糊|二维码|QR|联系方式|微信|QQ|VX|群|水印|广告|引流|站外|网址|链接)/i.test(riskEvidence);
}

function resultForMissingImage(image, reason) {
  return {
    index: image.index,
    id: image.id,
    section: image.section,
    title: image.title,
    ok: false,
    initialDecision: 'uncertain',
    finalDecision: 'uncertain',
    riskType: '无法审阅图片',
    evidenceSummary: reason || image.error || '图片未下载或无法读取',
    reviewMode: 'unavailable',
    sourceCallId: '',
    batchCallId: '',
    singleCallId: '',
    coverageStatus: 'missing',
    confidenceFlags: ['unavailable'],
  };
}

function summarizeImageModelReview(results, model, expectedCount = null) {
  const passCount = results.filter(row => row.finalDecision === 'pass').length;
  const rejectCount = results.filter(row => row.finalDecision === 'reject').length;
  const uncertainCount = results.filter(row => row.finalDecision === 'uncertain').length;
  const errorCount = results.filter(row => row.error || row.ok === false).length;
  const expected = Number(expectedCount ?? results.length);
  const coverageMissingCount = Math.max(0, expected - results.length) + results.filter(row => row.coverageStatus !== 'covered' || !row.sourceCallId).length;
  return {
    required: results.length > 0,
    status: results.length === 0 ? 'none' : (rejectCount || uncertainCount || errorCount || coverageMissingCount ? 'model_blocked' : 'model_passed'),
    artifact: results.length > 0 ? 'image_model_review.json' : '',
    model: model || '',
    passCount,
    rejectCount,
    uncertainCount,
    errorCount,
    expectedCount: expected,
    resultCount: results.length,
    coverageMissingCount,
  };
}

function loadReusableImageModelReview(outDir, imageManifest) {
  const reviewPath = path.join(outDir, 'image_model_review.json');
  const callsPath = path.join(outDir, 'image_model_review_calls.json');
  if (!fs.existsSync(reviewPath) || !fs.existsSync(callsPath)) return null;
  let review;
  let calls;
  try {
    review = readJsonNoBom(reviewPath);
    calls = readJsonNoBom(callsPath);
  } catch (_) {
    return null;
  }
  if (!Array.isArray(review?.results) || !Array.isArray(calls)) return null;
  const manifest = imageManifest || [];
  if (review.results.length !== manifest.length) return null;
  const byIndex = new Map(review.results.map(row => [Number(row.index), row]));
  const callsById = new Map(calls.map(call => [String(call.callId || ''), call]));
  for (const image of manifest) {
    const row = byIndex.get(Number(image.index));
    if (!row) return null;
    if (String(row.id || '') && String(image.id || '') && String(row.id) !== String(image.id)) return null;
    const available = image.ok && image.file && fs.existsSync(image.file);
    if (!available) continue;
    if (row.coverageStatus !== 'covered' || !row.sourceCallId) return null;
    const call = callsById.get(String(row.sourceCallId));
    if (!call || Number(call.status) < 200 || Number(call.status) >= 300) return null;
  }
  const model = review.model || review.imageReview?.model || DEFAULT_IMAGE_REVIEW_MODEL;
  return {
    model,
    results: review.results,
    imageReview: summarizeImageModelReview(review.results, model, manifest.length),
    calls,
    resumed: true,
  };
}

async function reviewImagesWithModel(summary, imageManifest, outDir, options = {}) {
  const reusable = loadReusableImageModelReview(outDir, imageManifest);
  if (reusable) {
    emitProgress(options, 'image_model_resume', { resultCount: reusable.results.length });
    return reusable;
  }
  const config = getImageReviewConfig(options);
  if (!config) return null;
  const fetchImpl = options.fetchImpl || fetch;
  const recordsById = new Map((summary.records || []).map(record => [String(record.id), record]));
  const results = [];
  const calls = [];
  let callSeq = 1;
  const nextCallId = mode => `img-${mode}-${String(callSeq++).padStart(4, '0')}`;
  const failedImages = (imageManifest || []).filter(image => !image.ok || !image.file || !fs.existsSync(image.file));
  for (const image of failedImages) results.push(resultForMissingImage(image));
  const okImages = (imageManifest || []).filter(image => image.ok && image.file && fs.existsSync(image.file));
  let batches = [];
  let imageInfo = {};
  if (okImages.length) {
    try {
      const built = buildModelBatchSheets(okImages, outDir, config.batchSize);
      batches = built.batches || [];
      imageInfo = built.imageInfo || {};
    } catch (error) {
      for (const image of okImages) results.push(resultForMissingImage(image, error.message));
      const imageReview = summarizeImageModelReview(results, config.model, imageManifest.length);
      writeJson(path.join(outDir, 'image_model_review_calls.json'), calls);
      writeJson(path.join(outDir, 'image_model_review.json'), { model: config.model, generatedAt: new Date().toISOString(), imageReview, results });
      return { model: config.model, results, imageReview, calls };
    }
  }
  emitProgress(options, 'batch_review', { batches: batches.length, images: okImages.length });
  for (const batch of batches) {
    let batchRows = [];
    const batchCallId = nextCallId('batch');
    const batchResult = await callImageReviewModel(batch.file, batch.items, 'batch', config, fetchImpl, batchCallId);
    calls.push(batchResult.audit);
    if (batchResult.error) {
      batchRows = batch.items.map(item => ({ index: Number(item.index), decision: 'uncertain', riskType: '模型调用失败', evidenceSummary: redactSecretText(batchResult.error.message), sourceCallId: batchCallId }));
    } else {
      batchRows = batchResult.rows.map(row => ({ ...row, sourceCallId: batchCallId }));
    }
    const batchByIndex = new Map(batchRows.map(row => [Number(row.index), row]));
    for (const image of batch.items) {
      const initial = batchByIndex.get(Number(image.index)) || { index: image.index, decision: 'uncertain', riskType: '模型结果缺失', evidenceSummary: '模型未返回该编号的结果' };
      let final = initial;
      let reviewMode = 'batch';
      let singleCallId = '';
      const record = recordsById.get(String(image.id));
      if (needsSingleImageReview(image, initial, imageInfo, record)) {
        reviewMode = 'single';
        const single = await callSingleImageReviewWithRetry(image, config, fetchImpl, nextCallId, calls, outDir, options);
        singleCallId = single.callId;
        const singleResult = single.result;
        if (singleResult.error) {
          final = { index: image.index, decision: 'uncertain', riskType: '单图复核失败', evidenceSummary: redactSecretText(singleResult.error.message), sourceCallId: singleCallId };
        } else {
          final = singleResult.rows.find(row => Number(row.index) === Number(image.index)) || singleResult.rows[0] || initial;
          final = { ...final, sourceCallId: singleCallId };
        }
      }
      final = applyConfidencePolicy(final, reviewMode);
      const finalDecision = normalizeImageDecision(final.decision || final.finalDecision);
      const sourceCallId = final.sourceCallId || initial.sourceCallId || '';
      results.push({
        index: image.index,
        id: image.id,
        section: image.section,
        title: image.title,
        file: image.file,
        url: image.url,
        initialDecision: initial.decision,
        finalDecision,
        riskType: final.riskType || '',
        evidenceSummary: final.evidenceSummary || '',
        reviewMode,
        sourceCallId,
        batchCallId,
        singleCallId,
        coverageStatus: sourceCallId ? 'covered' : 'missing',
        confidenceFlags: final.confidenceFlags || [],
        imageInfo: imageInfo[String(image.index)] || {},
      });
    }
  }
  results.sort((a, b) => Number(a.index) - Number(b.index));
  const imageReview = summarizeImageModelReview(results, config.model, imageManifest.length);
  writeJson(path.join(outDir, 'image_model_review_calls.json'), calls);
  writeJson(path.join(outDir, 'image_model_review.json'), { model: config.model, generatedAt: new Date().toISOString(), imageReview, results });
  return { model: config.model, results, imageReview, calls };
}

function applyImageModelReview(summary, modelResults) {
  const rawResults = Array.isArray(modelResults) ? modelResults : (modelResults?.results || []);
  const results = rawResults.map(row => applyConfidencePolicy({
    ...row,
    decision: row.decision || row.finalDecision,
  }, row.reviewMode || (row.singleCallId ? 'single' : 'batch')));
  const byId = new Map();
  for (const row of results) {
    const id = String(row.id || '');
    if (!id) continue;
    if (!byId.has(id)) byId.set(id, []);
    byId.get(id).push(row);
  }
  for (const record of summary.records || []) {
    const rows = byId.get(String(record.id)) || [];
    if (!rows.length) continue;
    const reject = rows.find(row => row.finalDecision === 'reject');
    const uncertain = rows.find(row => row.finalDecision === 'uncertain' || row.error);
    if (reject) {
      record.suggestion = {
        ...(record.suggestion || {}),
        action: 'reject',
        reason: record.section === 'wa' ? WA_REJECT_REASON : SHARE_REJECT_REASON,
        issue: reject.riskType || reject.evidenceSummary || '图片模型审核发现风险',
        executable: true,
      };
      record.imageCheck = `模型审图拒绝：${reject.evidenceSummary || reject.riskType || '图片存在风险'}`;
    } else if (uncertain) {
      record.suggestion = {
        ...(record.suggestion || {}),
        action: 'manualConfirm',
        reason: '',
        issue: uncertain.riskType || uncertain.evidenceSummary || '图片模型审核无法确认',
        executable: false,
      };
      record.imageCheck = `模型审图需人工确认：${uncertain.evidenceSummary || uncertain.riskType || '图片无法确认'}`;
    } else if (rows.every(row => row.finalDecision === 'pass')) {
      record.imageCheck = '模型审图未见明显问题';
    }
  }
  summary.imageReview = summarizeImageModelReview(results, modelResults?.model || summary.imageReview?.model || DEFAULT_IMAGE_REVIEW_MODEL, summary.imageManifestCount || summary.imageManifest?.length || results.length);
  return recalculateCounts(summary);
}
function renderMarkdown(summary) {
  const lines = [];
  lines.push(`# 配置分享库 & WA库审核报告`);
  lines.push('');
  lines.push(`- 扫描时间：${summary.scannedAt}`);
  lines.push(`- 扫描组合：${summary.scannedCombos}`);
  lines.push(`- 待处理记录：${summary.records.length}`);
  lines.push(`- 接口错误：${summary.errors.length}`);
  lines.push('');
  lines.push(`## 汇总`);
  lines.push('');
  for (const [action, count] of Object.entries(summary.counts)) lines.push(`- ${action}: ${count}`);
  if (summary.imageReview) {
    lines.push(`- 图片模型审核：${summary.imageReview.status || 'pending'}；pass=${summary.imageReview.passCount || 0} reject=${summary.imageReview.rejectCount || 0} uncertain=${summary.imageReview.uncertainCount || 0} error=${summary.imageReview.errorCount || 0}`);
  }
  lines.push('');
  lines.push(`## 明细`);
  for (const r of summary.records) {
    const actualScope = scopeLabel(r.scopeValue || r.raw?.scope || r.combo.scopeValue) || r.combo.scope;
    const comboScope = r.combo.scope || scopeLabel(r.combo.scopeValue);
    lines.push('');
    lines.push(`### ${r.section === 'share' ? '配置分享' : 'WA'}｜${r.title || '(无标题)'}`);
    lines.push(`- ID/SN：${r.id}`);
    lines.push(`- 组合：${r.combo.gameType} / ${actualScope} / ${r.combo.auditState}${r.section === 'wa' ? ' / 用户发布' : ''}`);
    if (comboScope && actualScope && comboScope !== actualScope) lines.push(`- 查询组合：${comboScope}`);
    lines.push(`- 作者账号：${r.account || ''}`);
    lines.push(`- 字段摘录：名称=${truncate(r.title, 80)}；简介=${truncate(stripHtml(r.fields?.brief), 120)}；详情=${truncate(stripHtml(r.fields?.detail), 220)}；更新=${truncate(stripHtml(r.fields?.updateDesc), 160)}`);
    lines.push(`- 图片检查：${r.imageCheck}`);
    if (r.reviewed_by_prior_override) lines.push(`- 历史改判参考：相似记录曾由 ${r.priorOverride?.originalAction || ''} 改为 ${r.priorOverride?.newAction || ''}，仅作参考`);
    lines.push(`- 问题点：${r.suggestion.issue || '未见明显问题'}`);
    if (r.suggestion.action === 'manualConfirm' || r.suggestion.executable === false) lines.push(`- 不可自动执行：${r.suggestion.issue || r.suggestion.reason || '需人工确认'}`);
    lines.push(`- 建议动作：${r.suggestion.action}${r.suggestion.reason ? `；拒绝理由=${r.suggestion.reason}` : ''}`);
  }
  return lines.join('\n');
}

function buildManualConfirmRows(summary) {
  const imageById = new Map();
  for (const image of summary.imageManifest || []) {
    if (!imageById.has(image.id)) imageById.set(image.id, []);
    if (image.file) imageById.get(image.id).push(image.file);
  }
  return (summary.records || [])
    .filter(record => record.suggestion && record.suggestion.action === 'manualConfirm')
    .map(record => ({
      id: record.id,
      section: record.section,
      title: record.title || '',
      combo: [record.combo?.gameType, scopeLabel(record.scopeValue || record.raw?.scope || record.combo?.scopeValue) || record.combo?.scope, record.combo?.auditState].filter(Boolean).join(' / '),
      reason: record.suggestion.issue || record.suggestion.reason || '需人工确认',
      localImages: imageById.get(record.id) || [],
      suggestedAction: 'manualConfirm',
    }));
}

function makeSummary(scan, outDir) {
  const records = buildRecords(scan);
  const counts = {};
  for (const r of records) counts[r.suggestion.action] = (counts[r.suggestion.action] || 0) + 1;
  return { scannedAt: scan.scannedAt, scannedCombos: scan.scannedCombos, recordsCount: records.length, errorsCount: scan.errors.length, counts, records, errors: scan.errors, outDir };
}

function recalculateCounts(input) {
  const counts = { reject: 0, autoPass: 0, manualConfirm: 0, transferPrivateThenPass: 0 };
  for (const record of input.records || []) {
    const action = record.suggestion && record.suggestion.action;
    if (action) counts[action] = (counts[action] || 0) + 1;
  }
  input.counts = counts;
  return input;
}

function buildImageReview(imageManifestCount) {
  return imageManifestCount > 0
    ? { required: true, status: 'pending', artifact: 'contact_sheet_visual.png' }
    : { required: false, status: 'none' };
}

function compactExecuteInput(input) {
  const next = JSON.parse(JSON.stringify(input));
  for (const record of next.records || []) {
    if (record.suggestion && record.suggestion.action === 'transferPrivateThenPass') continue;
    delete record.raw;
  }
  return next;
}

function listArg(value) {
  if (!value || value === true) return [];
  return String(value).split(',').map(x => x.trim()).filter(Boolean);
}

function loadOverrideIds(args) {
  const approveIds = new Set([...listArg(args['approve-id']), ...listArg(args.approveId)]);
  const transferPrivateIds = new Set([...listArg(args['transfer-private-id']), ...listArg(args.transferPrivateId)]);
  const rejectIds = new Set([...listArg(args['reject-id']), ...listArg(args.rejectId)]);
  const manualConfirmIds = new Set([...listArg(args['manual-confirm-id']), ...listArg(args.manualConfirmId)]);
  if (args.override && args.override !== true) {
    const override = readJsonNoBom(args.override);
    for (const id of override.approveIds || override.approve_ids || []) approveIds.add(String(id));
    for (const id of override.transferPrivateIds || override.transfer_private_ids || []) transferPrivateIds.add(String(id));
    for (const id of override.rejectIds || override.reject_ids || []) rejectIds.add(String(id));
    for (const id of override.manualConfirmIds || override.manual_confirm_ids || []) manualConfirmIds.add(String(id));
  }
  return { approveIds, transferPrivateIds, rejectIds, manualConfirmIds };
}

function overrideActionMap(args) {
  const { approveIds, transferPrivateIds, rejectIds, manualConfirmIds } = loadOverrideIds(args || {});
  const actions = new Map();
  for (const id of approveIds) actions.set(id, 'autoPass');
  for (const id of transferPrivateIds) actions.set(id, 'transferPrivateThenPass');
  for (const id of rejectIds) actions.set(id, 'reject');
  for (const id of manualConfirmIds) actions.set(id, 'manualConfirm');
  return actions;
}

function hasOverrideArgs(args) {
  return Boolean((args && args.override && args.override !== true) || (args && args['approve-id']) || (args && args.approveId) || (args && args['transfer-private-id']) || (args && args.transferPrivateId) || (args && args['reject-id']) || (args && args.rejectId) || (args && args['manual-confirm-id']) || (args && args.manualConfirmId));
}

function buildOverridePreview(input, args) {
  const actions = overrideActionMap(args);
  if (actions.size === 0) return [];
  const recordsById = new Map((input.records || []).map(record => [String(record.id), record]));
  const missing = [...actions.keys()].filter(id => !recordsById.has(id));
  if (missing.length) throw new Error(`Unknown override id(s): ${missing.join(',')}`);
  return [...actions.entries()].map(([id, newAction]) => {
    const record = recordsById.get(id);
    return {
      id,
      section: record.section || '',
      title: record.title || '',
      combo: [record.combo?.gameType, scopeLabel(record.scopeValue || record.raw?.scope || record.combo?.scopeValue) || record.combo?.scope, record.combo?.auditState].filter(Boolean).join(' / '),
      originalAction: record.suggestion?.action || '',
      newAction,
      originalIssue: record.suggestion?.issue || '',
      originalReason: record.suggestion?.reason || '',
    };
  });
}

function normalizeLearningText(s) {
  return stripHtml(s).toLowerCase().replace(/[\s\p{P}\p{S}]+/gu, '');
}

function shouldLearnOverride(originalAction, newAction) {
  return ['reject', 'manualConfirm', 'transferPrivateThenPass'].includes(originalAction)
    && ['autoPass', 'transferPrivateThenPass'].includes(newAction);
}

function buildOverrideLearnings(input, args, preview = null) {
  const rows = preview || buildOverridePreview(input, args || {});
  if (!rows.length) return null;
  const recordsById = new Map((input.records || []).map(record => [String(record.id), record]));
  const entries = [];
  for (const row of rows) {
    if (!shouldLearnOverride(row.originalAction, row.newAction)) continue;
    const record = recordsById.get(String(row.id)) || {};
    const contextText = [
      record.title,
      record.fields?.brief,
      record.fields?.detail,
      record.fields?.updateDesc,
      row.originalIssue,
      row.originalReason,
    ].filter(Boolean).map(stripHtml).join(' ');
    entries.push({
      id: row.id,
      section: row.section || record.section || '',
      title: row.title || record.title || '',
      combo: row.combo || '',
      originalAction: row.originalAction,
      newAction: row.newAction,
      originalIssue: row.originalIssue || '',
      originalReason: row.originalReason || '',
      textFingerprint: normalizeLearningText(contextText).slice(0, 180),
      learnedAt: new Date().toISOString(),
    });
  }
  if (!entries.length) return null;
  return {
    generatedAt: new Date().toISOString(),
    source: input.outDir || '',
    entries,
  };
}

function applyPriorOverrideLearnings(summary, learnings) {
  const entries = Array.isArray(learnings) ? learnings : (learnings?.entries || []);
  if (!entries.length) return summary;
  for (const record of summary.records || []) {
    const action = record.suggestion?.action || '';
    const issueKey = normalizeLearningText(record.suggestion?.issue || record.suggestion?.reason || '');
    const recordText = normalizeLearningText([record.title, record.fields?.brief, record.fields?.detail, record.fields?.updateDesc].filter(Boolean).join(' '));
    const match = entries.find(entry => {
      if (entry.section && record.section && entry.section !== record.section) return false;
      if (entry.originalAction && entry.originalAction !== action) return false;
      const learnedIssue = normalizeLearningText(entry.originalIssue || entry.originalReason || '');
      if (learnedIssue && issueKey && learnedIssue === issueKey) return true;
      const learnedTitle = normalizeLearningText(entry.title || '');
      if (learnedTitle && recordText && (recordText.includes(learnedTitle) || learnedTitle.includes(recordText.slice(0, Math.min(12, recordText.length))))) return true;
      return false;
    });
    if (!match) continue;
    record.reviewed_by_prior_override = true;
    record.priorOverride = {
      sourceId: match.id || '',
      originalAction: match.originalAction || '',
      newAction: match.newAction || '',
      originalIssue: match.originalIssue || '',
    };
    record.suggestion = {
      ...(record.suggestion || {}),
      reviewed_by_prior_override: true,
      priorOverrideAction: match.newAction || '',
    };
  }
  return summary;
}

function loadPriorOverrideLearnings(root = DEFAULT_ROOT) {
  const base = path.join(root || DEFAULT_ROOT, 'output', 'share-wa-review');
  if (!fs.existsSync(base)) return { entries: [] };
  const entries = [];
  const dirs = fs.readdirSync(base, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => path.join(base, dirent.name))
    .sort((a, b) => String(b).localeCompare(String(a)))
    .slice(0, 120);
  for (const dir of dirs) {
    const file = path.join(dir, 'override_learnings.json');
    if (!fs.existsSync(file)) continue;
    try {
      const data = readJsonNoBom(file);
      for (const entry of data.entries || []) entries.push({ ...entry, sourceFile: file });
    } catch (_) {}
  }
  return { entries };
}

function ensureImagesReviewed(input, args) {
  const count = Number(input.imageManifestCount || (Array.isArray(input.imageManifest) ? input.imageManifest.length : 0));
  const required = input.imageReview?.required || count > 0;
  const modelPassed = input.imageReview?.status === 'model_passed';
  const reviewed = isTruthyArg(args?.['images-reviewed']) || isTruthyArg(args?.imagesReviewed);
  if (required && !reviewed && !modelPassed) {
    throw new Error('Image review is required before execute. Inspect contact_sheet_visual.png, then rerun with --images-reviewed.');
  }
  if (required && reviewed) {
    input.imageReview = { ...(input.imageReview || buildImageReview(count)), status: 'reviewed' };
  }
}

function applyOverrides(input, args) {
  const next = JSON.parse(JSON.stringify(input));
  const { approveIds, transferPrivateIds, rejectIds, manualConfirmIds } = loadOverrideIds(args);
  for (const record of next.records || []) {
    if (approveIds.has(record.id)) {
      record.suggestion = { ...(record.suggestion || {}), action: 'autoPass', reason: '', issue: '用户确认该条目可通过', executable: true };
    }
    if (transferPrivateIds.has(record.id)) {
      record.suggestion = { ...(record.suggestion || {}), action: 'transferPrivateThenPass', reason: '', issue: '用户确认该条目转私密后通过', executable: true };
    }
    if (rejectIds.has(record.id)) {
      record.suggestion = { ...(record.suggestion || {}), action: 'reject', reason: record.section === 'wa' ? WA_REJECT_REASON : SHARE_REJECT_REASON, issue: '用户确认该条目不通过', executable: true };
    }
    if (manualConfirmIds.has(record.id)) {
      record.suggestion = { ...(record.suggestion || {}), action: 'manualConfirm', reason: '', issue: '用户确认保留人工确认', executable: false };
    }
  }
  return recalculateCounts(next);
}

function executableRecords(input) {
  const next = JSON.parse(JSON.stringify(input));
  const records = (next.records || []).filter(record => {
    const action = record.suggestion && record.suggestion.action;
    return record.suggestion && record.suggestion.executable !== false && action !== 'manualConfirm';
  });
  return recalculateCounts({ ...next, records, recordsCount: records.length, skippedManualConfirm: (next.records || []).length - records.length });
}

function prepareExecuteInput(input, args) {
  ensureImagesReviewed(input, args || {});
  const preview = buildOverridePreview(input, args || {});
  const next = applyOverrides(input, args || {});
  const inputPath = args && args.inputPath ? path.resolve(args.inputPath) : null;
  const outDir = next.outDir || (inputPath ? path.dirname(inputPath) : process.cwd());
  const hasOverrides = hasOverrideArgs(args || {});
  const outputPath = hasOverrides ? path.join(outDir, 'summary.execute.json') : (inputPath || path.join(outDir, 'summary.execute.json'));
  if (preview.length) writeJson(path.join(outDir, 'override_preview.json'), preview);
  const learnings = buildOverrideLearnings(input, args || {}, preview);
  if (learnings) writeJson(path.join(outDir, 'override_learnings.json'), learnings);
  if (hasOverrides) writeJson(outputPath, next);
  return { input: next, path: outputPath, outDir };
}

async function runReport(args) {
  const outDir = args.out ? path.resolve(args.out) : path.join(args.root || DEFAULT_ROOT, 'output', 'share-wa-review', stamp());
  ensureDir(outDir);
  const progress = (stage, data = {}) => console.error(`[share-wa-review] ${stage}${Object.keys(data).length ? ` ${JSON.stringify(data)}` : ''}`);
  progress('扫描');
  let scan = runPlaywrightFunction(buildScanFunction(), 'scan_review', outDir, undefined, { recoverAuth: true });
  if (isAuthFailureScan(scan)) {
    ensureAuthenticated(outDir);
    scan = runPlaywrightFunction(buildScanFunction(), 'scan_review', outDir, undefined, { recoverAuth: true });
  }
  writeJson(path.join(outDir, 'scan_raw.json'), scan);
  const summary = makeSummary(scan, outDir);
  applyPriorOverrideLearnings(summary, loadPriorOverrideLearnings(args.root || DEFAULT_ROOT));
  progress('下载图片', { records: summary.records.length });
  const imageManifest = await downloadImages(summary, outDir);
  summary.imageManifest = imageManifest;
  summary.imageManifestCount = imageManifest.length;
  summary.imageReview = buildImageReview(imageManifest.length);
  const modelReview = await reviewImagesWithModel(summary, imageManifest, outDir, {
    onProgress: event => {
      if (event.stage === 'image_model_resume') progress('审图resume', { resultCount: event.resultCount });
      if (event.stage === 'batch_review') progress('图册审核', { batches: event.batches, images: event.images });
      if (event.stage === 'single_review') progress('单图复核', { index: event.index, retry: Boolean(event.retry) });
    },
  });
  if (modelReview) applyImageModelReview(summary, modelReview);
  progress('写报告');
  writeJson(path.join(outDir, 'manual_confirm.json'), buildManualConfirmRows(summary));
  writeJson(path.join(outDir, 'summary.json'), summary);
  fs.writeFileSync(path.join(outDir, 'review_report.md'), renderMarkdown(summary), 'utf8');
  const artifacts = {
    summary: path.join(outDir, 'summary.json'),
    report: path.join(outDir, 'review_report.md'),
    manualConfirm: path.join(outDir, 'manual_confirm.json'),
    contactSheet: path.join(outDir, 'contact_sheet_visual.png'),
    imageReview: path.join(outDir, 'image_model_review.json'),
    imageReviewCalls: path.join(outDir, 'image_model_review_calls.json'),
  };
  console.log(JSON.stringify({ mode: 'report', outDir, scannedCombos: summary.scannedCombos, recordsCount: summary.recordsCount, errorsCount: summary.errorsCount, counts: summary.counts, imageManifestCount: summary.imageManifestCount, imageReview: summary.imageReview, artifacts }, null, 2));
  return summary;
}

function buildExecuteFunction(plan) {
  return async input => {
    const API_BASE = 'https://ui-cms-api.opd.netease.com';
    const post = async (path, body) => {
      const r = await fetch(API_BASE + path, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const text = await r.text(); let json; try { json = JSON.parse(text); } catch (e) { json = { text: text.slice(0, 500) }; }
      return { status: r.status, json, ok: r.status === 200 && json.code === 0 };
    };
    const get = async path => (await fetch(API_BASE + path, { credentials: 'include' })).json();
    const results = [];
    for (const r of input.records) {
      const action = r.suggestion && r.suggestion.action;
      if (!r.suggestion || r.suggestion.executable === false || action === 'manualConfirm') { results.push({ id: r.id, action, skipped: true, reason: 'manualConfirm or non-executable' }); continue; }
      if (action === 'autoPass') {
        const path = r.section === 'share' ? '/share-api/audit/pass' : '/wa-api/audit/pass';
        results.push({ id: r.id, section: r.section, action, result: await post(path, { sn: r.id }) });
      } else if (action === 'reject') {
        const path = r.section === 'share' ? '/share-api/audit/reject' : '/wa-api/audit/reject';
        results.push({ id: r.id, section: r.section, action, result: await post(path, { sn: r.id, reason: r.suggestion.reason }) });
      } else if (action === 'transferPrivateThenPass') {
        if (r.section === 'share') {
          const d = r.raw || {};
          const payload = { game_type: d.game_type, title: d.title, display_imgs: d.display_imgs, desc: d.desc, update_desc: d.update_desc, brief_desc: d.brief_desc, jump_room: d.jump_room, room_id: d.room_id || '', creation_statement: d.creation_statement, scope: 'private', share_code_life_type: d.share_code_life_type || 'forever', sn: r.id };
          Object.keys(payload).forEach(k => payload[k] === undefined && delete payload[k]);
          const modify = await post('/share-api/modify', payload);
          const pass = modify.ok ? await post('/share-api/audit/pass', { sn: r.id }) : null;
          results.push({ id: r.id, section: r.section, action, modify, pass });
        } else {
          const d = (await get('/wa-api/detail?sn=' + encodeURIComponent(r.id))).result || r.raw || {};
          const payload = { game_type: d.game_type, game_version: d.game_version, source: d.source, source_link: d.source_link || '', author_sn: d.author_sn, assign_user_sn: d.assign_user_sn, content: d.content, show_desc: d.show_desc, state: d.state, version: d.version, jump_room: d.jump_room, room_id: d.room_id || '', enable_aigpt: d.enable_aigpt, creation_statement: d.creation_statement, with_file: d.with_file, file_path: d.file_path, scope: 'private', share_code_life_type: d.share_code_life_type, cms_name: d.cms_name, cms_brief_desc: d.cms_brief_desc, cms_display_imgs: d.cms_display_imgs, cms_desc: d.cms_desc, cms_category_ids: d.cms_category_ids, sn: r.id };
          Object.keys(payload).forEach(k => payload[k] === undefined && delete payload[k]);
          const modify = await post('/wa-api/modify', payload);
          const pass = modify.ok ? await post('/wa-api/audit/pass', { sn: r.id }) : null;
          results.push({ id: r.id, section: r.section, action, modify, pass });
        }
      }
    }
    return { executedAt: new Date().toISOString(), results };
  };
}

function summarizeExecuteResult(result) {
  const results = result.results || [];
  const byAction = {};
  for (const item of results) byAction[item.action] = (byAction[item.action] || 0) + 1;
  return {
    total: results.length,
    byAction,
    skipped: results.filter(item => item.skipped).length,
    failed: results.filter(item => item.result?.ok === false || item.modify?.ok === false || item.pass?.ok === false).length,
  };
}

function runExecute(args) {
  if (!args.input) throw new Error('--input summary.json is required for execute mode');
  const input = readJsonNoBom(args.input);
  const prepared = prepareExecuteInput(input, { ...args, inputPath: args.input });
  const outDir = prepared.outDir;
  const result = runPlaywrightFunction(buildExecuteFunction(prepared.input), 'execute_review', outDir, prepared.input);
  writeJson(path.join(outDir, 'execute_result.json'), result);
  const executeSummary = summarizeExecuteResult(result);
  const artifacts = {
    input: prepared.path,
    result: path.join(outDir, 'execute_result.json'),
    overridePreview: path.join(outDir, 'override_preview.json'),
    overrideLearnings: path.join(outDir, 'override_learnings.json'),
  };
  const output = { mode: 'execute', outDir, input: prepared.path, counts: prepared.input.counts, results: executeSummary.total, skipped: executeSummary.skipped, failed: executeSummary.failed, byAction: executeSummary.byAction, artifacts };
  console.log(JSON.stringify(output, null, 2));
  return { ...output, result, executeSummary, prepared };
}

function runRescan(args) { return runReport({ ...args, out: args.out || path.join(args.root || DEFAULT_ROOT, 'output', 'share-wa-review', `${stamp()}-rescan`) }); }

function countByAction(records) {
  const counts = {};
  for (const record of records || []) {
    const action = record.suggestion?.action || 'unknown';
    counts[action] = (counts[action] || 0) + 1;
  }
  return counts;
}

function withoutOverrideArgs(args) {
  const next = { ...(args || {}) };
  for (const key of ['override', 'approve-id', 'approveId', 'transfer-private-id', 'transferPrivateId', 'reject-id', 'rejectId', 'manual-confirm-id', 'manualConfirmId']) {
    delete next[key];
  }
  return next;
}

async function runCycle(args, deps = {}) {
  if (!args.input) throw new Error('--input summary.json is required for cycle mode');
  const readFn = deps.readJson || readJsonNoBom;
  const writeFn = deps.writeJson || writeJson;
  const executeFn = deps.executeFn || (async executeArgs => runExecute(executeArgs));
  const rescanFn = deps.rescanFn || (async rescanArgs => runRescan(rescanArgs));
  let currentInputPath = path.resolve(args.input);
  let current = readFn(currentInputPath);
  const baseOutDir = current.outDir || path.dirname(currentInputPath);
  ensureDir(baseOutDir);
  const cyclePath = path.join(baseOutDir, 'cycle_summary.json');
  const maxRounds = clampInt(args['max-rounds'] || args.maxRounds, 8, 1, 30);
  const cycle = {
    mode: 'cycle',
    startedAt: new Date().toISOString(),
    input: currentInputPath,
    status: 'running',
    rounds: [],
    remainingCount: (current.records || []).length,
    cycleSummary: cyclePath,
  };

  for (let round = 1; round <= maxRounds; round++) {
    if (round > 1 || !hasOverrideArgs(args)) {
      const currentExecutable = executableRecords(current);
      const currentRemaining = (current.records || []).length;
      if (currentExecutable.records.length === 0) {
        cycle.status = currentRemaining > 0 ? 'manual_remaining' : 'cleared';
        cycle.remainingCount = currentRemaining;
        break;
      }
    }
    const roundArgs = { ...args, inputPath: currentInputPath };
    if (round > 1) {
      delete roundArgs.override;
      delete roundArgs['approve-id'];
      delete roundArgs.approveId;
      delete roundArgs['transfer-private-id'];
      delete roundArgs.transferPrivateId;
      delete roundArgs['reject-id'];
      delete roundArgs.rejectId;
      delete roundArgs['manual-confirm-id'];
      delete roundArgs.manualConfirmId;
    }
    const prepared = prepareExecuteInput(current, roundArgs);
    const executable = executableRecords(prepared.input);
    const totalRemaining = (prepared.input.records || []).length;
    if (executable.records.length === 0) {
      cycle.status = totalRemaining > 0 ? 'manual_remaining' : 'cleared';
      cycle.remainingCount = totalRemaining;
      break;
    }

    const roundOutDir = prepared.outDir || baseOutDir;
    ensureDir(roundOutDir);
    const roundInput = {
      ...prepared.input,
      records: executable.records,
      recordsCount: executable.records.length,
      counts: executable.counts,
      skippedManualConfirm: executable.skippedManualConfirm,
      outDir: roundOutDir,
    };
    const roundInputPath = path.join(roundOutDir, `cycle_round_${String(round).padStart(2, '0')}_execute.json`);
    writeFn(roundInputPath, roundInput);
    const executeOutput = await executeFn({ ...withoutOverrideArgs(args), input: roundInputPath, inputPath: roundInputPath }, roundInput);
    const executeSummary = executeOutput?.executeSummary || summarizeExecuteResult(executeOutput?.result || executeOutput || {});
    const roundInfo = {
      round,
      input: roundInputPath,
      outDir: roundOutDir,
      byAction: executeSummary.byAction || {},
      executed: executeSummary.total || executable.records.length,
      failed: executeSummary.failed || 0,
      skipped: executeSummary.skipped || 0,
      skippedManualConfirm: executable.skippedManualConfirm || 0,
    };
    cycle.rounds.push(roundInfo);
    if (roundInfo.failed > 0) {
      cycle.status = 'failed';
      cycle.remainingCount = totalRemaining;
      break;
    }

    const rescanOut = path.join(args.root || DEFAULT_ROOT, 'output', 'share-wa-review', `${stamp()}-cycle-${String(round).padStart(2, '0')}-rescan`);
    const rescan = await rescanFn({ ...withoutOverrideArgs(args), mode: 'rescan', out: rescanOut }, roundInfo);
    current = rescan?.summary || rescan;
    if (!current || !Array.isArray(current.records)) {
      cycle.status = 'failed';
      roundInfo.error = 'rescan did not return a summary';
      break;
    }
    currentInputPath = current.outDir ? path.join(current.outDir, 'summary.json') : currentInputPath;
    roundInfo.rescanOutDir = current.outDir || '';
    roundInfo.remainingCount = (current.records || []).length;
    roundInfo.rescanByAction = current.counts || countByAction(current.records || []);
    cycle.remainingCount = roundInfo.remainingCount;
  }

  if (cycle.status === 'running') cycle.status = 'max_rounds_reached';
  cycle.finishedAt = new Date().toISOString();
  writeFn(cyclePath, cycle);
  console.log(JSON.stringify(cycle, null, 2));
  return cycle;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.mode === 'report') return await runReport(args);
  if (args.mode === 'execute') return runExecute(args);
  if (args.mode === 'rescan') return await runRescan(args);
  if (args.mode === 'cycle') return await runCycle(args);
  throw new Error(`Unknown --mode ${args.mode}`);
}

if (require.main === module) {
  main().catch(e => { console.error(e.stack || e.message); process.exit(1); });
}

module.exports = {
  applyImageModelReview,
  applyPriorOverrideLearnings,
  applyOverrides,
  buildManualConfirmRows,
  buildExecuteFunction,
  executableRecords,
  prepareExecuteInput,
  readJsonNoBom,
  recalculateCounts,
  renderMarkdown,
  reviewImagesWithModel,
  runCycle,
  runPlaywrightFunction,
  summarizeExecuteResult,
  suggest,
  writePlaywrightFunction,
};


