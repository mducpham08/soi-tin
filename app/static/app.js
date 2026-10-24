/* Soi Tin – giao diện. Không dùng thư viện ngoài.
   Mọi nội dung từ người dùng / model đều gắn bằng textContent, không dùng innerHTML. */
"use strict";

const $ = (sel) => document.querySelector(sel);
const LEVEL_WORD = { scam: "Lừa đảo", caution: "Cần cẩn thận", safe: "Có vẻ an toàn" };
const KIND_LABEL = {
  official: "Tên miền thật", gov: "Cơ quan nhà nước", edu: "Giáo dục", lookalike: "Tên miền nhái",
  shortener: "Link rút gọn", messaging: "Kênh nhắn tin", freemail: "Email miễn phí", unknown: "Chưa rõ",
};
const nf = (x, d = 0) => Number(x).toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d });

const store = {
  get(k) { try { return window.localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { window.localStorage.setItem(k, v); } catch { /* bỏ qua */ } },
};

let config = null;
let busy = false;

function el(tag, attrs = {}, text) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "className") n.className = v; else n.setAttribute(k, v === true ? "" : v);
  }
  if (text !== undefined) n.textContent = text;
  return n;
}

/* ------------------------------------------------------------ khởi động */

async function init() {
  const msg = $("#msg");
  msg.addEventListener("input", updateCount);
  msg.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); $("#check-form").requestSubmit(); }
  });
  $("#check-form").addEventListener("submit", onSubmit);
  $("#again").addEventListener("click", () => {
    msg.value = ""; updateCount(); $("#result").hidden = true; hideError();
    $("#check").scrollIntoView({ block: "start" }); msg.focus({ preventScroll: true });
  });
  $("#edit").addEventListener("click", () => { $("#check").scrollIntoView({ block: "start" }); msg.focus({ preventScroll: true }); });

  loadEval();
  try {
    const r = await fetch("/api/config");
    if (!r.ok) throw new Error(r.status);
    config = await r.json();
  } catch {
    showError("Không kết nối được tới server. Hãy kiểm tra server đã chạy chưa rồi tải lại trang.");
    return;
  }
  const z = document.documentElement.style;
  const safe = config.thresholds.safe * 100, scam = config.thresholds.scam * 100;
  z.setProperty("--z-safe", `${safe}fr`); z.setProperty("--z-caution", `${scam - safe}fr`); z.setProperty("--z-scam", `${100 - scam}fr`);
  $("#foot-prompt").textContent = config.prompt;
  if (config.mode === "fake") showBanner("Chế độ thử: kết quả lấy từ luật từ khóa, không gọi AI.");
  if (config.mode === "public" && config.limits) {
    showBanner(`Bản demo dùng Haiku 5.5, mỗi người kiểm tra được ${config.limits.per_ip} tin mỗi ngày.`);
  }
  renderModels();
  renderSamples();
  updateCount();
}

function showBanner(text) { const b = $("#mode-banner"); b.textContent = text; b.hidden = false; }

function updateCount() {
  const n = $("#msg").value.length;
  const max = config ? config.max_chars : 4000;
  const c = $("#count");
  c.textContent = `${nf(n)} / ${nf(max)}`;
  c.classList.toggle("over", n > max);
}

function renderModels() {
  const box = $("#models");
  const saved = store.get("soitin.model");
  const usable = config.models.filter((m) => m.available);
  const pick = (usable.find((m) => m.key === saved) || usable[0] || config.models[0]).key;
  for (const m of config.models) {
    const label = el("label", { className: "model-opt", title: m.available ? m.hint : m.reason });
    const input = el("input", { type: "radio", name: "model", value: m.key, disabled: !m.available });
    input.checked = m.key === pick;
    input.addEventListener("change", () => { store.set("soitin.model", m.key); updateHint(); });
    label.append(input, el("span", {}, m.label));
    box.append(label);
  }
  if (config.models.length < 2) box.hidden = true;
  updateHint();
}

function selectedModel() {
  const r = document.querySelector('input[name="model"]:checked');
  return r ? r.value : "haiku";
}

function updateHint() {
  const key = selectedModel();
  const m = config.models.find((x) => x.key === key);
  const off = config.models.filter((x) => !x.available).map((x) => `${x.label}: ${x.reason}`);
  $("#model-hint").textContent = [m ? `${m.label}: ${m.hint}` : "", ...off].filter(Boolean).join("  ");
}

function renderSamples() {
  const list = $("#samples-list");
  for (const s of config.samples) {
    const b = el("button", { type: "button", className: "sample" });
    b.append(el("span", { className: "sample-title" }, s.title), el("span", { className: "sample-text" }, s.text));
    b.addEventListener("click", () => {
      const msg = $("#msg"); msg.value = s.text; updateCount(); hideError();
      msg.focus(); msg.setSelectionRange(0, 0); msg.scrollTop = 0;
    });
    const li = el("li"); li.append(b); list.append(li);
  }
}

