from aqt import mw
from aqt.qt import QAction, QFileDialog, QMessageBox
from aqt.importing import importFile
import os

def import_csv_with_default_dialog():
    file_path, _ = QFileDialog.getOpenFileName(mw, "Select CSV to Import", "", "CSV Files (*.csv)")
    if not file_path:
        return

    # Subdeck name from filename
    subdeck_name = os.path.splitext(os.path.basename(file_path))[0]

    # Parent is the currently selected deck
    main_deck_name = mw.col.decks.current()['name']
    full_deck_name = f"{main_deck_name}::{subdeck_name}"
    deck_id = mw.col.decks.id(full_deck_name)

    # Preselect this deck so Import dialog defaults to it
    mw.col.decks.select(deck_id)  # UI will default to this deck [web:10]

    try:
        # Launch the standard Import dialog for this file
        importFile(mw, file_path)  # Same code path as File → Import [web:99]
    except Exception as e:
        QMessageBox.critical(mw, "Import Failed", f"An error occurred: {str(e)}")

action = QAction("Import CSV (Default Dialog)", mw)
action.triggered.connect(import_csv_with_default_dialog)
mw.form.menuTools.addAction(action)
