export const BUNDLE_SCHEMA = "universalinvoicemail-invoicebundle-v1";
export const COMPANION_APP = "UniversalInvoiceMail Web Companion";
export const ALLOWED_COMPANION_FIELDS = ["amount", "review_status", "notes"];
export const REVIEW_STATUSES = [
  { value: "unchecked", label: "Ungeprüft" },
  { value: "checked", label: "Geprüft" },
  { value: "needs_question", label: "Rückfrage" },
  { value: "ready", label: "Bereit" },
];

const REVIEW_STATUS_VALUES = new Set(REVIEW_STATUSES.map((status) => status.value));
const STORAGE_KEY = "universalinvoicemail:lastBundle";

function asText(value, maxLength = 1000) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value).trim().slice(0, maxLength);
}

export function normalizeAmount(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const normalized = String(value).trim().replace(",", ".");
  if (!normalized) {
    return null;
  }
  const amount = Number.parseFloat(normalized);
  if (!Number.isFinite(amount)) {
    throw new Error(`invalid amount: ${value}`);
  }
  return Math.round(amount * 100) / 100;
}

export function normalizeReviewStatus(value) {
  const status = asText(value, 40).toLowerCase() || "unchecked";
  if (!REVIEW_STATUS_VALUES.has(status)) {
    throw new Error(`invalid review_status: ${status}`);
  }
  return status;
}

function normalizeFileReference(reference) {
  return {
    relative_path: asText(reference?.relative_path, 500),
    filename: asText(reference?.filename, 260),
    mime_type: asText(reference?.mime_type, 120) || "application/pdf",
    sha256: asText(reference?.sha256, 128),
    size_bytes: Number.isFinite(Number(reference?.size_bytes)) ? Number(reference.size_bytes) : 0,
  };
}

export function normalizeInvoice(invoice) {
  const id = asText(invoice?.id, 120);
  if (!id) {
    throw new Error("invoice row without id");
  }
  return {
    id,
    profile_id: asText(invoice?.profile_id, 120),
    profile_name: asText(invoice?.profile_name, 120),
    date: asText(invoice?.date, 40),
    sender: asText(invoice?.sender, 200),
    subject: asText(invoice?.subject, 300),
    filename: asText(invoice?.filename, 260),
    amount: normalizeAmount(invoice?.amount),
    currency: asText(invoice?.currency, 16) || "EUR",
    review_status: normalizeReviewStatus(invoice?.review_status),
    notes: asText(invoice?.notes, 4000),
    datev_status: asText(invoice?.datev_status, 80),
    files: Array.isArray(invoice?.files) ? invoice.files.map(normalizeFileReference) : [],
    local_hash: asText(invoice?.local_hash, 128),
  };
}

export function normalizeBundle(bundle) {
  if (!bundle || bundle.schema !== BUNDLE_SCHEMA) {
    throw new Error(`unsupported bundle schema: ${bundle?.schema || "missing"}`);
  }
  const invoices = Array.isArray(bundle.invoices) ? bundle.invoices.map(normalizeInvoice) : [];
  return {
    ...bundle,
    invoices,
    profiles: Array.isArray(bundle.profiles) ? bundle.profiles : [],
    companion_changes: {
      mode: bundle.companion_changes?.mode || "none",
      allowed_fields: ALLOWED_COMPANION_FIELDS.slice(),
    },
  };
}

export function createEditState(invoices) {
  return Object.fromEntries(
    invoices.map((invoice) => [
      invoice.id,
      {
        amount: invoice.amount,
        review_status: invoice.review_status,
        notes: invoice.notes,
      },
    ]),
  );
}

export function updateEditState(editState, invoiceId, fieldName, value) {
  if (!ALLOWED_COMPANION_FIELDS.includes(fieldName)) {
    throw new Error(`field is not allowed in companion edits: ${fieldName}`);
  }
  const current = editState[invoiceId] || {};
  const nextValue = fieldName === "amount"
    ? normalizeAmount(value)
    : fieldName === "review_status"
      ? normalizeReviewStatus(value)
      : asText(value, 4000);
  return {
    ...editState,
    [invoiceId]: {
      ...current,
      [fieldName]: nextValue,
    },
  };
}