/* ------------------------------------------------------------ gửi kiểm tra */

function showError(text) { const e = $("#form-error"); e.textContent = text; e.hidden = false; }
function hideError() { $("#form-error").hidden = true; }

function setBusy(on) {
  busy = on;
  $("#composer-sheet").classList.toggle("is-busy", on);
  const b = $("#submit");
  b.disabled = on;
  b.textContent = on ? "Đang kiểm tra…" : "Kiểm tra tin";
}

async function onSubmit(e) {
  e.preventDefault();
  if (busy || !config) return;
  hideError();
  const text = $("#msg").value.trim();
  if (!text) { showError("Bạn chưa dán nội dung tin."); $("#msg").focus(); return; }
  if (text.length > config.max_chars) {
    showError(`Tin dài ${nf(text.length)} ký tự, quá giới hạn ${nf(config.max_chars)}. Hãy chỉ dán phần nội dung đáng ngờ.`);
    return;
  }
  setBusy(true);
  try {
    const r = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model: selectedModel() }),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) { showError(data.error || `Server báo lỗi ${r.status}. Hãy thử lại.`); return; }
    renderResult(data);
  } catch {
    showError("Mất kết nối tới server. Hãy kiểm tra mạng rồi thử lại.");
  } finally {
    setBusy(false);
  }
}

/* ------------------------------------------------------------ hiển thị kết quả */

