package ZEdit;

import NetsManager.Traxit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.text.html.*;


	public class Helper extends JFrame {
    static FileOutputStream ftw;
    JEditorPane jat;
    JTextField textin = new JTextField(
            "Welcome to Help for Zigli's Editor.               'q' exits.");
    JMenuBar jiji = new JMenuBar();
    String helpFileName;
    int locx;
    int locy;

    public Helper(String commandName, String _helpFileName)
        throws EmptyStackException {
        this.helpFileName = _helpFileName;

        if (commandName != null) {
            this.setTitle("Help for " + commandName);
        } else {
            setTitle("Zigli's Editor Help");
        }

        int localwdth = (int) Math.round(0.65 * ZEditor.wdth);
        int localhght = (int) Math.round(0.85 * ZEditor.hght);

        this.setSize(new Dimension(localwdth, localhght));

        Dimension dsize = this.getSize();
        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        locx = (scrsize.width - dsize.width) / 5;
        locy = (scrsize.height - dsize.height) / 2;
        setLocation(locx, locy);

        jat = new JEditorPane();

        JScrollPane scrap = new JScrollPane(jat,
                JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

        scrap.setMinimumSize(new Dimension(localwdth, localhght));
        scrap.setPreferredSize(new Dimension(localwdth, localhght));

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add("Center", scrap);
        getContentPane().add("South", textin);
        getContentPane().add("North", jiji);
        pack();
        setVisible(true);

        jat.addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {
                    if (e.getKeyCode() == KeyEvent.VK_Q) {
                        dispose();
                    }
                }
            });

        this.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
                    dispose();
                }
            });

        jat.setEditable(false);
        jat.setFont(new Font("Lucida Bright", Font.BOLD, TPEditorX.fntSize));

        jat.addHyperlinkListener(new HyperlinkListener() {
                public void hyperlinkUpdate(HyperlinkEvent e) {
                    if (e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
                        try {
                            String where = e.getURL().toString();
                            String which = where.substring(where.indexOf(":") +
                                    1);

                            InputStream file = ZEdit.ZEditor.wrapper(which);
                            ByteArrayOutputStream bar = new ByteArrayOutputStream();

                            for (int q = 0; (q = file.read()) != -1;)
                                bar.write(q);

                            bar.flush();

                            jat.setText(bar.toString());
                        } catch (Exception ex) {
                            System.out.println(ex.getMessage());
                        }
                    }

                    if (e.getEventType() == HyperlinkEvent.EventType.ENTERED) {
                        textin.setText(e.getURL().toString());
                    }
                }
            });

        try {
            InputStream file = ZEdit.ZEditor.wrapper("ServPak/html/" +
                    helpFileName);
            ByteArrayOutputStream bar = new ByteArrayOutputStream();

            for (int q = 0; (q = file.read()) != -1;)
                bar.write(q);

            bar.flush();

            ftw = new FileOutputStream("tmp.html");

            if (commandName != null) {
                new NetsManager.Traxit(bar.toByteArray(),
                    "ServPak/xsl/helpquery.xsl", commandName);
                new NetsManager.Traxit(NetsManager.Traxit.tabby,
                    "ServPak/xsl/showhelp.xsl", null);

                ftw.write(NetsManager.Traxit.tabby);
            } else {
                ftw.write(bar.toByteArray());
            }

            ftw.flush();
            ftw.close();

            jat.setPage("file:tmp.html");
        } catch (Exception exx) {
            System.out.println(exx.getMessage());
        }
    }
}
