# ZEFM Python port

This branch preserves the original Java sources on `master` and provides an integration point for the Python rewrite.

## Proposed layout

- `python/`: Python package (`zefm/`), tests, configuration, migration scripts and documentation.
- Original `ZEdit/`, `NetsManager/` and other Java source directories remain intact.

## Import the tested v40 release

Extract `ZEFM_process_scaffold_v40.zip` into the `python/` directory, without including local runtime data. From the repository root:

```sh
mkdir -p python
unzip -q ~/Downloads/ZEFM_process_scaffold_v40.zip -d python
python3 -m unittest discover -s python/tests -v
cd python && python3 -m zefm.editor.gui.tk_editor
```

Depending on test imports, run the tests from within `python/`:

```sh
cd python
python3 -m unittest discover -s tests -v
```

## Private data must remain local

Do not commit MyISAM databases, downloaded email, message bodies, private notes, user dictionaries recovered from personal databases, tokens, or personal session preferences. Import programs and sample fixtures are appropriate for version control.

Changes should be reviewed on this branch before merging into `master`.
