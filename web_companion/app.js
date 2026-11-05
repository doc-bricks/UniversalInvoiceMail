import {
  REVIEW_STATUSES,
  buildChangeBundle,
  changedInvoices,
  clearPersistedBundle,
  createEditState,
  filterInvoices,
  formatCurrency,
  listProfiles,
  loadPersistedBundle,
  normalizeBundle,
  persistBundle,
  summarizeBundle,
  updateEditState,
} from "./library.js";

export const TRANSLATIONS = {
  de: {
    app_title_page: "UniversalInvoiceMail Companion",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "Rechnungsprüfung",
    actions_aria: "Bundle-Aktionen",
    btn_open_bundle: "Bundle öffnen",
    btn_restore: "Letzten Stand",
    btn_clear: "Lokalen Stand löschen",
    btn_export_changes: "Änderungen exportieren",
    filter_aria: "Filter",
    lbl_search: "Suche",
    lbl_profile: "Profil",
    lbl_status: "Status",
    opt_all_profiles: "Alle Profile",
    opt_all_statuses: "Alle Status",
    invoices_aria: "Rechnungen",
    detail_empty_bundle: "Kein Bundle geladen",
    lbl_amount: "Betrag",
    lbl_review_status: "Prüfstatus",
    lbl_notes: "Notiz",
    lbl_file_hash: "Datei-Hash",
    summary_invoices: "{count} Rechnungen",
    summary_missing_amount: "{count} ohne Betrag",
    summary_ready_datev: "{count} DATEV-bereit",
    summary_changes: "{count} Änderungen",
    toast_bundle_loaded: "Bundle geladen",
    toast_restored: "Lokales Bundle wiederhergestellt",
    toast_no_restored: "Kein lokales Bundle gespeichert",
    toast_cleared: "Lokaler Browser-Stand gelöscht",
    toast_exported: "{count} Änderungen exportiert",
    badge_changed: "geändert",
    no_hash: "Kein Hash im Bundle",
    no_profile: "Ohne Profil",
    status_unreviewed: "Ungeprüft",
    status_reviewed: "Geprüft",
    status_needs_clarification: "Klärung nötig",
    status_rejected: "Verworfen",
  },
  en: {
    app_title_page: "UniversalInvoiceMail Companion",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "Invoice Review",
    actions_aria: "Bundle Actions",
    btn_open_bundle: "Open Bundle",
    btn_restore: "Restore Last",
    btn_clear: "Clear Local State",
    btn_export_changes: "Export Changes",
    filter_aria: "Filters",
    lbl_search: "Search",
    lbl_profile: "Profile",
    lbl_status: "Status",
    opt_all_profiles: "All Profiles",
    opt_all_statuses: "All Statuses",
    invoices_aria: "Invoices",
    detail_empty_bundle: "No bundle loaded",
    lbl_amount: "Amount",
    lbl_review_status: "Review Status",
    lbl_notes: "Notes",
    lbl_file_hash: "File Hash",
    summary_invoices: "{count} Invoices",
    summary_missing_amount: "{count} missing amount",
    summary_ready_datev: "{count} DATEV ready",
    summary_changes: "{count} changes",
    toast_bundle_loaded: "Bundle loaded",
    toast_restored: "Local bundle restored",
    toast_no_restored: "No local bundle saved",
    toast_cleared: "Local browser state cleared",
    toast_exported: "{count} changes exported",
    badge_changed: "changed",
    no_hash: "No hash in bundle",
    no_profile: "No Profile",
    status_unreviewed: "Unreviewed",
    status_reviewed: "Reviewed",
    status_needs_clarification: "Needs Clarification",
    status_rejected: "Rejected",
  },
  es: {
    app_title_page: "UniversalInvoiceMail Companion",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "Revisión de facturas",
    actions_aria: "Acciones del lote",
    btn_open_bundle: "Abrir lote",
    btn_restore: "Restaurar último",
    btn_clear: "Borrar estado local",
    btn_export_changes: "Exportar cambios",
    filter_aria: "Filtros",
    lbl_search: "Buscar",
    lbl_profile: "Perfil",
    lbl_status: "Estado",
    opt_all_profiles: "Todos los perfiles",
    opt_all_statuses: "Todos los estados",
    invoices_aria: "Facturas",
    detail_empty_bundle: "Ningún lote cargado",
    lbl_amount: "Importe",
    lbl_review_status: "Estado de revisión",
    lbl_notes: "Notas",
    lbl_file_hash: "Hash de archivo",
    summary_invoices: "{count} facturas",
    summary_missing_amount: "{count} sin importe",
    summary_ready_datev: "{count} listo para DATEV",
    summary_changes: "{count} cambios",
    toast_bundle_loaded: "Lote cargado",
    toast_restored: "Lote local restaurado",
    toast_no_restored: "No hay lote local guardado",
    toast_cleared: "Estado local del navegador borrado",
    toast_exported: "{count} cambios exportados",
    badge_changed: "modificado",
    no_hash: "Sin hash en el lote",
    no_profile: "Sin perfil",
    status_unreviewed: "Sin revisar",
    status_reviewed: "Revisado",
    status_needs_clarification: "Requiere aclaración",
    status_rejected: "Rechazado",
  },
  zh: {
    app_title_page: "UniversalInvoiceMail 伴侣",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "发票审核",
    actions_aria: "批次操作",
    btn_open_bundle: "打开批次",
    btn_restore: "恢复最后状态",
    btn_clear: "清除本地状态",
    btn_export_changes: "导出更改",
    filter_aria: "筛选",
    lbl_search: "搜索",
    lbl_profile: "配置文件",
    lbl_status: "状态",
    opt_all_profiles: "所有配置文件",
    opt_all_statuses: "所有状态",
    invoices_aria: "发票列表",
    detail_empty_bundle: "未加载批次",
    lbl_amount: "金额",
    lbl_review_status: "审核状态",
    lbl_notes: "备注",
    lbl_file_hash: "文件哈希",
    summary_invoices: "{count} 张发票",
    summary_missing_amount: "{count} 缺少金额",
    summary_ready_datev: "{count} 已就绪DATEV",
    summary_changes: "{count} 处更改",
    toast_bundle_loaded: "批次已加载",
    toast_restored: "已恢复本地批次",
    toast_no_restored: "没有保存的本地批次",
    toast_cleared: "已清除浏览器本地状态",
    toast_exported: "已导出 {count} 处更改",
    badge_changed: "已修改",
    no_hash: "批次中无哈希",
    no_profile: "无配置文件",
    status_unreviewed: "未审核",
    status_reviewed: "已审核",
    status_needs_clarification: "需要明确",
    status_rejected: "已驳回",
  },
  ja: {
    app_title_page: "UniversalInvoiceMail コンパニオン",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "請求書レビュー",
    actions_aria: "バッチ操作",
    btn_open_bundle: "バッチを開く",
    btn_restore: "前回状態を復元",
    btn_clear: "ローカル状態をクリア",
    btn_export_changes: "変更をエクスポート",
    filter_aria: "フィルター",
    lbl_search: "検索",
    lbl_profile: "プロファイル",
    lbl_status: "ステータス",
    opt_all_profiles: "すべてのプロファイル",
    opt_all_statuses: "すべてのステータス",
    invoices_aria: "請求書一覧",
    detail_empty_bundle: "バッチが読み込まれていません",
    lbl_amount: "金額",
    lbl_review_status: "確認ステータス",
    lbl_notes: "メモ",
    lbl_file_hash: "ファイルハッシュ",
    summary_invoices: "{count} 件の請求書",
    summary_missing_amount: "{count} 件金額なし",
    summary_ready_datev: "{count} 件DATEV準備完了",
    summary_changes: "{count} 件の変更",
    toast_bundle_loaded: "バッチを読み込みました",
    toast_restored: "ローカルバッチを復元しました",
    toast_no_restored: "保存されたローカルバッチはありません",
    toast_cleared: "ブラウザのローカル状態をクリアしました",
    toast_exported: "{count} 件の変更をエクスポートしました",
    badge_changed: "変更あり",
    no_hash: "バッチにハッシュがありません",
    no_profile: "プロファイルなし",
    status_unreviewed: "未確認",
    status_reviewed: "確認済み",
    status_needs_clarification: "要確認",
    status_rejected: "破棄",
  },
  ru: {
    app_title_page: "UniversalInvoiceMail Компаньон",
    app_eyebrow: "UniversalInvoiceMail",
    app_title: "Проверка счетов",
    actions_aria: "Действия с пакетом",
    btn_open_bundle: "Открыть пакет",
    btn_restore: "Восстановить",
    btn_clear: "Очистить локально",
    btn_export_changes: "Экспорт изменений",
    filter_aria: "Фильтры",
    lbl_search: "Поиск",
    lbl_profile: "Профиль",
    lbl_status: "Статус",
    opt_all_profiles: "Все профили",
    opt_all_statuses: "Все статусы",
    invoices_aria: "Счета",
    detail_empty_bundle: "Пакет не загружен",
    lbl_amount: "Сумма",
    lbl_review_status: "Статус проверки",
    lbl_notes: "Заметка",
    lbl_file_hash: "Хэш файла",
    summary_invoices: "{count} счетов",
    summary_missing_amount: "{count} без суммы",
    summary_ready_datev: "{count} готово для DATEV",
    summary_changes: "{count} изменений",
    toast_bundle_loaded: "Пакет загружен",
    toast_restored: "Локальный пакет восстановлен",
    toast_no_restored: "Нет сохраненного локального пакета",
    toast_cleared: "Локальное состояние браузера очищено",
    toast_exported: "Экспортировано {count} изменений",
    badge_changed: "изменено",
    no_hash: "Нет хэша в пакете",
    no_profile: "Без профиля",
    status_unreviewed: "Не проверено",
    status_reviewed: "Проверено",
    status_needs_clarification: "Требует уточнения",
    status_rejected: "Отклонено",
  },
};

