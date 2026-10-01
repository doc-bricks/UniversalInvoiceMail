"""Private staging for CSV exports, without GUI or mail dependencies."""

from contextlib import contextmanager
import logging
import os
from pathlib import Path
import tempfile


def _check_target(target, protected_paths):
    resolved = target.resolve()
    for source in protected_paths:
        if resolved == source.resolve():
            raise ValueError("CSV-Ziel ist eine geschützte Quelldatei. Bitte einen anderen Pfad wählen.")
        try:
            same = target.samefile(source)
        except FileNotFoundError:
            same = False
        if same:
            raise ValueError("CSV-Ziel ist eine geschützte Quelldatei. Bitte einen anderen Pfad wählen.")


@contextmanager
def atomic_csv_output(output_path, protected_paths=()):
    """Publish only a complete UTF-8-BOM CSV; retain old output on failure.

    Identity checks protect known originals and state files, including aliases.
    They do not provide a transaction against concurrent external path changes.
    """
    target = Path(output_path)
    protected = tuple(Path(path) for path in protected_paths if path)
    _check_target(target, protected)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", newline="", delete=False,
            dir=target.parent, prefix=".uim-csv-", suffix=".tmp",
        ) as stream:
            temporary = Path(stream.name)
            yield stream
            stream.flush()
            os.fsync(stream.fileno())
        _check_target(target, protected)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                logging.warning("Eigene temporäre CSV-Datei konnte nicht entfernt werden: %s", temporary)
