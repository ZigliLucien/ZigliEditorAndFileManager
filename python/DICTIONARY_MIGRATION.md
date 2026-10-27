# ZEFM v38 — original dictionaries, keymap viewer, and safe migration

## Two different language facilities

The original Java `Alphabet.java` has two independent mechanisms:

1. **Keyboard layout:** `Keymaps/*.keymap` maps Alt, Alt+Shift, or Alt+Meta key chords to Unicode characters. The v36+ Python editor already supports these chords. **Language → Show Keymap / Keyboard Reference...** (v38) provides a searchable visual reference, clipboard copy, direct Unicode insertion, and an activation button; no external keyboard-layout tool is required for the popup itself.
2. **Lexical dictionaries:** MySQL `dictionaries(lang,word,data)` stores an original word and translation text. The `data` string may contain comma-separated translations. **Language → Look Up Word in Dictionary...** (v38) looks up the selected word or the Unicode word at the cursor, including Hebrew combining marks.

The separate `dictionaries/fr.json` and `dictionaries/yi.json` files in the installation contain *shortcut expansions* (e.g. `coeur` → `cœur`), not legacy lexical dictionary entries. They remain unchanged.

## Recovering the original lexical dictionaries

`ZEFMdb.zip` contains MyISAM files (`dictionaries.frm`, `.MYD`, `.MYI`); it is **not** a JSON export and cannot be passed directly to the importer. Recover the database in an isolated and compatible MySQL/MariaDB migration environment first, following `NOTES_AND_DB_MIGRATION.md`. Keep the original ZIP and a backup unchanged. The Python editor itself does not require MySQL.

From that *separately restored* database, export the dictionary table:

```sh
python3 -m pip install pymysql
python3 -m zefm.storage.export_legacy_tables dictionaries ~/dictionaries-export.jsonl --database ZEFMdb --user YOUR_DB_USER
```

The exporter prompts for a password and checks record counts. **Do not publish your export:** it can contain private data. Next, inspect how records map to language files without modifying anything:

```sh
python3 -m zefm.storage.import_legacy_dictionaries ~/dictionaries-export.jsonl --dry-run
```

Then import:

```sh
python3 -m zefm.storage.import_legacy_dictionaries ~/dictionaries-export.jsonl
```

Optional `--output-dir /safe/path` changes the destination. Existing dictionary files are **not overwritten** unless you specify `--force`, and input validation precedes writes. Files are created with private `0600` permissions. As with any multi-file import, a filesystem error during final replacement can leave some language files updated; retain the original export for recovery.

The default location is `~/.local/share/zefm/dictionaries/` (or `$XDG_DATA_HOME/zefm/dictionaries/`). One UTF-8 **JSON Lines** file is written per language, such as `fr.jsonl`, `yi.jsonl`. Source records retain `lang`, `word`, and `data` verbatim. `French` and `Yiddish` normalize to the filenames `fr` and `yi` respectively; other safe language names are converted to lowercase filenames. Duplicate words and comma-separated translations are never collapsed. This is a streaming lookup format, so no separate database is needed.

## Keymap menu on Linux and Mac

In the editor, choose **Language → Show Keymap / Keyboard Reference...**. Pick a layout from the dropdown. You can filter by key chord, glyph, or Unicode name, double-click a row to insert its character, copy a full reference, or click **Use this keymap** to activate Alt chords in the current buffer. `System keyboard (off)` disables custom chords. Input mappings and dictionary language selections remain independent.

On macOS, the operating system's Option-key handling may conflict with ZEFM Alt mappings. The reference window's **Insert selected** action works without Alt. On X11, your window manager may intercept Alt chords. No keyboard interception happens when the keymap is off.

## Verification boundary

The conversion pipeline is implemented and tested using representative UTF-8 records (French, Yiddish with combining marks, duplicate words, invalid exports), but **the complete historical MyISAM database has not yet been restored or migrated**. Thus the lexical dictionary UI will report no entry until the local conversion is performed. The GUI smoke tests run under Xvfb; run interactive checks on your Slackware and Mac installations.
