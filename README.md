Depricated use [csv import plus](https://github.com/athulkrishna2015/csv-import-plus)

## [csv to subdeck](https://ankiweb.net/shared/info/1776942606)

#### Features
- Paste CSV content directly into a dedicated dialog with clear status feedback on delimiter, row count, and detected note type.[11]
- Auto‑detect comma, tab, semicolon, or pipe delimiters with a robust fallback and a manual override when needed.[11]
- Optional “First row is header” toggle to skip column names before import.[11]
- Smart note‑type auto‑pick by matching header names and column count to your collection’s note types.[11]
- Create a subdeck under the currently selected deck in one click, then import into it immediately.[11]
- Choose between Quick Import or “Import with Anki dialog” for the standard importer path and mapping options.[11]
- Support for a simple directive at the top of your CSV like “#notetype:Basic” or “#notetype:Cloze” to force the note type.[11]
- Treat the last extra column as tags during Quick Import, and skip empty rows automatically with a clear result summary.[11]

#### How to use
- Open Anki → Tools → “CSV Paste Import…” to launch the dialog.[11]
- Paste CSV, optionally tick “First row is header,” then select a deck and note type or rely on auto‑detection.[11]
- Use “Create subdeck” to add and preselect a child deck under the current deck before importing.[11]
- Click “Quick Import” to add notes immediately, or “Import with Anki dialog” to use Anki’s standard Import window with your chosen deck preselected.[11]

#### CSV directives
- Add a directive on top to force note type, for example: “#notetype:Basic” or “#notetype:Cloze” on its own line.[11]
- Directive lines are ignored during import to avoid polluting your data rows.[11]

#### Notes
- Auto‑detection uses csv.Sniffer with a consistent multi‑delimiter fallback to stay reliable on short or irregular CSV snippets.[11]
- When an extra column exists beyond the note type’s fields, the last column is parsed as whitespace‑separated tags during Quick Import.[11]
- The dialog preselects the currently active deck to keep imports fast and predictable.[11]

#### Troubleshooting
- If no rows are detected, verify the delimiter, uncheck “First row is header,” and confirm the pasted content has visible separators.[11]
- If the wrong note type is chosen, set it explicitly via the dropdown or by adding “#notetype:Your Note Type” at the top of the CSV.[11]
- If you need field mapping or more advanced options, use “Import with Anki dialog” from within the add‑on dialog.[11]

***

### GitHub README.md
CSV Import+ for Anki: paste CSV into a dialog, auto‑detect the delimiter, auto‑pick the note type, create a subdeck, and import via Quick Import or the standard Anki importer.[11]

#### Why this add‑on
- Eliminates repetitive deck switching and guesswork by preselecting target decks and suggesting the best‑fit note type.[11]
- Speeds up CSV workflows with a single window for paste, detection, subdeck creation, and import decisions.[11]
- Keeps power‑user escape hatches via directives and the ability to launch the default importer on demand.[11]

#### Features
- Paste‑based CSV workflow with live status for delimiter, row count, and detected note type.[11]
- Supported delimiters: comma, tab, semicolon, pipe, with manual override and resilient fallback detection logic.[11]
- Header handling: optional “First row is header” to skip column names cleanly.[11]
- Note‑type detection: matches header names and column counts against your collection’s models.[11]
- Subdeck creation: add “Parent::Child” automatically under the selected deck, then import into it.[11]
- Dual import paths: Quick Import for instant adds, or open Anki’s standard Import dialog for mapping and verification.[11]
- CSV directives: “#notetype:Basic” or “#notetype:Cloze” to pin note type, with directive lines stripped before import.[11]
- Tag support: extra last column is treated as tags during Quick Import, with whitespace splitting.[11]

#### Installation
- From AnkiWeb: install via Anki’s Add‑ons manager as usual and restart Anki to load the add‑on.[4]
- Manual install: open Anki → Tools → Add‑ons → Open add‑ons folder, place the add‑on folder inside, and restart Anki to enable it.[4]

#### Usage
- Launch: Tools → “CSV Paste Import…” from Anki’s main window.[11]
- Paste CSV, optionally enable “First row is header,” and pick a deck and note type or use the suggested defaults.[11]
- Create subdeck if desired, then choose Quick Import or “Import with Anki dialog” depending on how much control you need.[11]
- For consistent note type selection across sessions or teams, add a top‑line directive like “#notetype:Basic” in your CSV template.[11]

#### Tips
- If auto‑detection picks the wrong note type, set it explicitly once, then keep a directive in your CSV template to lock it.[11]
- If your CSV is sparse or irregular, manually set the delimiter and uncheck the header toggle to confirm row parsing.[11]
- Use “Import with Anki dialog” for edge cases that require column mapping or preview before committing.[11]

#### Limitations
- Quick Import assigns fields in order and treats only the final extra column as tags, without per‑column tag mapping.[11]
- Field count mismatches are truncated to available fields, so consider adding a directive or adjusting your template for best results.[11]
- The paste‑based workflow expects text CSV; very large files or complex encodings are better handled through the standard importer path.[11]

#### Privacy and safety
- The add‑on runs entirely on your machine and does not send your data to external services.[11]
- Temporary files may be created only when launching the standard importer and are kept just for that import flow.[11]

#### Contributing
- Bug reports and feature requests are welcome, and reproducible samples with a short CSV snippet greatly speed up fixes.[11]
- When suggesting detection improvements, include the first 10–20 lines of your CSV and note the expected delimiter and header usage.[11]
- Small, focused pull requests are preferred to keep the dialog fast and maintainable.[11]

#### Changelog
- v1.0.0: Initial release with delimiter auto‑detect, header handling, note‑type auto‑pick, subdeck creation, Quick Import, and “Import with Anki dialog”.[11]

#### Acknowledgements
- Built to streamline CSV workflows in Anki and inspired by the ergonomics of succinct import dialogs for power users.[11]

#### License
- This repository will adopt a permissive license in line with common Anki add‑on practice once selected for distribution.[11]

#### Support
- For questions, include your Anki version, platform, a short CSV sample, and whether Quick Import or the standard importer path was used.[11]

### Short AnkiWeb blurb
Paste CSV, auto‑detect the delimiter, auto‑pick note type, create a subdeck, and import in one dialog, with an option to launch the standard importer when needed.[11]

[1](https://github.com/tianshanghong/awesome-anki)
[2](https://forums.ankiweb.net/t/enhancement-request-use-github-as-addon-codebase-with-ankiweb-addon-page-copying-that-github-data/27546)
[3](https://github.com/topics/anki-addon)
[4](https://github.com/glutanimate/anki-addons-misc)
[5](https://github.com/pranavdeshai/anki-prettify)
[6](https://github.com/b3nj5m1n/enhancemainwindowthemes)
[7](https://github.com/ctrlaltwill/Ankimin)
[8](https://ankiweb.net/shared/info/871222788)
[9](https://www.reddit.com/r/Anki/comments/1k4yemm/ankimin_beautiful_minimal_card_templates_for_anki/)
[10](https://publish.obsidian.md/hub/02+-+Community+Expansions/02.05+All+Community+Expansions/Auxiliary+Tools/obsidianki4)
[11](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6472502/2b019e63-3281-4fdf-8a5f-a464cde16dcb/init.py)
