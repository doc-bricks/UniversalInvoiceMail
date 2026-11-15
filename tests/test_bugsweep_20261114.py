"""Regressionstests — Bugsweep UniversalInvoiceMail 2026-11-14 (IMAP-Suche mit Umlauten)."""
from unittest.mock import MagicMock

from tests.test_integration import uim  # Modul-Setup (Qt-/Optional-Mocks) wiederverwenden


class _AsciiImap:
    """Kodiert str-Argumente wie imaplib (ASCII, im UTF8=ACCEPT-Modus UTF-8); Literal über .literal."""

    def __init__(self, hits, utf8=False):
        self.hits, self.utf8_enabled, self.literal = hits, utf8, None
        self.capabilities = ()
        self.searches, self.fetched = [], []

    def uid(self, command, *args):
        encoding = "utf-8" if self.utf8_enabled else "ascii"
        for arg in args:
            if isinstance(arg, str):
                bytes(arg, encoding)
        if command == "fetch":
            self.fetched.append(args[0])
            return "OK", [None]
        literal, self.literal = self.literal, None
        self.searches.append((args, literal))
        values = [literal.decode("utf-8")] if literal is not None else []
        values += [a.strip('"') for a in args if isinstance(a, str) and a.startswith('"')]
        # Testserver: jedes Kriterium für sich (OR/AND-Logik testet der Client)
        matched = set()
        for value in values:
            matched |= set(self.hits.get(value, []))
        if len(values) > 1 and "OR" not in args:
            matched = set.intersection(*(set(self.hits.get(v, [])) for v in values))
        return "OK", [b" ".join(sorted(matched, key=int))]


def _worker(sender="", subject=""):
    account = uim.MailAccount(id="a", name="A", provider="IMAP")
    profile = uim.InvoiceProfile(id="p", name="Shop", account_id="a", sender_filter=sender,
                                 subject_filter=subject, enabled=True)
    settings = uim.AppSettings()
    settings.date_filter_months = 0
    worker = uim.InvoiceWorker([account], [profile], settings, set())
    worker.log = MagicMock()
    worker.progress = MagicMock()
    worker.should_stop = False  # in der Gesamtsuite sonst ggf. ein (wahrer) Qt-Mock
    worker.settings.max_emails_per_run = 50
    return worker, profile


def _errors(worker):
    return [str(c.args[0]) for c in worker.log.emit.call_args_list if "fehlgeschlagen" in str(c.args[0])]


def test_imap_search_with_umlaut_subject_works():
    """imaplib kodiert Suchargumente als ASCII: Betreff „Rückerstattung“ oder Absender „Müller“ ließen
    die Suche scheitern („IMAP Suche fehlgeschlagen: 'ascii' codec…“) — keine Rechnung gefunden."""
    worker, profile = _worker(subject="Rückerstattung")
    mail = _AsciiImap({"Rückerstattung": [b"4", b"9"]})
    worker._search_imap(mail, profile)
    assert _errors(worker) == []
    assert mail.fetched == [b"4", b"9"]


def test_imap_search_umlaut_sender_or_group_and_subject():
    worker, profile = _worker(sender="Müller GmbH, shop.example", subject="Rechnung")
    mail = _AsciiImap({"Müller GmbH": [b"1", b"2"], "shop.example": [b"3"], "Rechnung": [b"2", b"3", b"8"]})
    worker._search_imap(mail, profile)
    assert _errors(worker) == []
    assert mail.fetched == [b"2", b"3"]  # (Müller ODER shop) UND Rechnung


def test_flat_search_args_unchanged_for_ascii():
    worker, profile = _worker(sender="a.de, b.de", subject="Rechnung")
    assert worker._build_imap_search_args(profile) == [
        "OR", "FROM", '"a.de"', "FROM", '"b.de"', "SUBJECT", '"Rechnung"']
