package ZEdit;

import java.awt.*;
import java.awt.print.*;

import javax.swing.*;
import javax.swing.plaf.basic.*;
import javax.swing.text.*;


class PrintView extends BoxView {
    int _firstOnPage = 0;
    int _lastOnPage = 0;
    int _pageIndex = 0;

    public PrintView(Element elem, View root, int w, int h) {
        super(elem, Y_AXIS);
        setParent(root);
        setSize(w, h);
        layout(w, h);
    }

    public boolean paintPage(Graphics g, int hPage, int pageIndex) {
        if (pageIndex > _pageIndex) {
            _firstOnPage = _lastOnPage + 1;

            if (_firstOnPage >= getViewCount()) {
                return false;
            }

            _pageIndex = pageIndex;
        }

        int yMin = getOffset(Y_AXIS, _firstOnPage);
        int yMax = yMin + hPage;
        Rectangle rc = new Rectangle();

        for (int k = _firstOnPage; k < getViewCount(); k++) {
            rc.x = getOffset(X_AXIS, k);
            rc.y = getOffset(Y_AXIS, k);
            rc.width = getSpan(X_AXIS, k);
            rc.height = getSpan(Y_AXIS, k);

            if ((rc.y + rc.height) > yMax) {
                break;
            }

            _lastOnPage = k;
            rc.y -= yMin;
            paintChild(g, rc, k);
        }

        return true;
    }
}
