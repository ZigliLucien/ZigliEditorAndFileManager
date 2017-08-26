package ZEdit;

import java.awt.*;
import java.awt.event.*;

import javax.swing.*;


public class QuickDialog extends JDialog {
    //Class
    TPEditorX parent;
    JPanel southpanel;
    JPanel centerpanel;
    JButton verify;
    JButton close;
    String northLabelText;
    String confirmString;

    public QuickDialog(TPEditorX _parent, String _title, JPanel _centerpanel,
        String _confirmString, String _northLabelText) {
        // Constructor
        super(new JFrame(), _title);

        this.centerpanel = _centerpanel;
        this.parent = _parent;

        getContentPane().add("Center", centerpanel);

        southpanel = new JPanel();

        if (_confirmString != null) {
            this.confirmString = _confirmString;
            verify = new JButton(confirmString);
            verify.addActionListener(parent);
            verify.setBackground(Color.green);

            southpanel.add(verify);
        }

        close = new JButton("Close");
        close.setBackground(Color.orange);
        close.addActionListener(parent);

        southpanel.add(close);

        getContentPane().add("South", southpanel);

        if (_northLabelText != null) {
            this.northLabelText = _northLabelText;
            this.getContentPane().add("North", new JLabel(northLabelText));
        }

        if (parent.textfill != null) {
            this.addMouseListener(new MouseAdapter() {
                    public void mouseEntered(MouseEvent e) {
                        parent.textfill.requestFocus();
                    }
                });
        }

        pack();

        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        int locx = (scrsize.width) / 5;
        int locy = (scrsize.height) / 2;
        setLocation(locx, locy);
        setVisible(true);
    }

    public QuickDialog(TPEditorX _parent, String _title, JPanel _centerpanel,
        String _confirmString) {
        this(_parent, _title, _centerpanel, _confirmString, null);
    }

    public QuickDialog(TPEditorX _parent, String _title, JPanel _centerpanel) {
        this(_parent, _title, _centerpanel, null, null);
    }
}
