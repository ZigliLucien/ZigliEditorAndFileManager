package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.text.html.*;

public class Webby extends TPEditorX implements ActionListener {
    static URL homeURL;
    static URL currentURL;
    static URL tempURL;
    static String localaddr;
    public static String userdir = System.getProperty("user.dir");
    static JMenuItem menuItem;
    static JMenuItem item;
     InputStream GetIt;
     OutputStream FileIt;
    static URLConnection urla;
    static int counter = 0;
    static int gocounter = 0;
    static int filenum = 0;
    static int clength;
    static int nn;
    static int mm;
    static Properties webinfo = new Properties();
    static final Object[] options = {
        "DOWNLOAD ONLY", "DOWNLOAD and DISPLAY", "CANCEL"
    };
    static final String[] names = new String[] {
            "Back Button", "GO", "HOME", "Quit", "Home"
        };
    static QuickDialog dialog;
    static JPanel info;
    static JTextField address;
    static String currentDir;
    boolean running;
    JTextField textin = new JTextField("Welcome to the Web!");
    JEditorPane viewer = new JEditorPane();
    JPopupMenu popup = new JPopupMenu();
    JMenu mimi = new JMenu("Pauli");
    JMenu gogo = new JMenu("Go");
    JMenu hoho = new JMenu("Home");
    JMenu bobo = new JMenu("BookMarks");
    JMenu bkbk = new JMenu("Back");
    JMenuBar jiji = new JMenuBar();
    URL[] history = new URL[12];
    String fntstyle;
    String fntfamily;
    String fntsize;
    String fntweight;
    boolean addingaddr;
    boolean doedit;

