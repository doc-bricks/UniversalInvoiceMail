import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import test from "node:test";
import {
  ALLOWED_COMPANION_FIELDS,
  BUNDLE_SCHEMA,
  buildChangeBundle,
  createEditState,
  filterInvoices,
  normalizeBundle,
  summarizeBundle,
  updateEditState,
} from "../library.js";

const companionRoot = new URL("../", import.meta.url);

async function readText(relativePath) {
  return readFile(new URL(relativePath, companionRoot), "utf8");
}

async function readFixture() {
  return JSON.parse(await readFile(new URL("./mobile_smoke_bundle.json", import.meta.url), "utf8"));
}

test("mobile fixture is a real redacted invoice bundle", async () => {
  const rawBundle = await readFixture();
  const bundle = normalizeBundle(rawBundle);
  const summary = summarizeBundle(bundle);
  const serialized = JSON.stringify(rawBundle).toLowerCase();

  assert.equal(bundle.schema, BUNDLE_SCHEMA);
  assert.equal(summary.invoiceCount, 2);
  assert.equal(summary.profileCount, 2);
  assert.equal(summary.missingAmount, 1);
  assert.equal(summary.readyForDatev, 1);
  assert.equal(rawBundle.export_options.include_mail_bodies, false);
  assert.equal(rawBundle.export_options.include_attachments, false);
  assert.equal(serialized.includes("password"), false);
  assert.equal(serialized.includes("token"), false);
  assert.equal(serialized.includes("credentials.json"), false);
  assert.equal(serialized.includes("client_secret"), false);
});

test("android and ios pwa metadata stays installable from the companion root", async () => {
  const [indexHtml, manifestRaw, serviceWorker] = await Promise.all([
    readText("./index.html"),
    readText("./manifest.webmanifest"),
    readText("./sw.js"),
  ]);
  const manifest = JSON.parse(manifestRaw);
  const iconPaths = manifest.icons.map((icon) => icon.src);

  assert.match(indexHtml, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
  assert.match(indexHtml, /<link rel="apple-touch-icon" href="\.\/icons\/apple-touch-icon-180\.png">/);
  assert.equal(manifest.display, "standalone");
  assert.equal(manifest.start_url, "./index.html");
  assert.equal(manifest.scope, "./");
  assert.ok(iconPaths.includes("./icons/Icon-192.png"));
  assert.ok(iconPaths.includes("./icons/Icon-512.png"));
  assert.ok(manifest.icons.some((icon) => icon.purpose === "maskable"));

  for (const iconPath of iconPaths.concat(["./icons/apple-touch-icon-180.png", "./icons/favicon.png"])) {
    assert.ok(iconPath.startsWith("./icons/"), `icon must stay inside web_companion/: ${iconPath}`);
    const iconStat = await stat(new URL(iconPath, companionRoot));
    assert.ok(iconStat.size > 1000, `icon has content: ${iconPath}`);
    assert.match(serviceWorker, new RegExp(iconPath.replaceAll(".", "\\.")));
  }
});

test("mobile pwa review flow exports only allowed companion fields", async () => {
  const bundle = normalizeBundle(await readFixture());
  let editState = createEditState(bundle.invoices);
  editState = updateEditState(editState, "sha256:mobile-smoke-amazon-202607", "amount", "44,90");
  editState = updateEditState(editState, "sha256:mobile-smoke-amazon-202607", "review_status", "ready");
  editState = updateEditState(editState, "sha256:mobile-smoke-amazon-202607", "notes", "Auf dem Tablet geprüft");
  const changeBundle = buildChangeBundle(bundle, editState, new Date("2026-07-16T20:00:00Z"));

  assert.deepEqual(changeBundle.companion_changes.allowed_fields, ALLOWED_COMPANION_FIELDS);
  assert.equal(changeBundle.invoices.length, 1);
  assert.deepEqual(Object.keys(changeBundle.invoices[0]).sort(), [
    "amount",
    "files",
    "id",
    "local_hash",
    "notes",
    "review_status",
  ]);
  assert.equal(changeBundle.invoices[0].amount, 44.9);
  assert.equal(JSON.stringify(changeBundle).includes("billing@example.invalid"), false);
  assert.equal(JSON.stringify(changeBundle).includes("message_id_hash"), false);
});

test("mobile pwa filters support profile, status and text review", async () => {
  const bundle = normalizeBundle(await readFixture());

  assert.equal(filterInvoices(bundle.invoices, { profile: "Amazon" }).length, 1);
  assert.equal(filterInvoices(bundle.invoices, { reviewStatus: "checked" }).length, 1);
  assert.equal(filterInvoices(bundle.invoices, { query: "juli" })[0].id, "sha256:mobile-smoke-phone-202607");
});
