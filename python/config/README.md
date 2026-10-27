ZEFM configuration (UTF-8 JSON)

zefm.json: general settings; load with zefm.config.load(path).
keyboard.json: optional command-label -> shortcut overrides. Empty mapping retains
all shortcuts transcribed from TPEditorX.java. Set a command to null to unbind it.
No arbitrary command names or duplicate bindings are accepted.

To migrate a Java properties file:
  python3 -m zefm.config_import old.properties config/imported.json
The importer preserves property names and values, but imported keys are NOT
silently interpreted as editor settings. Review and map them deliberately.
Java XML/XSLT documents remain XML/XSLT.