function renderResult(r) {
  const groups = config.groups;
  const order = new Map(r.signals.map((s, i) => [s.id, i + 1]));
  const byId = new Map(r.signals.map((s) => [s.id, s]));

  // kết luận + thang mức nghi ngờ
  const v = $("#verdict");
  v.dataset.level = r.level;
  $("#verdict-word").textContent = LEVEL_WORD[r.level];
  $("#meter-pin").style.setProperty("--p", r.confidence);
  $("#meter").setAttribute("aria-label", `Mức nghi ngờ ${Math.round(r.confidence * 100)} trên 100`);
  $("#explanation").textContent = r.explanation;

  // tin có tô sáng
  const box = $("#annotated");
  box.replaceChildren();
  r.segments.forEach((seg, i) => {
    if (!seg.signals.length) { box.append(document.createTextNode(seg.text)); return; }
    const first = byId.get(seg.signals[0]);
    const prev = r.segments[i - 1], nxt = r.segments[i + 1];
    const cls = ["hl"];
    if (prev && prev.signals.length) cls.push("join-l");   // nối liền với đoạn tô trước, không bo góc ở giữa
    if (nxt && nxt.signals.length) cls.push("join-r");
    const span = el("span", {
      className: cls.join(" "), "data-group": first.group, "data-signals": seg.signals.join(" "),
      title: seg.signals.map((id) => byId.get(id).name).join(", "), tabindex: "0",
    }, seg.text);
    // đoạn thuộc nhiều nhóm dấu hiệu: thêm gạch chân màu của nhóm thứ hai
    const other = seg.signals.map((id) => byId.get(id).group).find((g) => g !== first.group);
    if (other) { span.classList.add("multi"); span.style.setProperty("--c2", `var(--hl-${other})`); }
    span.addEventListener("mouseenter", () => activate(seg.signals));
    span.addEventListener("mouseleave", () => activate([]));
    span.addEventListener("focus", () => activate(seg.signals));
    span.addEventListener("blur", () => activate([]));
    span.addEventListener("click", () => {
      const note = document.querySelector(`.note[data-signal="${seg.signals[0]}"]`);
      if (note) note.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
    box.append(span);
    const next = r.segments[i + 1];
    const ending = seg.signals.filter((id) => !(next && next.signals.includes(id)));
    if (ending.length) box.append(el("sup", { className: "ref", "aria-hidden": "true" }, ending.map((id) => order.get(id)).join(",")));
  });

  // chú thích màu
  const legend = $("#legend");
  legend.replaceChildren();
  const used = [...new Set(r.signals.map((s) => s.group))];
  for (const g of Object.keys(groups)) {
    if (!used.includes(g)) continue;
    const item = el("span", { className: "legend-item" });
    const sw = el("span", { className: "swatch" });
    sw.style.setProperty("--c", `var(--hl-${g})`);
    item.append(sw, document.createTextNode(groups[g]));
    legend.append(item);
  }
  legend.hidden = used.length === 0;

  // danh sách dấu hiệu
  const list = $("#notes-list");
  list.replaceChildren();
  const tpl = $("#note-tpl");
  r.signals.forEach((s, i) => {
    const li = tpl.content.firstElementChild.cloneNode(true);
    li.dataset.group = s.group;
    li.dataset.signal = s.id;
    li.querySelector(".note-ref").textContent = i + 1;
    li.querySelector(".note-name").textContent = s.name;
    li.querySelector(".note-why").textContent = s.why;
    const q = li.querySelector(".note-quote");
    if (s.evidence) {
      q.textContent = `“${s.evidence}”`;
      q.classList.toggle("not-found", !s.found);
      const why = !s.found ? "Không tìm thấy đoạn này trong tin."
        : s.exact === false ? "Model chép lại có sửa chữ, app tô chỗ gần giống nhất trong tin." : "";
      if (why) q.after(el("p", { className: "note-flag" }, why));
    } else q.remove();
    li.addEventListener("mouseenter", () => activate([s.id]));
    li.addEventListener("mouseleave", () => activate([]));
    list.append(li);
  });
  const head = r.level === "safe" ? "Điểm cần để ý" : "Dấu hiệu tìm thấy";
  $("#notes-title").textContent = r.signals.length ? `${head} (${r.signals.length})` : head;
  $("#notes-empty").hidden = r.signals.length > 0;

  // chữ bị biến dạng (luật của app)
  const obfList = $("#obf-list");
  obfList.replaceChildren();
  for (const o of r.obfuscation || []) {
    const li = el("li", { className: "link-row obf-row" });
    const samples = el("span", { className: "obf-samples" });
    o.samples.forEach((s) => samples.append(el("span", { className: "obf-sample" }, s)));
    li.append(el("span", { className: "link-host" }, o.label), samples, el("span", { className: "link-note" }, o.note));
    obfList.append(li);
  }
  $("#obf").hidden = !(r.obfuscation && r.obfuscation.length);

  // link và tên miền
  const links = $("#links-list");
  links.replaceChildren();
  for (const l of r.links) {
    const li = el("li", { className: "link-row" });
    li.append(el("span", { className: "link-host" }, l.host),
      el("span", { className: "badge", "data-kind": l.kind }, KIND_LABEL[l.kind] || l.kind),
      el("span", { className: "link-note" }, l.note));
    links.append(li);
  }
  $("#links").hidden = r.links.length === 0;

  // thông tin lượt chạy
  const meta = $("#meta");
  meta.replaceChildren();
  const m = r.meta;
  const modelLabel = (config.models.find((x) => x.key === m.model) || {}).label || m.model;
  const cost = !(m.cost_usd > 0) ? "Miễn phí"
    : m.cost_usd < 0.0001 ? "< 0,0001 USD" : `≈ ${nf(m.cost_usd, 4)} USD`;
  for (const [k, val] of [["Model", modelLabel], ["Thời gian", `${nf(m.latency_s, 1)} giây`],
                          ["Chi phí lượt này", cost], ["Prompt", m.prompt]]) {
    const d = el("div"); d.append(el("dt", {}, k), el("dd", {}, val)); meta.append(d);
  }
  const notes = $("#result-notes");
  notes.textContent = (r.notes || []).join(" ");
  notes.hidden = !(r.notes && r.notes.length);

  const res = $("#result");
  res.hidden = false;
  res.scrollIntoView({ block: "start" });
  res.focus({ preventScroll: true });
}

function activate(ids) {
  document.querySelectorAll(".hl").forEach((n) => {
    const s = n.dataset.signals.split(" ");
    n.classList.toggle("is-active", ids.some((id) => s.includes(id)));
  });
  document.querySelectorAll(".note").forEach((n) => n.classList.toggle("is-active", ids.includes(n.dataset.signal)));
}

/* ------------------------------------------------------------ bảng độ chính xác */

async function loadEval() {
  let data;
  try { data = await (await fetch("/static/eval.json")).json(); } catch { return; }
  const body = $("#eval-table tbody");
  for (const row of data.rows) {
    const tr = el("tr", { className: row.baseline ? "is-baseline" : undefined });
    const th = el("th", { scope: "row" }, row.name);
    th.append(el("span", { className: "sys-sub" }, row.sub));
    const f1 = el("td");
    const wrap = el("div", { className: "f1" });
    const bar = el("span", { className: "f1-bar" });
    const fill = el("span"); fill.style.setProperty("--v", row.f1);
    bar.append(fill);
    wrap.append(el("strong", {}, nf(row.f1, 1)), bar);
    f1.append(wrap);
    tr.append(th, f1,
      el("td", {}, `${row.tp} / ${row.n_scam} tin`),
      el("td", {}, `${row.fp} / ${row.n_legit} tin`),
      el("td", {}, nf(row.signal_f1, 1)),
      el("td", {}, row.cost_1000 > 0 ? `${nf(row.cost_1000, 2)} USD` : "Miễn phí"),
      el("td", {}, row.sec > 0 ? `${nf(row.sec, 1)} giây` : "Tức thì"));
    body.append(tr);
  }
}

init();