let currentLang = "de";

export function getTranslation(key, lang = currentLang) {
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.de;
  return dict[key] || TRANSLATIONS.de[key] || key;
}

export function t(key, params = {}, lang = currentLang) {
  let str = getTranslation(key, lang);
  for (const [k, v] of Object.entries(params)) {
    str = str.replaceAll(`{${k}}`, String(v));
  }
  return str;
}

const state = {
  bundle: null,
  invoices: [],
  filtered: [],
  editState: {},
  selectedId: "",
  filters: {
    query: "",
    profile: "",
    reviewStatus: "",
  },
};

const hasDoc = typeof document !== "undefined";

const els = hasDoc ? {
  langSelect: document.querySelector("#lang-select"),
  fileInput: document.querySelector("#bundle-file"),
  restoreButton: document.querySelector("#restore-bundle"),
  clearButton: document.querySelector("#clear-bundle"),
  exportButton: document.querySelector("#export-changes"),
  queryInput: document.querySelector("#query"),
  profileSelect: document.querySelector("#profile-filter"),
  statusSelect: document.querySelector("#status-filter"),
  summary: document.querySelector("#summary"),
  invoiceList: document.querySelector("#invoice-list"),
  detailEmpty: document.querySelector("#detail-empty"),
  detailForm: document.querySelector("#detail-form"),
  detailTitle: document.querySelector("#detail-title"),
  detailMeta: document.querySelector("#detail-meta"),
  amountInput: document.querySelector("#amount"),
  statusInput: document.querySelector("#review-status"),
  notesInput: document.querySelector("#notes"),
  fileHash: document.querySelector("#file-hash"),
  toast: document.querySelector("#toast"),
} : {};

