package ZEdit;

import java.awt.*;
import java.awt.print.*;

import javax.swing.*;
import javax.swing.plaf.basic.*;
import javax.swing.text.*;


/*
Wrapper taken from
7/99 Marty Hall, http://www.apl.jhu.edu/~hall/java/
his PrintUtilities.

Rendering to graphics is taken from the WordProcessor application by
Matthew Robinson and Pavel Vorobiev in online version of Chapter 22
of their book Swing, published by Manning Publications Co.

Much thanks to these folks for making their code available to all.
*/
public class ZPrint implements Printable {
    JTextPane buffer;
    PrintView _printView;

    public ZPrint(JTextPane _buffer) {
        this.buffer = _buffer;
        printit();
    }

    public void printit() {
        PrinterJob printJob = PrinterJob.getPrinterJob();
        printJob.setPrintable(this);

        if (printJob.printDialog()) {
            try {
                printJob.print();
            } catch (PrinterException pe) {
                System.out.println("Error printing: " + pe);
            }
        }
    }

    public int print(Graphics pg, PageFormat pageFormat, int pageIndex)
        throws PrinterException {
        pg.translate((int) pageFormat.getImageableX(),
            (int) pageFormat.getImageableY());

        int wPage = (int) pageFormat.getImageableWidth();
        int hPage = (int) pageFormat.getImageableHeight();

        pg.setClip(0, 0, wPage, hPage);

        if (_printView == null) {
            BasicTextUI btui = (BasicTextUI) buffer.getUI();
            View root = btui.getRootView(buffer);
            _printView = new PrintView(buffer.getDocument()
                                             .getDefaultRootElement(), root,
                    wPage, hPage);
        }

        boolean bContinue = _printView.paintPage(pg, hPage, pageIndex);

        if (bContinue) {
            return PAGE_EXISTS;
        } else {
            _printView = null;

            return NO_SUCH_PAGE;
        }
    }
}
