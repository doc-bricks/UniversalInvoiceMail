import test from "node:test";
import assert from "node:assert/strict";
import { TRANSLATIONS, getTranslation, t } from "../app.js";

const REQUIRED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"];

test("TRANSLATIONS contains all 6 Tier-2 languages", () => {
  for (const lang of REQUIRED_LANGUAGES) {
    assert.ok(TRANSLATIONS[lang], `Language ${lang} missing in TRANSLATIONS`);
  }
});

test("100% key parity across all 6 languages without empty values", () => {
  const deKeys = Object.keys(TRANSLATIONS.de);
  assert.ok(deKeys.length >= 25, `Expected at least 25 keys, found ${deKeys.length}`);

  for (const lang of REQUIRED_LANGUAGES) {
    const keys = Object.keys(TRANSLATIONS[lang]);
    assert.deepEqual(
      keys.sort(),
      deKeys.sort(),
      `Keys in ${lang} do not match de keys exactly`
    );

    for (const key of deKeys) {
      const val = TRANSLATIONS[lang][key];
      assert.equal(typeof val, "string", `${lang}.${key} must be a string`);
      assert.ok(val.trim().length > 0, `${lang}.${key} must not be empty`);
    }
  }
});

test("t() interpolates parameters correctly across languages", () => {
  assert.equal(t("summary_invoices", { count: 5 }, "de"), "5 Rechnungen");
  assert.equal(t("summary_invoices", { count: 5 }, "en"), "5 Invoices");
  assert.equal(t("summary_invoices", { count: 5 }, "es"), "5 facturas");
  assert.equal(t("summary_invoices", { count: 5 }, "zh"), "5 张发票");
  assert.equal(t("summary_invoices", { count: 5 }, "ja"), "5 件の請求書");
  assert.equal(t("summary_invoices", { count: 5 }, "ru"), "5 счетов");
});