function editDiffers(invoice, edit) {
  if (!edit) {
    return false;
  }
  return invoice.amount !== normalizeAmount(edit.amount)
    || invoice.review_status !== normalizeReviewStatus(edit.review_status)
    || invoice.notes !== asText(edit.notes, 4000);
}

export function changedInvoices(bundle, editState) {
  const normalized = normalizeBundle(bundle);
  return normalized.invoices
    .filter((invoice) => editDiffers(invoice, editState[invoice.id]))
    .map((invoice) => {
      const edit = editState[invoice.id];
      return {
        id: invoice.id,
        amount: normalizeAmount(edit.amount),
        review_status: normalizeReviewStatus(edit.review_status),
        notes: asText(edit.notes, 4000),
        files: invoice.files,
        local_hash: invoice.local_hash,
      };
    });
}

export function buildChangeBundle(bundle, editState, now = new Date()) {
  const normalized = normalizeBundle(bundle);
  const invoices = changedInvoices(normalized, editState);
  return {
    schema: BUNDLE_SCHEMA,
    created_at: now.toISOString(),
    source: {
      app: COMPANION_APP,
      version: "pwa-1",
      platform: "web",
    },
    original_source: normalized.source || null,
    export_options: {
      include_profiles: false,
      include_file_references: true,
      include_mail_bodies: false,
      include_attachments: false,
    },
    profiles: [],
    invoices,
    datev: null,
    companion_changes: {
      mode: "changes",
      allowed_fields: ALLOWED_COMPANION_FIELDS.slice(),
    },
  };
}

export function summarizeBundle(bundle) {
  const normalized = normalizeBundle(bundle);
  const statusCounts = Object.fromEntries(REVIEW_STATUSES.map((status) => [status.value, 0]));
  let missingAmount = 0;
  let readyForDatev = 0;
  for (const invoice of normalized.invoices) {
    statusCounts[invoice.review_status] = (statusCounts[invoice.review_status] || 0) + 1;
    if (invoice.amount === null) {
      missingAmount += 1;
    }
    if (invoice.datev_status === "ready" || invoice.amount !== null) {
      readyForDatev += 1;
    }
  }
  return {
    invoiceCount: normalized.invoices.length,
    profileCount: normalized.profiles.length,
    missingAmount,
    readyForDatev,
    statusCounts,
  };
}

export function filterInvoices(invoices, filters = {}) {
  const query = asText(filters.query).toLowerCase();
  const profile = asText(filters.profile);
  const reviewStatus = asText(filters.reviewStatus);
  return invoices.filter((invoice) => {
    if (profile && invoice.profile_name !== profile) {
      return false;
    }
    if (reviewStatus && invoice.review_status !== reviewStatus) {
      return false;
    }
    if (!query) {
      return true;
    }
    const haystack = [
      invoice.id,
      invoice.profile_name,
      invoice.sender,
      invoice.subject,
      invoice.filename,
      invoice.notes,
      invoice.date,
    ].join(" ").toLowerCase();
    return haystack.includes(query);
  });
}

export function listProfiles(invoices) {
  return Array.from(new Set(invoices.map((invoice) => invoice.profile_name).filter(Boolean))).sort((a, b) => (
    a.localeCompare(b, "de")
  ));
}

export function formatCurrency(value, currency = "EUR", locale = "de-DE") {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(Number(value));
}

export function persistBundle(storage, bundle) {
  storage.setItem(STORAGE_KEY, JSON.stringify(normalizeBundle(bundle)));
}

export function loadPersistedBundle(storage) {
  const raw = storage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  return normalizeBundle(JSON.parse(raw));
}

export function clearPersistedBundle(storage) {
  storage.removeItem(STORAGE_KEY);
}