function toast(message) {
  if (!els.toast) return;
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 2800);
}

export function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) {
    lang = "de";
  }
  currentLang = lang;
  if (els.langSelect) {
    els.langSelect.value = lang;
  }
  try {
    window.localStorage?.setItem("uim_lang", lang);
  } catch {}

  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (key) {
      el.textContent = getTranslation(key, lang);
    }
  });

  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const key = el.dataset.i18nAria;
    if (key) {
      el.setAttribute("aria-label", getTranslation(key, lang));
    }
  });

  renderStatusInputOptions();
  renderFilters();
  render();
}

function renderStatusInputOptions() {
  if (!els.statusInput) return;
  const currentVal = els.statusInput.value;
  els.statusInput.innerHTML = "";
  for (const status of REVIEW_STATUSES) {
    const option = document.createElement("option");
    option.value = status.value;
    option.textContent = statusLabel(status.value);
    els.statusInput.append(option);
  }
  if (currentVal) {
    els.statusInput.value = currentVal;
  }
}

function setBundle(bundle, { persist = true } = {}) {
  const normalized = normalizeBundle(bundle);
  state.bundle = normalized;
  state.invoices = normalized.invoices;
  state.editState = createEditState(normalized.invoices);
  state.selectedId = normalized.invoices[0]?.id || "";
  if (persist) {
    persistBundle(window.localStorage, normalized);
  }
  renderFilters();
  render();
}

