#!/usr/bin/env node
/** Verify the Japanese overlay is complete and aligned with the Chinese atlas. */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const atlas = path.join(root, 'public/atlas');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const sourceRaw = fs.readFileSync(path.join(atlas, 'index.json'));
const sourceIndex = JSON.parse(sourceRaw);
const ja = read(path.join(atlas, 'ja/index.json'));
const errors = [];
const warnings = [];
const warn = message => warnings.push(message);
const fail = message => { if (errors.length < 100) errors.push(message); };
if (ja.sourceIndexSha256 !== createHash('sha256').update(sourceRaw).digest('hex')) fail('Japanese index was built from a different Chinese index.');
if (ja.chunk !== sourceIndex.chunk) fail('Japanese chunk size differs from the source.');
if (Object.keys(ja.words).length !== sourceIndex.count) fail('Japanese word count differs from the source.');
const seen = new Set();
let examples = 0;
let fields = 0;
const checkText = (source, target, label) => {
  fields++;
  if (typeof target !== 'string') return fail(`${label}: expected string`);
  if (source.trim() && !target.trim()) fail(`${label}: nonempty source became empty`);
  if (/ZXQTERM|QXZ|⟪\s*X\s*\d|⟦\s*\d+\s*⟧|<unk>|⁇/i.test(target)) fail(`${label}: untranslated placeholder or unknown token`);
  if (/[这们词语说]/u.test(target)) warn(`${label}: simplified Chinese character: ${target}`);
  if (/(.{2,8})\1{3,}/u.test(target)) warn(`${label}: repeated output sequence: ${target}`);
  if (/\.(?:ex\[|tip)/.test(label) && source.length > 10) {
    if (!/[\u3040-\u30ff]/u.test(target)) warn(`${label}: sentence without Japanese kana: ${target}`);
    if (source === target) warn(`${label}: sentence identical to Chinese source: ${target}`);
  }
};
for (let n = 0; n * sourceIndex.chunk < sourceIndex.count; n++) {
  const sourcePath = path.join(atlas, `entries/${n}.json`);
  const sourceRaw = fs.readFileSync(sourcePath);
  const source = JSON.parse(sourceRaw);
  if (ja.sourceChunksSha256?.[n] !== createHash("sha256").update(sourceRaw).digest("hex")) fail(`Chunk ${n}: source content changed after translation`);
  const target = read(path.join(atlas, `ja/entries/${n}.json`));
  if (!Array.isArray(target) || target.length !== source.length) { fail(`Chunk ${n}: length mismatch`); continue; }
  source.forEach((entry, i) => {
    const translated = target[i];
    if (translated.id !== entry.id || seen.has(translated.id)) fail(`Chunk ${n}/${i}: ID/order mismatch`);
    seen.add(translated.id);
    for (const [key, original] of [['senses', entry.senses.map(s => s.zh)], ['ex', entry.ex.map(x => x.zh)], ['col', entry.col]]) {
      if (!Array.isArray(translated[key]) || translated[key].length !== original.length) { fail(`${entry.id}.${key}: length mismatch`); continue; }
      original.forEach((text, j) => {
        const value = translated[key][j];
        checkText(text, value, `${entry.id}.${key}[${j}]`);
        if (key === 'col' && text.includes('｜') && text.split('｜')[0] !== value?.split('｜')[0]) fail(`${entry.id}.col[${j}]: English collocation changed`);
      });
    }
    for (const key of ['tip', 'note']) {
      const original = entry[key] || '';
      const localized = translated[key];
      checkText(original, localized, `${entry.id}.${key}`);
      for (const term of original.match(/\/[^/\n]+\/|[A-Za-z][A-Za-z0-9 /'’+()_.-]*/g) || []) {
        if (!localized?.includes(term.trim())) fail(`${entry.id}.${key}: English/IPA literal changed: ${term.trim()}`);
      }
    }
    for (const key of ['fam', 'syn', 'ant']) {
      const original = entry[key];
      const localized = translated[key];
      if (localized === undefined && !original.some(text => /[\u3400-\u9fff]/u.test(text))) continue;
      if (!Array.isArray(localized) || localized.length !== original.length) { fail(`${entry.id}.${key}: missing related-word translation`); continue; }
      original.forEach((text, j) => {
        checkText(text, localized[j], `${entry.id}.${key}[${j}]`);
        if (!/[\u3400-\u9fff]/u.test(text) && localized[j] !== text) fail(`${entry.id}.${key}[${j}]: English changed`);
      });
    }
    const expected = `${entry.senses[0].pos} ${translated.senses?.[0]}`.trim();
    if (ja.words[entry.id] !== expected) fail(`${entry.id}: index differs from first sense`);
    examples += translated.ex?.length || 0;
  });
}
if (seen.size !== sourceIndex.count) fail('Not all source IDs have a Japanese entry.');
if (examples !== sourceIndex.examples) fail('Example count differs from source.');
console.log(JSON.stringify({ words: seen.size, examples, checkedFields: fields, errors: errors.length, linguisticWarnings: warnings.length, reviewedEntries: ja.translation?.reviewedEntries || 0 }, null, 2));
if (warnings.length) console.warn(warnings.slice(0, 30).join('\n'));
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