    public Webby() throws Exception {
        super("WebViewer");

        userdir = userdir.replace('\\', '/');

        if (userdir.indexOf(":") > 0) {
            userdir = userdir.substring(userdir.indexOf(":") + 1);
        }

        try {
            localaddr = InetAddress.getLocalHost().getHostAddress();

            InputStream infile = new FileInputStream("Web.properties");
            webinfo.load(infile);
            homeURL = new URL(webinfo.getProperty("homeURLString"));

            ///////////////////////////////////////////////////////////////////////
            fntsize = webinfo.getProperty("FONTSIZE");

            if (webinfo.containsKey("FONTSTYLE")) {
                fntstyle = webinfo.getProperty("FONTSTYLE");
            }

            if (webinfo.containsKey("FONTWEIGHT")) {
                fntweight = webinfo.getProperty("FONTWEIGHT");
            }

            if (webinfo.containsKey("FONTFAMILY")) {
                fntfamily = webinfo.getProperty("FONTFAMILY");
            }

            /////////////////////////////////// SET CSS STYLES/////////////////////////////////
            StyleSheet css = ZEditor.kit.getStyleSheet();
            Style style = css.getStyle(StyleContext.DEFAULT_STYLE);

            if (fntweight != null) {
                css.addRule("body { font-weight : " + fntweight + "; }");
            }

            css.addRule("body { font-size : " + fntsize + "; }");

            if (fntstyle != null) {
                css.addRule("body { font-style : " + fntstyle + "; }");
            }

            if (fntfamily != null) {
                css.addRule("body { font-family : " + fntfamily + "; }");
            }

            ////////////////////////////////////////////////////////////////////
            ////////////////////////////////// END STYLES ///////////////////////////////////
        } catch (Exception wex) {
        }

        int[] strokes = new int[] { 0, 0, 0x48, 0x51 };
        int[] modifiers = new int[] { 0, 0, Event.CTRL_MASK, Event.CTRL_MASK };

        for (int i = 0; i < names.length; i++) {
            menuItem = new JMenuItem(names[i]);
            menuItem.setFont(new Font("Times", Font.PLAIN, 14));
            menuItem.setBackground(Color.cyan);
            menuItem.addActionListener(this);

            if (i < 2) {
                popup.add(menuItem);
            } else if (i < 4) {
                mimi.add(menuItem);
                menuItem.setAccelerator(KeyStroke.getKeyStroke(strokes[i],
                        modifiers[i]));
            } else {
                hoho.add(menuItem);
            }
        }

        getContentPane().add(popup);

        // MenuBar
        jiji.add(mimi);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(bkbk);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(gogo);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(bobo);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(hoho);

        try {
            ZEditor.putFile("data/Bookmax.data", "Data/Bookmax.data");

            String[] bkmrksfile = TPEditorX.getJMenu("Data/Bookmax.data", false);

            setBkmrx(bobo, bkmrksfile);

            int N = Math.min(bkmrksfile.length - 2, 12);

            for (int i = 0; i < 12; i++) {
                if (i < N) {
                    menuItem = new JMenuItem(bkmrksfile[i + 2]);
                }

                if (i >= N) {
                    menuItem = new JMenuItem("*");
                }

                menuItem.setFont(new Font("Times", Font.PLAIN, 12));
                menuItem.setBackground(Color.cyan);
                menuItem.addActionListener(this);
                gogo.add(menuItem);
            }
        } catch (Exception e) {
        }

        menuItem = new JMenuItem("Back Button");
        menuItem.setBackground(Color.gray);
        menuItem.addActionListener(this);
        bkbk.add(menuItem);

        JScrollPane editorScrollPane = new JScrollPane(viewer);
        editorScrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
        editorScrollPane.setPreferredSize(new Dimension(770, 550));
        editorScrollPane.setMinimumSize(new Dimension(500, 500));

        setTitle(webinfo.getProperty("title"));
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add("Center", editorScrollPane);
        getContentPane().add("South", textin);
        getContentPane().add("North", jiji);
        pack();
        setVisible(true);

        viewer.setEditable(false);

        ////////////////////////////// SHOW START PAGE ///////////////////////////
        try {
            viewer.setFont(new Font("Lucida Typewriter", Font.BOLD, 16));

            displayURL(homeURL);

            for (int i = 0; i < 12; i++) {
                history[i] = homeURL;
            }
        } catch (Exception e) {
            System.err.println("Couldn't find Home Page: " + homeURL);
        }

        ///////////////////////////////////////////////////////////////////////////
        viewer.addHyperlinkListener(new HyperlinkListener() {
                public void hyperlinkUpdate(HyperlinkEvent e) {
                    if (e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
                        String proto = e.getURL().getProtocol();

                        if (proto.equals("http") || proto.equals("file")) {
                            try {
                                displayURL(e.getURL());
                            } catch (Exception edu) {
                            }
                        } else {
                            mm = Download(e.getURL());
                        }
                    }

                    if (e.getEventType() == HyperlinkEvent.EventType.ENTERED) {
                        tempURL = e.getURL();
                        textin.setText(tempURL.toString());
                    }
                }
            });

        textin.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    try {
                        displayURL(new URL(textin.getText()));
                    } catch (Exception ex) {
                    } finally {
                        return;
                    }
                }
            });

        textin.addMouseListener(new MouseAdapter() {
                public void mouseClicked(MouseEvent e) {
                    if (!e.isControlDown() && !e.isShiftDown()) {
                        textin.setText(currentURL.toString());
                    }

                    if (SwingUtilities.isRightMouseButton(e)) {
                        try {
                            String curl = currentURL.toString();

                            if ((curl.indexOf("?") >= 0) &&
                                    (curl.indexOf("^") < 0)) {
                                curl = curl.substring(0, curl.indexOf("?"));
                            }

                            viewer.getDocument().putProperty(Document.StreamDescriptionProperty,
                                null);
                            displayURL(new URL(curl));
                        } catch (Exception ee) {
                        }
                    }
                }
            });

        viewer.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (SwingUtilities.isRightMouseButton(e)) {
                        if (!e.isShiftDown() && !e.isControlDown()) {
                            popup.show(e.getComponent(), e.getX(), e.getY());
                        }

                        if (e.isShiftDown() && !e.isControlDown()) {
                            doedit = true;
                        }
                    }

                    if (SwingUtilities.isLeftMouseButton(e)) {
                        try {
                            if (!e.isShiftDown() && e.isControlDown()) {
                                moveToBack();
                            }
                        } catch (Exception ex) {
                        }
                    }
                }
            });
    }

    //////////////////////// END CONSTRUCTOR //////////////////////////////
    ///////////////////// DISPLAY URL ////////////////////////
    public void displayURL(URL _url) throws Exception {
        final URL url = _url;
        currentURL = url;

        if ((url.toString().indexOf("^") > 0) ||
                (url.getFile().indexOf(".") < 0)) {
            currentDir = url.toString();
        }

        running = false;

        Thread t = new Thread() {
                public void run() {
                    try {
                        urla = url.openConnection();

                        if (urla.getContent() != null) {
                            textin.setText(url.toString());
                        } else {
                            System.out.println("URL not responding.");
                            textin.setText("URL not responding.");

                            return;
                        }

                        viewer.setEditable(false);

                        String hostt = url.getHost() + ":" + url.getPort();

                        boolean local = (url.getHost().equals("localhost") ||
                            InetAddress.getByName(url.getHost()).getHostAddress()
                                       .equals(localaddr));

                      if (doedit && !local) {
                            doedit = false;
                            doEdit(hostt, url);

                            return;
                        }

                        if (doedit && local) {
                            doedit = false;
                            doQuickEdit(hostt, url);

                            return;
                        }

                        String prename = url.getFile();
                        String name = (prename.indexOf("/") < 0) ? prename
                                                                 : prename.substring(1 +
                                prename.lastIndexOf("/"));

                        String ctype = urla.getContentType();

                        try {
                            if (ctype.equals("text/html") ||
                                    ctype.equals("text/plain")) {
                                System.out.println("Connecting to " +
                                    url.toString());
                                viewer.setPage(currentURL);
                            } else {
                                System.out.println("Content-type: " + ctype);

                                if (webinfo.containsKey(ctype)) {
                                    String xrun = webinfo.getProperty(ctype);
                                    GetIt = urla.getInputStream();

                                    String filename = userdir + "/TmpZefm/" +
                                        name;
                                    FileIt = new FileOutputStream(filename);

                                    for (int q = 0; (q = GetIt.read()) != -1;)
                                        FileIt.write(q);

                                    FileIt.flush();
                                    FileIt.close();

                                    if (ctype.startsWith("image")) {
                                        FileIt = new FileOutputStream(userdir +
                                                "/tmp.html");

                                        String page = "<html><body><img src=" +
                                            filename + "/></body></html>";
                                        FileIt.write(page.getBytes());
                                        FileIt.flush();
                                        FileIt.close();
                                        viewer.setPage("file:" + userdir +
                                            "/tmp.html");
                                    } else {
                                        runIt(xrun, filename);
                                        running = true;
                                    }
                                } else {
                                    textin.setText(
                                        "Content-type unknown. Caching page.");
                                    doPage(urla);

                                    return;
                                }
                            }
                        } catch (Exception eee) {
                            return;
                        }

                        int nextcounter = counter + 1;
                        counter = (nextcounter == 12) ? 0 : nextcounter;
                        history[counter] = url;
                        gocounter = counter;
                        setGoJMenu(url);
                    } catch (Exception e) {
                    } finally {
                        if (running) {
                            try {
                                URL udir = new URL(currentDir);
                                int nextcounter = counter + 1;
                                counter = (nextcounter == 12) ? 0 : nextcounter;
                                history[counter] = udir;
                                gocounter = counter;
                                setGoJMenu(udir);
                            } catch (Exception eurl) {
                            }
                        }

                        refresh();

                        return;
                    }
                }

                //run
            };

        //thread
        t.start();
        t.join(3000);
    }

    //////////////////////////// DOWNLOAD ///////////////////////////
    public int Download(URL url) {
        currentURL = url;

        String prename = url.getFile();
        String name = (prename.indexOf("/") < 0) ? prename
                                                 : prename.substring(1 +
                prename.lastIndexOf("/"));

        try {
            urla = url.openConnection();
            clength = urla.getContentLength();

            textin.setText(name + ": " + url + " has " + clength +
                " bytes of type " + urla.getContentType());

            if (clength < 0) {
                doPage(urla);

                return 1;
            }

            nn = JOptionPane.showOptionDialog(null, "Think About It",
                    "Downloading", JOptionPane.DEFAULT_OPTION,
                    JOptionPane.QUESTION_MESSAGE, null, options, options[2]);

            mm = (nn < 2) ? 1 : 2;

            switch (mm) {
            case (1):

                if (!new File("Downloads").exists()) {
                    new File("Downloads").mkdir();
                }

                GetIt = urla.getInputStream();

                String filename = "Downloads/" + name;
                FileIt = new FileOutputStream(userdir + "/" + filename);

                textin.setText("Downloading " + filename);

                try {
                    int qq = 0;

                    final Frame winji = new Frame("Downloading " +
                            url.toString());
                    TextArea outview = new TextArea("", 20, 70);

                    int[] loc = TPEditorX.locationSet(10, 7);

                    winji.setLocation(loc[0], loc[1]);
                    winji.setLayout(new BorderLayout());
                    winji.add(outview, "Center");

                    Panel penny = new Panel();
                    Button lali = new Button("CLOSE");
                    lali.setBackground(Color.yellow);

                    lali.addActionListener(new ActionListener() {
                            public void actionPerformed(ActionEvent e) {
                                winji.dispose();
                            }
                        });

                    penny.add(lali);

                    winji.addWindowListener(new WindowAdapter() {
                            public void windowClosing(WindowEvent e) {
                                winji.dispose();
                            }
                        });

                    winji.pack();
                    winji.setVisible(true);

                    for (int q = 0; (q = GetIt.read()) != -1;) {
                        qq++;
                        FileIt.write(q);

                        if ((qq % 100000) == 0) {
                            outview.append("     Downloaded " + qq +
                                " bytes from " + url.toString() + "\n");
                        }
                    }

                    FileIt.flush();
                    FileIt.close();

                    winji.add(penny, "South");
                    winji.pack();

                    outview.append("             DONE        \n");
                } catch (Exception eo) {
                }

                filenum++;

                String state = (filenum == 1) ? " file" : " files";

                textin.setText("DONE: " + filename + "  " + filenum + state +
                    " downloaded.");

                if (nn == 1) {
                    textin.setText(userdir + "/" + filename);
                    viewer.setPage(new URL("file:" + userdir + "/" + filename));
                }

                return nn;

            default:
                textin.setText("Cancelled.");

                return nn;
            }
        } catch (IOException ioe) {
            textin.setText(" Check this link.");

            return nn;
        }
    }

    //////////////////////// ACTIONS ///////////////////////////////////////
    public void actionPerformed(ActionEvent e) {
        boolean caught = false;
        viewer.setEditable(false);

        String called = e.getActionCommand();

        try {
            if (called.equals("Back Button")) {
                caught = true;
                gocounter = (gocounter > 0) ? (gocounter - 1) : 11;
                currentURL = history[gocounter];
                textin.setText(currentURL.toString());
                viewer.setPage(currentURL);
                history[gocounter + 1] = currentURL;
                setGoJMenu(currentURL);
            }

            if (called.equals("Add Bookmarks")) {
                AddBookmarks();
            }

            if (called.equals("Delete Bookmarks")) {
                DeleteBookmarks();
            }

            if (called.equals("Go Bookmarks")) {
                GoBookmarks();
            }

            if (called.equals("GO")) {
                caught = true;
                mm = Download(tempURL);
            }

            if (called.equals("HOME") || called.equals("Home")) {
                caught = true;
                displayURL(homeURL);
            }

            if (called.equals("Quit")) {
                this.dispose();
            }

            if (called.equals("Close")) {
                dialog.dispose();
            }

            if (called.indexOf("/") >= 0) {
                caught = true;
                displayURL(new URL(called));
            }

            if (!caught) {
                textin.setText(called);
            }
        } catch (Exception actione) {
        } finally {
            return;
        }
    }

    public void setGoJMenu(URL _currentURL) {
        gogo.remove(0);
        menuItem = new JMenuItem(_currentURL.toString());
        menuItem.setFont(new Font("Times", Font.PLAIN, 12));
        menuItem.setBackground(Color.cyan);
        menuItem.addActionListener(this);
        gogo.add(menuItem);
    }

    //////////////////////////////////////////////////////////////
    void AddBookmarks() { //////////////////// AddBookmarks ///////////////////////

        //////////////////////////////////////////////////////////////
        address = new JTextField(currentURL.toString());

        info = new JPanel();
        info.setLayout(new GridLayout(2, 1));
        info.add(new JLabel("Address              "));
        info.add(address);

        dialog = new QuickDialog(this, "Adding bookmark", info, "Go Bookmarks");

        addingaddr = true;
    }

    //////////////////////////////////////////////////////////////
    void DeleteBookmarks() { ///////////////////////////// DeleteBookmarks ///////////////////////

        //////////////////////////////////////////////////////////////
        address = new JTextField(currentURL.toString());

        info = new JPanel();
        info.setLayout(new GridLayout(2, 1));
        info.add(new JLabel("Address              "));
        info.add(address);

        dialog = new QuickDialog(this, "Deleting bookmark", info,"Go Bookmarks");

        addingaddr = false;
    }

    //////////////////////////////////////////////////////////////
    void GoBookmarks() { ///////////////////////////// GoBookmarks ///////////////////////

        //////////////////////////////////////////////////////////////
        try {
            if (addingaddr) {
                PrintWriter prtw = new PrintWriter(new FileWriter(
                            "Data/Bookmax.data", true), true);
                prtw.print(address.getText() + "\n");
                prtw.close();
            } else {
                String newbkms = "";
                FileInputStream bkms = new FileInputStream("Data/Bookmax.data");
                byte[] bbb = new byte[bkms.available()];
                bkms.read(bbb);

                StringTokenizer stin = new StringTokenizer(new String(bbb), "\n");

                while (stin.hasMoreTokens()) {
                    String v = stin.nextToken();

                    if (!v.equals(address.getText())) {
                        newbkms += (v + "\n");
                    }
                }

                PrintWriter prtww = new PrintWriter(new FileWriter(
                            "Data/Bookmax.data"), true);
                prtww.print(newbkms);
                prtww.close();
            }

            String[] bkmrx = TPEditorX.getJMenu("Data/Bookmax.data", false);

            bobo.removeAll();
            setBkmrx(bobo, bkmrx);
        } catch (IOException ioe) {
        } finally {
            dialog.dispose();
        }
    }

    void setBkmrx(JMenu _bobo, String[] bkmrks) {
        for (int i = 0; i < bkmrks.length; i++) {
            menuItem = new JMenuItem(bkmrks[i]);
            menuItem.setFont(new Font("Times", Font.PLAIN, 12));
            menuItem.setBackground(Color.cyan);
            menuItem.addActionListener(this);
            _bobo.add(menuItem);
        }
    }

    public void runIt(String _runcommand, String _currentfile) {
        runIt(_runcommand + " " + _currentfile);
    }


	//////////////// RunIt ///////////////

    public void runIt(String _shellcommand) {
        shellcommand = _shellcommand;
        showoutput = new JFrame("Shell Output");

        JTextArea outview = new JTextArea("", 25, 70);
        JScrollPane scrollpane = new JScrollPane(outview,
                JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

        int[] loc = locationSet(10, 7);
        showoutput.setLocation(loc[0], loc[1]);

        showoutput.getContentPane().add(scrollpane);
        showoutput.pack();

        showoutput.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
                    showoutput.dispose();

                    return;
                }
            });

        try {
            Runtime local = Runtime.getRuntime();
            Process out = local.exec(shellcommand);
            InputStream infoout = out.getInputStream();
            InputStream errout = out.getErrorStream();

            ByteArrayOutputStream stdout = new ByteArrayOutputStream();
            ByteArrayOutputStream errorout = new ByteArrayOutputStream();

            for (int qq = 0; (qq = infoout.read()) != -1;) {
                stdout.write(qq);
            }

            for (int qq = 0; (qq = errout.read()) != -1;) {
                errorout.write(qq);
            }

            stdout.flush();
            errorout.flush();

            outview.setText("");
            outview.append(errorout.toString() + "\n\n");

            outview.append(stdout.toString());
            out.waitFor();

            outview.append("\n\n       DONE     \n\n");

            if (shell) {
                dialog.dispose();
            }
        } catch (Exception e) {
            showoutput.setVisible(true);
        } finally {
            return;
        }
    }