function renderFilters() {
  if (!els.profileSelect || !els.statusSelect) return;
  const profiles = listProfiles(state.invoices);
  const currentProfile = els.profileSelect.value;
  els.profileSelect.innerHTML = [
    `<option value="">${escapeHtml(t("opt_all_profiles"))}</option>`,
    ...profiles.map((profile) => `<option value="${escapeHtml(profile)}">${escapeHtml(profile)}</option>`),
  ].join("");
  els.profileSelect.value = currentProfile || "";

  const currentStatus = els.statusSelect.value;
  els.statusSelect.innerHTML = [
    `<option value="">${escapeHtml(t("opt_all_statuses"))}</option>`,
    ...REVIEW_STATUSES.map((status) => (
      `<option value="${status.value}">${escapeHtml(statusLabel(status.value))}</option>`
    )),
  ].join("");
  els.statusSelect.value = currentStatus || "";
}

function renderSummary() {
  if (!els.summary) return;
  if (!state.bundle) {
    els.summary.innerHTML = `<span>${escapeHtml(t("detail_empty_bundle"))}</span>`;
    return;
  }
  const summary = summarizeBundle(state.bundle);
  const changes = changedInvoices(state.bundle, state.editState).length;
  els.summary.innerHTML = [
    `<span><strong>${summary.invoiceCount}</strong> ${escapeHtml(t("summary_invoices", { count: "" }).trim())}</span>`,
    `<span><strong>${summary.missingAmount}</strong> ${escapeHtml(t("summary_missing_amount", { count: "" }).trim())}</span>`,
    `<span><strong>${summary.readyForDatev}</strong> ${escapeHtml(t("summary_ready_datev", { count: "" }).trim())}</span>`,
    `<span><strong>${changes}</strong> ${escapeHtml(t("summary_changes", { count: "" }).trim())}</span>`,
  ].join("");
  if (els.exportButton) {
    els.exportButton.disabled = changes === 0;
  }
}

function renderList() {
  if (!els.invoiceList) return;
  state.filtered = filterInvoices(state.invoices, state.filters);
  if (!state.filtered.some((invoice) => invoice.id === state.selectedId)) {
    state.selectedId = state.filtered[0]?.id || "";
  }
  els.invoiceList.innerHTML = state.filtered.map((invoice) => {
    const edit = state.editState[invoice.id] || invoice;
    const isSelected = invoice.id === state.selectedId;
    const hasChanges = changedInvoices({ ...state.bundle, invoices: [invoice] }, state.editState).length > 0;
    return `
      <button class="invoice-row${isSelected ? " selected" : ""}" data-id="${escapeHtml(invoice.id)}" type="button">
        <span class="row-main">
          <span>${escapeHtml(invoice.profile_name || t("no_profile"))}</span>
          <strong>${escapeHtml(invoice.sender || invoice.filename || invoice.id)}</strong>
        </span>
        <span class="row-side">
          <span>${formatCurrency(edit.amount, invoice.currency)}</span>
          <span class="status-dot ${escapeHtml(edit.review_status)}">${escapeHtml(statusLabel(edit.review_status))}</span>
          ${hasChanges ? `<span class="changed">${escapeHtml(t("badge_changed"))}</span>` : ""}
        </span>
      </button>
    `;
  }).join("");
}

