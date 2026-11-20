// Checks the phone page translation table against the strings the page can show.
// English text is the key, so English output (and the other page tests) stay unchanged.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "../services/phone_web/index.html"), "utf8");
const scripts = html.split("<script").slice(1).map(part => part.slice(part.indexOf(">") + 1).split("</script>")[0]);
const code = scripts.join("\n");
const table = JSON.parse(/const UI_TEXT=(\[.*?\]);\n/s.exec(code)[1]);
const translated = new Map(table.map(([english, russian, german]) => [english, {russian, german}]));
const unescape = text => text.replace(/\\(["\\])/g, "$1");
const keys = new Set();
for (const match of code.matchAll(/\bT\("((?:[^"\\]|\\.)*)"/g)) keys.add(unescape(match[1]));
const markup = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "");
const entities = text => text.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
for (const match of markup.matchAll(/<\w+[^>]*\sdata-t[\s>][^<]*/g)) {
  const text = entities(match[0].slice(match[0].indexOf(">") + 1).trim());
  if (text) keys.add(text);
}
for (const match of markup.matchAll(/<\w+[^>]*\sdata-ta\b[^>]*>/g)) {
  const label = /aria-label="([^"]*)"/.exec(match[0]);
  assert(label, "data-ta element without aria-label: " + match[0]);
  keys.add(label[1]);
}
// Machine values shown through a lookup table rather than a literal call.
for (const key of ["Playing", "Paused", "Closed", "Muted", "Waiting", "File error", "Stopped", "Not playing", "Sound is off", "Starting…"]) keys.add(key);
const sameInAllLanguages = new Set(["Wi-Fi", "Bluetooth", "Direct · 192.168.4.1"]);
const missing = [...keys].filter(key => !translated.has(key) && !sameInAllLanguages.has(key));
assert.deepEqual(missing, [], "Strings without RU/DE translation");
const placeholders = text => (text.match(/\{\w+\}/g) || []).sort().join();
for (const [english, {russian, german}] of translated) {
  assert(russian && german, "Empty translation for " + english);
  assert.equal(placeholders(russian), placeholders(english), "RU placeholders differ: " + english);
  assert.equal(placeholders(german), placeholders(english), "DE placeholders differ: " + english);
  assert(!/[<>]/.test(russian + german), "Translations must be plain text: " + english);
}
const months = table.find(([english]) => english.startsWith("January "));
assert(months && months.every(list => list.split(" ").length === 12), "Month list must contain 12 names");
// Remote names are always inserted with textContent; no innerHTML except a fixed icon.
assert.equal((code.match(/innerHTML/g) || []).length, 1);
assert.match(code, /icon\.innerHTML=`<use href="\$\{playing\?"#i-pause":"#i-play"\}"\/>`/);
console.log(`phone_ui_text_test: PASS (${keys.size} strings, ${table.length} translations)`);