//////////////////////// DoPage /////////////////////////////////////

    void doPage(URLConnection _urla) {
        try {
            String filename = userdir + "/TmpZefm/tmpurl.html";
            GetIt = _urla.getInputStream();
            FileIt = new FileOutputStream(filename);

            for (int q = 0; (q = GetIt.read()) != -1;)
                FileIt.write(q);

            FileIt.flush();
            FileIt.close();
            viewer.setPage(new URL("file:" + filename));
        } catch (Exception e) {
            return;
        }
    }

///////////////////////////////// DoEdit //////////////////////////////////

    public  void doEdit(String _hostt, URL _url)
        throws Exception {
        String urline = _url.toString();
        String filel = urline.substring(urline.indexOf("//") + 2);
        filel = filel.substring(filel.indexOf("/"));

        TPEditorX.hosttext = _hostt;
        TPEditorX.filetext = filel;
        GetIt = urla.getInputStream();

        String fileout = filel.replace('/', '_');

        if (!new File("RemoteFiles").exists()) {
            new File("RemoteFiles").mkdir();
        }

        fileout = "RemoteFiles/" + _url.getHost() + fileout;
        System.out.println("downloading " + fileout);

        FileIt = new FileOutputStream(userdir + "/" + fileout);

        for (int q = 0; (q = GetIt.read()) != -1;) FileIt.write(q);

        FileIt.flush();
        FileIt.close();

        TPEditorX newBuffer = new TPEditorX(filel, fileout);

        ZEditor.daki.add(newBuffer);

        ZEditor zak = (ZEditor) newBuffer.getTopLevelAncestor();
        zak.tiling();
    }


////////////////////// DoQuickEdit //////////////////////

    public  void doQuickEdit(String _hostt, URL _url)
        throws Exception {
        String urline = _url.toString();
        String filel = urline.substring(urline.indexOf("//") + 2);
        filel = filel.substring(filel.indexOf("/"));

        TPEditorX.hosttext = _hostt;
        TPEditorX.filetext = filel;
        GetIt = urla.getInputStream();

        String fileout = filel.replace('/', '_');

        if (!new File("RemoteFiles").exists()) {
            new File("RemoteFiles").mkdir();
        }

        fileout = "RemoteFiles/" + _url.getHost() + fileout;
        System.out.println("downloading " + fileout);

        FileIt = new FileOutputStream(userdir + "/" + fileout);

        for (int q = 0; (q = GetIt.read()) != -1;)
            FileIt.write(q);

        FileIt.flush();
        FileIt.close();
	
	new NetsManager.QuickEditor(fileout);

       
    }

}