function renderDetail() {
  if (!els.detailEmpty || !els.detailForm) return;
  const invoice = state.invoices.find((item) => item.id === state.selectedId);
  if (!invoice) {
    els.detailEmpty.hidden = false;
    els.detailForm.hidden = true;
    return;
  }

  const edit = state.editState[invoice.id] || invoice;
  els.detailEmpty.hidden = true;
  els.detailForm.hidden = false;
  els.detailTitle.textContent = invoice.subject || invoice.filename || invoice.id;
  els.detailMeta.textContent = [
    invoice.date,
    invoice.profile_name,
    invoice.sender,
    invoice.filename,
  ].filter(Boolean).join(" · ");
  els.amountInput.value = edit.amount === null ? "" : String(edit.amount);
  els.statusInput.value = edit.review_status;
  els.notesInput.value = edit.notes;
  const fileRef = invoice.files[0];
  els.fileHash.textContent = fileRef?.sha256 || invoice.local_hash || t("no_hash");
}

function render() {
  renderSummary();
  renderList();
  renderDetail();
}

function statusLabel(value) {
  const map = {
    unreviewed: "status_unreviewed",
    reviewed: "status_reviewed",
    needs_clarification: "status_needs_clarification",
    rejected: "status_rejected",
  };
  const key = map[value];
  return key ? t(key) : value;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function readBundleFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      setBundle(JSON.parse(String(reader.result)));
      toast(t("toast_bundle_loaded"));
    } catch (error) {
      toast(error.message);
    }
  };
  reader.readAsText(file, "utf-8");
}

function exportChanges() {
  if (!state.bundle) {
    return;
  }
  const changeBundle = buildChangeBundle(state.bundle, state.editState);
  const blob = new Blob([JSON.stringify(changeBundle, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `universalinvoicemail-companion-changes-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
  toast(t("toast_exported", { count: changeBundle.invoices.length }));
}

function updateSelectedField(fieldName, value) {
  if (!state.selectedId) {
    return;
  }
  try {
    state.editState = updateEditState(state.editState, state.selectedId, fieldName, value);
    render();
  } catch (error) {
    toast(error.message);
  }
}

if (els.langSelect) {
  els.langSelect.addEventListener("change", (event) => {
    setLanguage(event.target.value);
  });
}

if (els.fileInput) {
  els.fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) {
      readBundleFile(file);
    }
  });
}

if (els.restoreButton) {
  els.restoreButton.addEventListener("click", () => {
    try {
      const restored = loadPersistedBundle(window.localStorage);
      if (restored) {
        setBundle(restored, { persist: false });
        toast(t("toast_restored"));
      } else {
        toast(t("toast_no_restored"));
      }
    } catch (error) {
      toast(error.message);
    }
  });
}

if (els.clearButton) {
  els.clearButton.addEventListener("click", () => {
    clearPersistedBundle(window.localStorage);
    toast(t("toast_cleared"));
  });
}

if (els.exportButton) {
  els.exportButton.addEventListener("click", exportChanges);
}

if (els.queryInput) {
  els.queryInput.addEventListener("input", (event) => {
    state.filters.query = event.target.value;
    render();
  });
}

if (els.profileSelect) {
  els.profileSelect.addEventListener("change", (event) => {
    state.filters.profile = event.target.value;
    render();
  });
}

if (els.statusSelect) {
  els.statusSelect.addEventListener("change", (event) => {
    state.filters.reviewStatus = event.target.value;
    render();
  });
}

if (els.invoiceList) {
  els.invoiceList.addEventListener("click", (event) => {
    const row = event.target.closest("[data-id]");
    if (!row) {
      return;
    }
    state.selectedId = row.dataset.id;
    render();
  });
}

if (els.amountInput) {
  els.amountInput.addEventListener("input", (event) => updateSelectedField("amount", event.target.value));
}
if (els.statusInput) {
  els.statusInput.addEventListener("change", (event) => updateSelectedField("review_status", event.target.value));
}
if (els.notesInput) {
  els.notesInput.addEventListener("input", (event) => updateSelectedField("notes", event.target.value));
}

let initialLang = "de";
try {
  initialLang = window.localStorage?.getItem("uim_lang") || (navigator.language?.slice(0, 2)) || "de";
  if (!TRANSLATIONS[initialLang]) {
    initialLang = "de";
  }
} catch {}

if (typeof document !== "undefined") {
  setLanguage(initialLang);

  try {
    const restored = loadPersistedBundle(window.localStorage);
    if (restored) {
      setBundle(restored, { persist: false });
    } else {
      render();
    }
  } catch {
    render();
  }

  if (typeof navigator !== "undefined" && "serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }
}
