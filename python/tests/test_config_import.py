import unittest, tempfile
from pathlib import Path
from zefm.config_import import import_properties

class ImportTests(unittest.TestCase):
    def test_basic(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.properties'; b=Path(d)/'b.json'
            a.write_text('name=ZEFM\nlabel=\\u0153\n',encoding='ascii')
            self.assertEqual(import_properties(a,b),{'name':'ZEFM','label':'œ'})
