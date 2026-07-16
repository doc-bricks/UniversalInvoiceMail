import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  ALLOWED_COMPANION_FIELDS,
  BUNDLE_SCHEMA,
  buildChangeBundle,
  changedInvoices,
  createEditState,
  filterInvoices,
  loadPersistedBundle,
  normalizeAmount,
  normalizeBundle,
  persistBundle,
  summarizeBundle,
  updateEditState,
} from "../library.js";

function sampleBundle() {
  return {
    schema: BUNDLE_SCHEMA,
    created_at: "2026-07-12T10:00:00+02:00",
    source: {
      app: "UniversalInvoiceMail",
      version: "2.3.0",
      platform: "windows",
    },
    export_options: {
      include_profiles: true,
      include_file_references: true,
      include_mail_bodies: false,
      include_attachments: false,
    },
    profiles: [{ id: "p1", name: "Amazon" }],
    invoices: [
      {
        id: "inv-1",
        profile_name: "Amazon",
        date: "2026-07-01",
        sender: "billing@example.test",
        subject: "Rechnung 123",
        filename: "rechnung-123.pdf",
        amount: null,
        currency: "EUR",
        review_status: "unchecked",
        notes: "",
        datev_status: "missing_amount",
        files: [{ filename: "rechnung-123.pdf", sha256: "abc", size_bytes: 42 }],
        local_hash: "abc",
        mail_reference: { message_id_hash: "sha256:redacted-ref" },
      },
      {
        id: "inv-2",
        profile_name: "Telekom",
        date: "2026-07-02",
        sender: "rechnung@example.test",
        subject: "Monatsrechnung",
        filename: "telekom.pdf",
        amount: 19.99,
        currency: "EUR",
        review_status: "checked",
        notes: "ok",
        datev_status: "ready",
        files: [{ filename: "telekom.pdf", sha256: "def", size_bytes: 48 }],
        local_hash: "def",
      },
    ],
    datev: { berater_nr: "100000", mandant_nr: "200000" },
    companion_changes: {
      mode: "none",
      allowed_fields: ALLOWED_COMPANION_FIELDS,
    },
  };
}

test("normalizes bundle and summarizes invoice state", () => {
  const bundle = normalizeBundle(sampleBundle());
  const summary = summarizeBundle(bundle);

  assert.equal(bundle.invoices[0].amount, null);
  assert.equal(summary.invoiceCount, 2);
  assert.equal(summary.missingAmount, 1);
  assert.equal(summary.readyForDatev, 1);
  assert.equal(summary.statusCounts.checked, 1);
});

test("filters invoices by profile, status and text query", () => {
  const bundle = normalizeBundle(sampleBundle());

  assert.equal(filterInvoices(bundle.invoices, { profile: "Amazon" }).length, 1);
  assert.equal(filterInvoices(bundle.invoices, { reviewStatus: "checked" }).length, 1);
  assert.equal(filterInvoices(bundle.invoices, { query: "monats" })[0].id, "inv-2");
});

test("builds minimal companion change bundle with only allowed fields", () => {
  const bundle = normalizeBundle(sampleBundle());
  let editState = createEditState(bundle.invoices);
  editState = updateEditState(editState, "inv-1", "amount", "12,50");
  editState = updateEditState(editState, "inv-1", "review_status", "ready");
  editState = updateEditState(editState, "inv-1", "notes", "Vom Tablet geprüft");

  assert.equal(changedInvoices(bundle, editState).length, 1);
  const changeBundle = buildChangeBundle(bundle, editState, new Date("2026-07-12T12:00:00Z"));

  assert.equal(changeBundle.schema, BUNDLE_SCHEMA);
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
  assert.equal(JSON.stringify(changeBundle).includes("message_id_hash"), false);
  assert.equal(JSON.stringify(changeBundle).includes("billing@example.test"), false);
  assert.equal(changeBundle.invoices[0].amount, 12.5);
});

test("rejects invalid companion fields and amounts", () => {
  const bundle = normalizeBundle(sampleBundle());
  const editState = createEditState(bundle.invoices);

  assert.throws(() => updateEditState(editState, "inv-1", "sender", "attacker"));
  assert.throws(() => normalizeAmount("abc"));
});

test("persists the last redacted bundle in browser storage", () => {
  const store = new Map();
  const storage = {
    setItem: (key, value) => store.set(key, value),
    getItem: (key) => store.get(key) || null,
    removeItem: (key) => store.delete(key),
  };

  persistBundle(storage, sampleBundle());
  const restored = loadPersistedBundle(storage);

  assert.equal(restored.schema, BUNDLE_SCHEMA);
  assert.equal(restored.invoices.length, 2);
});

test("static PWA shell references only local assets", async () => {
  const [indexHtml, manifest, serviceWorker] = await Promise.all([
    readFile(new URL("../index.html", import.meta.url), "utf8"),
    readFile(new URL("../manifest.webmanifest", import.meta.url), "utf8"),
    readFile(new URL("../sw.js", import.meta.url), "utf8"),
  ]);

  assert.match(indexHtml, /type="module" src="\.\/app\.js"/);
  assert.match(indexHtml, /rel="manifest" href="\.\/manifest\.webmanifest"/);
  assert.equal(JSON.parse(manifest).display, "standalone");
  assert.match(serviceWorker, /CACHE_NAME = "universalinvoicemail-companion-v2"/);
});
