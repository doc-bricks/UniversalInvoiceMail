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

const els = {
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
};

function toast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 2800);
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
  const profiles = listProfiles(state.invoices);
  els.profileSelect.innerHTML = [
    `<option value="">Alle Profile</option>`,
    ...profiles.map((profile) => `<option value="${escapeHtml(profile)}">${escapeHtml(profile)}</option>`),
  ].join("");

  els.statusSelect.innerHTML = [
    `<option value="">Alle Status</option>`,
    ...REVIEW_STATUSES.map((status) => (
      `<option value="${status.value}">${escapeHtml(status.label)}</option>`
    )),
  ].join("");
}

function renderSummary() {
  if (!state.bundle) {
    els.summary.innerHTML = `<span>Kein Bundle geladen</span>`;
    return;
  }
  const summary = summarizeBundle(state.bundle);
  const changes = changedInvoices(state.bundle, state.editState).length;
  els.summary.innerHTML = [
    `<span><strong>${summary.invoiceCount}</strong> Rechnungen</span>`,
    `<span><strong>${summary.missingAmount}</strong> ohne Betrag</span>`,
    `<span><strong>${summary.readyForDatev}</strong> DATEV-bereit</span>`,
    `<span><strong>${changes}</strong> Änderungen</span>`,
  ].join("");
  els.exportButton.disabled = changes === 0;
}

function renderList() {
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
          <span>${escapeHtml(invoice.profile_name || "Ohne Profil")}</span>
          <strong>${escapeHtml(invoice.sender || invoice.filename || invoice.id)}</strong>
        </span>
        <span class="row-side">
          <span>${formatCurrency(edit.amount, invoice.currency)}</span>
          <span class="status-dot ${escapeHtml(edit.review_status)}">${statusLabel(edit.review_status)}</span>
          ${hasChanges ? `<span class="changed">geändert</span>` : ""}
        </span>
      </button>
    `;
  }).join("");
}

function renderDetail() {
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
  els.fileHash.textContent = fileRef?.sha256 || invoice.local_hash || "Kein Hash im Bundle";
}

function render() {
  renderSummary();
  renderList();
  renderDetail();
}

function statusLabel(value) {
  return REVIEW_STATUSES.find((status) => status.value === value)?.label || value;
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
      toast("Bundle geladen");
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
  toast(`${changeBundle.invoices.length} Änderungen exportiert`);
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

els.fileInput.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (file) {
    readBundleFile(file);
  }
});

els.restoreButton.addEventListener("click", () => {
  try {
    const restored = loadPersistedBundle(window.localStorage);
    if (restored) {
      setBundle(restored, { persist: false });
      toast("Lokales Bundle wiederhergestellt");
    } else {
      toast("Kein lokales Bundle gespeichert");
    }
  } catch (error) {
    toast(error.message);
  }
});

els.clearButton.addEventListener("click", () => {
  clearPersistedBundle(window.localStorage);
  toast("Lokaler Browser-Stand gelöscht");
});

els.exportButton.addEventListener("click", exportChanges);

els.queryInput.addEventListener("input", (event) => {
  state.filters.query = event.target.value;
  render();
});

els.profileSelect.addEventListener("change", (event) => {
  state.filters.profile = event.target.value;
  render();
});

els.statusSelect.addEventListener("change", (event) => {
  state.filters.reviewStatus = event.target.value;
  render();
});

els.invoiceList.addEventListener("click", (event) => {
  const row = event.target.closest("[data-id]");
  if (!row) {
    return;
  }
  state.selectedId = row.dataset.id;
  render();
});

els.amountInput.addEventListener("input", (event) => updateSelectedField("amount", event.target.value));
els.statusInput.addEventListener("change", (event) => updateSelectedField("review_status", event.target.value));
els.notesInput.addEventListener("input", (event) => updateSelectedField("notes", event.target.value));

for (const status of REVIEW_STATUSES) {
  const option = document.createElement("option");
  option.value = status.value;
  option.textContent = status.label;
  els.statusInput.append(option);
}

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

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}
