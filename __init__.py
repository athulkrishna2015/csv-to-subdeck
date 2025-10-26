# -*- coding: utf-8 -*-

"""
CSV File Import+ (Subdeck & Autodetect)

A file-based sibling to the CSV Paste Import dialog:
- Pick a CSV file
- Auto-detect delimiter and rows
- Optional: first row is header
- Choose deck and note type
- Create a subdeck (prefilled from filename)
- Quick Import directly OR open Anki's default Import dialog

This mirrors the UX and helpers found in the CSV Paste add-on (note-type
auto-pick, directives like #notetype:Basic, delimiter detection, subdeck tools).
"""

from aqt import mw, gui_hooks
from aqt.qt import (
    QAction, QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)
from aqt.utils import showInfo, showWarning
from aqt.importing import importFile

import csv
import io
import os
import re
import tempfile


PROFILE_KEY_LAST_DIR = "csv_file_import_plus_last_dir"


class CSVFileImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.deck_infos = []
        self.model_infos = []
        self.file_path = ""
        self.setup_ui()

    # -------------------- UI --------------------
    def setup_ui(self):
        self.setWindowTitle("CSV File Import+")
        self.setMinimumSize(720, 520)

        root = QVBoxLayout()

        # Instructions
        instr = QLabel(
            "1) Choose a CSV, 2) Adjust options, 3) Pick deck and note type, 4) Import.\n"
            "Supported delimiters: comma, tab, semicolon, pipe. Directives: #notetype:Basic\n"
            "Quick Import adds notes directly; Import with Anki dialog opens the standard importer."
        )
        instr.setWordWrap(True)
        root.addWidget(instr)

        # File row
        file_group = QGroupBox("CSV File")
        file_form = QFormLayout()
        file_row = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("No file selected…")
        self.file_edit.setReadOnly(True)
        self.browse_btn = QPushButton("Browse…")
        self.browse_btn.clicked.connect(self.pick_file)
        file_row.addWidget(self.file_edit)
        file_row.addWidget(self.browse_btn)
        file_form.addRow("", self.wrap_layout(file_row))

        # Header toggle
        self.header_check = QCheckBox("First row is header")
        self.header_check.toggled.connect(self.on_content_changed)
        file_form.addRow("", self.header_check)

        file_group.setLayout(file_form)
        root.addWidget(file_group)

        # Status line
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #21808D; font-weight: 500;")
        root.addWidget(self.status_label)

        # Settings
        settings_group = QGroupBox("Import Settings")
        settings_form = QFormLayout()

        # Deck combo
        self.deck_combo = QComboBox()
        self.refresh_decks()  # also selects current deck if present
        settings_form.addRow("Target Deck:", self.deck_combo)

        # Subdeck creator
        subdeck_container = QWidget(self)
        subdeck_row = QHBoxLayout(subdeck_container)
        self.subdeck_edit = QLineEdit()
        self.subdeck_edit.setPlaceholderText("New subdeck name (prefilled from file)")
        self.create_subdeck_btn = QPushButton("Create subdeck")
        self.create_subdeck_btn.clicked.connect(self.create_subdeck)
        subdeck_row.addWidget(self.subdeck_edit)
        subdeck_row.addWidget(self.create_subdeck_btn)
        subdeck_container.setEnabled(self.deck_combo.count() > 0)
        self.deck_combo.currentIndexChanged.connect(
            lambda _: subdeck_container.setEnabled(self.deck_combo.count() > 0)
        )
        settings_form.addRow("Add Subdeck:", subdeck_container)

        # Note type combo
        self.notetype_combo = QComboBox()
        try:
            self.model_infos = list(mw.col.models.all_names_and_ids())
        except Exception:
            self.model_infos = []
        self.notetype_combo.addItems([m.name for m in self.model_infos])
        settings_form.addRow("Note Type:", self.notetype_combo)

        # Delimiter combo
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([
            "Auto-detect",
            "Comma (,)",
            "Tab",
            "Semicolon (;)",
            "Pipe (|)",
        ])
        self.delimiter_combo.setCurrentIndex(0)
        self.delimiter_combo.currentIndexChanged.connect(self.on_content_changed)
        settings_form.addRow("Delimiter:", self.delimiter_combo)

        settings_group.setLayout(settings_form)
        root.addWidget(settings_group)

        # Buttons
        btns = QHBoxLayout()
        self.quick_btn = QPushButton("Quick Import")
        self.quick_btn.clicked.connect(self.do_import)
        self.quick_btn.setDefault(True)
        self.anki_btn = QPushButton("Import with Anki dialog")
        self.anki_btn.clicked.connect(self.open_with_default_importer)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(self.quick_btn)
        btns.addWidget(self.anki_btn)
        btns.addWidget(cancel_btn)
        root.addLayout(btns)

        self.setLayout(root)

    def wrap_layout(self, layout):
        # Wrap a QLayout into a QWidget for use in QFormLayout rows
        w = QWidget(self)
        w.setLayout(layout)
        return w

    # -------------------- Deck/model helpers --------------------
    def refresh_decks(self, select_name: str | None = None):
        try:
            self.deck_infos = list(mw.col.decks.all_names_and_ids())
        except Exception:
            self.deck_infos = []
        self.deck_combo.clear()
        names = [d.name for d in self.deck_infos]
        self.deck_combo.addItems(names)
        # Select current deck by default
        try:
            cur = mw.col.decks.current()
            cur_name = cur["name"] if isinstance(cur, dict) else getattr(cur, "name", "")
            if cur_name:
                idx = self.deck_combo.findText(cur_name)
                if idx >= 0:
                    self.deck_combo.setCurrentIndex(idx)
        except Exception:
            pass
        # Optionally select requested deck name
        if select_name:
            idx = self.deck_combo.findText(select_name)
            if idx >= 0:
                self.deck_combo.setCurrentIndex(idx)

    def _deck_id_from_index(self, i):
        if not self.deck_infos or i < 0 or i >= len(self.deck_infos):
            return None
        d = self.deck_infos[i]
        return getattr(d, "id", getattr(d, "did", None))

    def _model_id_from_index(self, i):
        if not self.model_infos or i < 0 or i >= len(self.model_infos):
            return None
        m = self.model_infos[i]
        return getattr(m, "id", None)

    def create_subdeck(self):
        parent_name = self.deck_combo.currentText().strip()
        child = self.subdeck_edit.text().strip()
        if not child:
            showWarning("Enter a subdeck name first.")
            return
        child = re.sub(r"\s{2,}", " ", child)
        full_name = f"{parent_name}::{child}"
        try:
            did = mw.col.decks.id(full_name)  # creates if missing
            mw.col.decks.select(did)
            self.refresh_decks(select_name=full_name)
            self.status_label.setText(f"✓ Created subdeck: {full_name}")
            # Clear after success
            self.subdeck_edit.clear()
        except Exception as e:
            showWarning(f"Could not create subdeck: {e}")

    # -------------------- File and content --------------------
    def pick_file(self):
        start_dir = mw.pm.profile.get(PROFILE_KEY_LAST_DIR, "")
        path, _ = QFileDialog.getOpenFileName(
            mw, "Select CSV to Import", start_dir, "CSV Files (*.csv)"
        )
        if not path:
            return
        self.file_path = path
        self.file_edit.setText(path)
        try:
            mw.pm.profile[PROFILE_KEY_LAST_DIR] = os.path.dirname(path)
        except Exception:
            pass
        # Prefill subdeck name from file name
        base = os.path.splitext(os.path.basename(path))[0]
        self.subdeck_edit.setText(base)
        self.on_content_changed()

    def read_file_text(self) -> str:
        if not self.file_path:
            return ""
        # Try utf-8, fallback to utf-8-sig
        for enc in ("utf-8", "utf-8-sig"):
            try:
                with open(self.file_path, "r", encoding=enc, newline="") as f:
                    return f.read()
            except Exception:
                continue
        # Last resort
        try:
            with open(self.file_path, "r", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    # -------------------- Directives and detection --------------------
    def extract_directives(self, content: str) -> dict:
        directives = {}
        for line in content.splitlines():
            if not line.strip():
                continue
            if not line.lstrip().startswith("#"):
                break
            m = re.match(r"^\s*#\s*([A-Za-z0-9_\-]+)\s*:\s*(.+?)\s*$", line)
            if m:
                directives[m.group(1).lower()] = m.group(2)
        return directives

    def strip_directive_lines(self, content: str) -> str:
        out = []
        skipping = True
        for line in content.splitlines():
            if skipping and line.strip().startswith("#"):
                continue
            skipping = skipping and not line.strip()
            if not skipping:
                out.append(line)
        return "\n".join(out)

    def normalize_name(self, s: str) -> str:
        s = s.strip().lower()
        s = re.sub(r"[\s_\-]+", " ", s)
        s = re.sub(r"[^a-z0-9 ]+", "", s)
        return s

    def find_model_index_by_name(self, name: str):
        if not name:
            return None
        target = name.strip().lower()
        alias_map = {
            "cloze": "cloze",
            "basic": "basic",
            "basic (and reversed card)": "basic (and reversed card)",
            "basic (type in the answer)": "basic (type in the answer)",
        }
        target = alias_map.get(target, target)
        for i, m in enumerate(self.model_infos):
            if m.name.strip().lower() == target:
                return i
        return None

    def detect_csv_format(self, content: str):
        sample = content[:2048]
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except Exception:
            delimiter = self.fallback_delimiter_detection(sample)
        reader = csv.reader(io.StringIO(content), delimiter=delimiter)
        rows = sum(1 for _ in reader)
        return delimiter, rows

    def fallback_delimiter_detection(self, sample: str):
        lines = sample.split("\n")[:5]
        if not lines:
            return ","
        delims = [",", "\t", ";", "|"]
        delimiter_counts = {}
        for d in delims:
            counts = [line.count(d) for line in lines if line.strip()]
            if counts:
                avg = sum(counts) / len(counts)
                if len(set(counts)) == 1 and counts[0] > 0:
                    delimiter_counts[d] = (avg, True)
                elif avg > 0:
                    delimiter_counts[d] = (avg, False)
        if delimiter_counts:
            sorted_delims = sorted(
                delimiter_counts.items(),
                key=lambda x: (x[1][1], x[1][0]),
                reverse=True,
            )
            return sorted_delims[0][0]
        return ","

    def get_delimiter_name(self, delimiter: str):
        names = {
            ",": "Comma (,)",
            "\t": "Tab",
            ";": "Semicolon (;)",
            "|": "Pipe (|)",
        }
        return names.get(delimiter, f"'{delimiter}'")

    def get_delimiter(self):
        selection = self.delimiter_combo.currentText()
        if selection == "Auto-detect":
            content = self.strip_directive_lines(self.read_file_text().strip())
            if content:
                try:
                    delimiter, _ = self.detect_csv_format(content)
                    return delimiter
                except Exception:
                    return ","
            return ","
        mapping = {
            "Comma (,)": ",",
            "Tab": "\t",
            "Semicolon (;)": ";",
            "Pipe (|)": "|",
        }
        return mapping.get(selection, ",")

    def auto_pick_note_type(self, content: str, delimiter: str):
        try:
            reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            rows = [r for r in reader if any(c.strip() for c in r)]
        except Exception:
            rows = []
        if not rows:
            return None
        # header?
        has_header_hint = self.header_check.isChecked()
        try:
            sniffer = csv.Sniffer()
            has_header_guess = sniffer.has_header(content[:2048])
        except Exception:
            has_header_guess = False
        has_header = has_header_hint or has_header_guess
        header = [c.strip() for c in rows[0]] if has_header else None
        sample_rows = rows[1:21] if has_header else rows[:20]
        col_counts = [len(r) for r in sample_rows] or [len(rows[0])]
        observed_cols = max(col_counts) if col_counts else len(rows[0])

        try:
            model_infos = list(mw.col.models.all_names_and_ids())
        except Exception:
            model_infos = []
        if not model_infos:
            return None

        best = None
        best_idx = None
        best_name = None
        best_fields = None

        header_norm = [self.normalize_name(h) for h in (header or [])]
        for idx, m in enumerate(model_infos):
            try:
                nt = mw.col.models.get(m.id)
                field_names = [f["name"] for f in nt["flds"]]
            except Exception:
                continue
            field_count = len(field_names)
            fields_norm = [self.normalize_name(x) for x in field_names]

            # name similarity
            score_name = 0
            if header_norm:
                for h in header_norm:
                    if not h:
                        continue
                    if h in fields_norm:
                        score_name += 3
                    else:
                        if any(h in fn or fn in h for fn in fields_norm if fn):
                            score_name += 1

            # column closeness
            diff = abs(observed_cols - field_count)
            if diff == 0:
                score_cols = 3
            elif diff == 1:
                score_cols = 2
            elif diff == 2:
                score_cols = 1
            else:
                score_cols = 0

            score_tuple = (score_name, score_cols, -field_count)
            if (best is None) or (score_tuple > best):
                best = score_tuple
                best_idx = idx
                best_name = m.name
                best_fields = field_count

        if best_idx is None:
            return None
        try:
            self.notetype_combo.setCurrentIndex(best_idx)
        except Exception:
            pass
        return (best_name, best_fields)

    # -------------------- Status / content change --------------------
    def on_content_changed(self):
        raw = self.read_file_text().strip()
        if not raw:
            self.status_label.setText("")
            return

        directives = self.extract_directives(raw)
        content = self.strip_directive_lines(raw)

        # Directive notetype override
        nt_name = directives.get("notetype")
        forced_model_info = None
        if nt_name:
            idx = self.find_model_index_by_name(nt_name)
            if idx is not None:
                try:
                    self.notetype_combo.setCurrentIndex(idx)
                    forced_model_info = (
                        self.model_infos[idx].name,
                        len(mw.col.models.get(self.model_infos[idx].id)["flds"]),
                    )
                except Exception:
                    pass

        # Delimiter and rows
        if self.delimiter_combo.currentText() == "Auto-detect":
            try:
                delimiter, rows = self.detect_csv_format(content)
            except Exception as e:
                self.status_label.setText(f"⚠ Detection failed: {str(e)}")
                return
        else:
            delimiter = self.get_delimiter()
            try:
                reader = csv.reader(io.StringIO(content), delimiter=delimiter)
                rows = sum(1 for _ in reader)
            except Exception:
                rows = 0
        delim_name = self.get_delimiter_name(delimiter)

        # Auto-pick note type if not forced
        detected_model = None
        if not forced_model_info:
            detected_model = self.auto_pick_note_type(content, delimiter)

        parts = []
        parts.append(f"✓ Detected: {delim_name} delimiter")
        parts.append(f"{rows} row(s)")
        if forced_model_info:
            model_name, field_count = forced_model_info
            parts.append(f"Note type: {model_name} ({field_count} field(s), via directive)")
        elif detected_model:
            model_name, field_count = detected_model
            parts.append(f"Note type: {model_name} ({field_count} field(s))")
        self.status_label.setText(" • ".join(parts))

    # -------------------- Import paths --------------------
    def open_with_default_importer(self):
        if not self.file_path:
            showWarning("Pick a CSV file first.")
            return

        # Select deck for sane defaults
        deck_idx = self.deck_combo.currentIndex()
        deck_id = self._deck_id_from_index(deck_idx)
        if deck_id is not None:
            try:
                mw.col.decks.select(deck_id)
            except Exception:
                pass

        # Strip directives by writing a cleaned temp file
        csv_raw = self.read_file_text().strip()
        csv_content = self.strip_directive_lines(csv_raw)

        try:
            fd, path = tempfile.mkstemp(prefix="anki_csv_file_", suffix=".csv", text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                    f.write(csv_content)
            except Exception as e:
                # fd might still be open on some platforms
                try:
                    os.close(fd)
                except Exception:
                    pass
                showWarning(f"Could not write temp CSV: {e}")
                return
        except Exception as e:
            showWarning(f"Could not create temp file: {e}")
            return

        try:
            importFile(mw, path)
            self.accept()
        except Exception as e:
            showWarning(f"Could not open import dialog: {e}")
        # Let Anki import hold the temp file; do not unlink immediately

    def do_import(self):
        if not self.file_path:
            showWarning("Pick a CSV file first.")
            return

        # Re-apply directive notetype at import time
        csv_raw = self.read_file_text().strip()
        directives = self.extract_directives(csv_raw)
        nt_name = directives.get("notetype")
        if nt_name:
            idx = self.find_model_index_by_name(nt_name)
            if idx is not None:
                self.notetype_combo.setCurrentIndex(idx)

        csv_content = self.strip_directive_lines(csv_raw)

        deck_idx = self.deck_combo.currentIndex()
        model_idx = self.notetype_combo.currentIndex()
        deck_id = self._deck_id_from_index(deck_idx)
        model_id = self._model_id_from_index(model_idx)

        if deck_id is None:
            showWarning("Could not resolve target deck.")
            return
        if model_id is None:
            showWarning("Could not resolve note type.")
            return

        try:
            notetype = mw.col.models.get(model_id)
            if not notetype:
                showWarning("Selected note type not found.")
                return

            delimiter = self.get_delimiter()
            reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
            rows = [r for r in reader]
            if not rows:
                showWarning("No data rows found.")
                return

            if self.header_check.isChecked() and len(rows) > 1:
                rows = rows[1:]

            field_names = [f["name"] for f in notetype["flds"]]
            mw.col.decks.select(deck_id)

            added = 0
            skipped_empty = 0
            for row in rows:
                if not row or all(not c.strip() for c in row):
                    skipped_empty += 1
                    continue
                note = mw.col.new_note(notetype)
                for i, val in enumerate(row[:len(field_names)]):
                    note.fields[i] = val.strip()
                # Tags from last column if extra
                if len(row) > len(field_names):
                    tags = row[-1].strip()
                    if tags:
                        note.tags = tags.split()
                mw.col.add_note(note, deck_id)
                added += 1

            mw.reset()
            msg = f"Import complete!\n\nAdded: {added} note(s)"
            if skipped_empty:
                msg += f"\nSkipped empty rows: {skipped_empty}"
            if self.delimiter_combo.currentText() == "Auto-detect":
                msg += f"\n\nUsed delimiter: {self.get_delimiter_name(delimiter)}"
            showInfo(msg)
            self.accept()

        except Exception as e:
            showWarning(f"Import failed: {str(e)}")


# -------------------- Menu integration --------------------
def show_csv_file_import_dialog():
    dlg = CSVFileImportDialog(mw)
    dlg.exec()


def setup_menu():
    action = QAction("CSV File Import…", mw)
    action.triggered.connect(show_csv_file_import_dialog)
    mw.form.menuTools.addAction(action)


gui_hooks.main_window_did_init.append(setup_menu)
