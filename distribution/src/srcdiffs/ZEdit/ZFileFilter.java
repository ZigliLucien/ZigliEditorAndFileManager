package ZEdit;

import java.io.File;

import javax.swing.filechooser.*;


public class ZFileFilter extends javax.swing.filechooser.FileFilter {
    String[] acceptables;
    String filterDescription;

    public ZFileFilter(String[] _acceptables, String _filterDescription) {
        this.acceptables = _acceptables;
        this.filterDescription = _filterDescription;
    }

    public boolean accept(File f) {
        String ff = f.getName();

        if (f.isDirectory()) {
            return true;
        }

        for (String v : acceptables) {
            if (ff.endsWith("." + v)) {
                return true;
            }
        }

        return false;
    }

    public String getDescription() {
        return filterDescription;
    }
}
