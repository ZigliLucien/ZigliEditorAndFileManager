package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.plaf.*;
import javax.swing.plaf.basic.*;
import javax.swing.text.*;
import javax.swing.text.html.*;

public class ZEditor extends JFrame implements ActionListener {

    public final static JDesktopPane daki = new JDesktopPane();

    static HashMap harry = new HashMap();
    static JMenuItem menuItem;
    static JMenuItem item;
    static JMenu bubu = new JMenu("Buffers");
    static JMenu rcrc = new JMenu("Recent Files");
    static JMenu vwvw = new JMenu("WebView");
    static JMenu help = new JMenu("Help");
    static JMenu bkmks = new JMenu("Bookmarks");
    static JMenuBar jiji = new JMenuBar();
    static final String[] utils = {
        "New Buffer", "Tile Windows", "One Window", "Maximize All", "Minimize All", "Quit"
    };
    static int buffnum;
    static final String[] views = { "Go Viewer", "Go Help" };
    public static boolean initializing = true;
    public static final JColorChooser chauncy = new JColorChooser();
	public    static int wdth;
	public    static int hght;
    static Dimension size;
   public static String[] fosizecmds;
	public    static String[] fofamcmds;
	public    static String[] fostylecmds;
	public    static final String[] fontfamilies = 
		GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames();
	public    static final String[] fontsizes = {
        "5", "6", "7", "8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "36", "48", "54", "72"
    };
	public    	static final String[] fontstyles = { "Bold", "Italic", "Bold-Italic", "Plain" };
    static final String[] directories = {
        "Quickwords", "Keywords", "ClickPads", "Data", "Dictionaries", "Keymaps", "TmpZefm"
    };
    static HTMLEditorKit kit = new HTMLEditorKit();
    static String printout;
    final JMenu utut = new JMenu("Utils");
    int[] strokes;
    int[] modifiers;

    static Vector<String> recentlist = new Vector<String>();
    static String[] recentfiles;

    /////////////////  CONSTRUCTOR  //////////////////////////
    public ZEditor(String args) throws Exception {

        String[] argv = args.split("\\s+");
                                new ZEditor(argv);
    }

    public ZEditor(String[] argv) throws Exception {

	System.setProperty("javax.xml.parsers.SAXParserFactory",
//			   "net.sf.saxon.aelfred.SAXParserFactoryImpl");
			   "com.sun.org.apache.xerces.internal.jaxp.SAXParserFactoryImpl");


	System.setProperty("javax.xml.transform.TransformerFactory",
		"net.sf.saxon.TransformerFactoryImpl");

        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();
        int localwdth = (int) Math.round(0.8 * scrsize.width);
        final int localhght = (int) Math.round(0.6 * scrsize.height);
        final int locx = (scrsize.width) / 10;
        final int locy = (scrsize.height) / 5;

        printout = "Running";

        if(!DBStart.DBChecked){ 
		new DBStart();
	              System.out.println("Initializing database through editor");
	}

        StyleSheet css = kit.getStyleSheet();
        Style style = css.getStyle(StyleContext.DEFAULT_STYLE);
        css.addRule(" a{ text-decoration: none; }");

        for (String dir : directories) {
            if (!new File(dir).exists()) {
                new File(dir).mkdir();
            }
        }

        putFile("properties/Modes.properties", "Modes.properties");
        putFile("properties/Extensions.properties", "Extensions.properties");
        putFile("properties/Mail.properties", "Mail.properties");
        putFile("properties/Editor.properties", "Editor.properties");
        putFile("properties/GetMail.properties", "GetMail.properties");
        putFile("properties/Web.properties", "Web.properties");

        putFile("data/Alphabets.data", "Data/Alphabets.data");
        putFile("data/Filefilters.data", "Data/Filefilters.data");
        putFile("data/Strings.data", "ClickPads/Strings.data");

        if (!new File("Data/bookmarks.data").exists()) {
            FileOutputStream fout = new FileOutputStream("Data/bookmarks.data");
            String startbkmks = "Add Bookmarks\nDelete Bookmarks\n";
            fout.write(startbkmks.getBytes());
            fout.flush();
            fout.close();
        }

         String[] bkmrx = TPEditorX.getJMenu("Data/bookmarks.data", false);


      for (String data : bkmrx) {
	if(data.trim().equals("Add Bookmarks") || data.trim().equals("Delete Bookmarks")) continue;
	            menuItem = new JMenuItem(data);
            	menuItem.setActionCommand(data+"***");
	            menuItem.addActionListener(this);
            	bkmks.add(menuItem);
        }

        fosizecmds = new String[fontsizes.length];

	Stack <String> stacc = new Stack<String>();

        for (String v : fontsizes) {
	stacc.push("f@nts@ze-" + v);
        }

	stacc.toArray(fosizecmds);
	stacc.clear();

        fofamcmds = new String[fontfamilies.length];

        for (String v : fontfamilies) {
            stacc.push("f@ntf@mily-" + v);
        }

	stacc.toArray( fofamcmds );
	stacc.clear();

        fostylecmds = new String[fontstyles.length];

        for (String v : fontstyles) {
            stacc.push("f@ntst@le-" + v);
        }

	stacc.toArray( fostylecmds );
	stacc.clear();

        if(new File("frames.tmp").exists()) {
		recentfiles = TPEditorX.getJMenu("frames.tmp", false);
		recentlist = new Vector<String>(Arrays.asList(recentfiles));
       for (String dataname : recentfiles) {
	            menuItem = new JMenuItem(dataname);
            	menuItem.setActionCommand(dataname+"***");
	            menuItem.addActionListener(this);
            	rcrc.add(menuItem);
        }
		}

        daki.setDragMode(JDesktopPane.OUTLINE_DRAG_MODE);
        daki.setBackground(new Color(0x0808b5));

        if (argv.length != 0) {
            String ttl = argv[0];

            for (int q = 1; q < argv.length; q++)
                ttl += (" " + argv[q]);
            
            this.setTitle(ttl);
        } else {
            this.setTitle("Zigli's Editor");
        }

        this.setContentPane(daki);
        setBufferMenu();

         daki.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (SwingUtilities.isRightMouseButton(e)) {
                        try {
                            Buffer buff = new Buffer();

                            if (!buff.empty) {
                                daki.add(buff);
                            }

                            tiling();
                        } catch (Exception ex) {
                            System.out.println(ex.getMessage());
                        }
                    }

                    if (SwingUtilities.isLeftMouseButton(e)) {
                        if (!initializing) {
                            tiling();
                        }

                        if (initializing) {
                            showSplash(locx, locy, localhght);
                        }
                    }
                }
            });
        strokes = new int[] { 0x4e, 0x54, 0x5a, 0x4d, 0x49, 0x51 };
        modifiers = new int[] {
                Event.CTRL_MASK, Event.CTRL_MASK | Event.ALT_MASK,
                Event.CTRL_MASK | Event.ALT_MASK,
                Event.CTRL_MASK | Event.ALT_MASK,
                Event.CTRL_MASK | Event.ALT_MASK, Event.CTRL_MASK
            };

        setMenu(utut, utils, strokes, modifiers);

        putFile("zeditor.help", "zeditor.help");

        String[] helpmenu = TPEditorX.getJMenu("zeditor.help");

        for (String v : helpmenu) {
            menuItem = new JMenuItem(v);
            help.add(menuItem);
        }

        strokes = new int[] { 0x55, KeyEvent.VK_SPACE };
        modifiers = new int[] { Event.CTRL_MASK, Event.SHIFT_MASK|Event.CTRL_MASK };

        setMenu(vwvw, views, strokes, modifiers);

        jiji.add(utut);
        jiji.add(bubu);
        jiji.add(rcrc);
        jiji.add(bkmks);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(vwvw);
        jiji.add(help);
        this.setJMenuBar(jiji);

            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
//         UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
            UIManager.put("ToolTip.background", new Color(0xf0,0xf0,0xaa));

        SwingUtilities.updateComponentTreeUI(this);

       this.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
		System.out.println("Exiting");
		DOps.stopMySQL();
                }
            });

        setLocation(locx, locy);
        setSize(localwdth, localhght);
        setVisible(true);

        showSplash(locx, locy, localhght);
    } 

    ////////////// MAIN //////////////
    public static void main(String[] args) throws Exception {
		new ZEditor(args);
    }

    ///////////////////////////////////////////////////////////
    ///////////////////// TILING //////////////////////////////
    ///////////////////////////////////////////////////////////
    public void tiling() {

        size = daki.getSize();
        wdth = size.width;
        hght = size.height;

	JInternalFrame[] jifa = daki.getAllFrames();

        if (jifa.length == 0) {
            return;
        }

        Vector<JInternalFrame> vjif = new Vector<JInternalFrame>();

         for (JInternalFrame jj : jifa) {

            final JInternalFrame jifi = jj;

            if (!jifi.isIcon()) {
                vjif.add(jifi);
            }

            jifi.addMouseListener(new MouseAdapter() {
                    public void mouseEntered(MouseEvent e) {
                        daki.setSelectedFrame(jifi);
                    }
                });
            jifi.addInternalFrameListener(new InternalFrameAdapter() {
                    public void internalFrameClosed(InternalFrameEvent e) {
                        setBufferMenu();
                    }
                });
        }

	JInternalFrame[] jif = new JInternalFrame[vjif.size()];
        	vjif.toArray(jif);

        if (jif.length == 0) {
            return;
        }

        int side = (int) Math.sqrt(jif.length);
        int rem = jif.length - (side * side);
        int shift = 0;

        if (rem == 0) {
            shift = 0;
        }

        if ((0 < rem) && (rem <= side)) {
            shift = 1;
        }

        if (side < rem) {
            shift = 2;
        }

        int rows = side + shift;
        int columns = side;

        if (jif.length == 3) {
            rows = 2;
            columns = 2;
        }

        int w = wdth / columns;
        int h = hght / rows;
        int x = 0;
        int y = 0;

        for (int s = 0; s < jif.length; s++) {
            int r = s % rows;
            int q = (s - r) / rows;
            int k = (columns * r) + q;

            ((JInternalFrame) jif[k]).reshape(q * w, r * h, w, h);

            if (((jif.length == 3) && (s == 2))) {
                ((JInternalFrame) jif[2]).reshape(0, h, wdth, h);
            }
        }
	setBufferMenu();
    }

    ///////////////////////////////////////////////////////////
    //////////////////// setBufferMenu ////////////////////////////
    ///////////////////////////////////////////////////////////

    public void setBufferMenu() {

        harry.clear();
        bubu.removeAll();

        for (JInternalFrame jifi : daki.getAllFrames()) {
            String localname = jifi.getTitle();
            harry.put(localname, jifi);
            menuItem = new JMenuItem(localname);
            menuItem.setActionCommand(localname + "**");
            menuItem.addActionListener(this);
            bubu.add(menuItem);
        }
    }

    ///////////////////////////////////////////////////////////
    ///////////////////// SET MENU /////////////////////////////
    ///////////////////////////////////////////////////////////
    public void setMenu(JMenu mimi, String[] words, int[] _strokes, int[] _modifiers) {
        for (int i=0; i < words.length; i++) {
            menuItem = new JMenuItem(words[i]);
            menuItem.addActionListener(this);
            menuItem.setAccelerator(KeyStroke.getKeyStroke(_strokes[i], _modifiers[i]));
            mimi.add(menuItem);
        }
    }

    /////////////////// RESOURCE WRAPPER /////////////////////////
    public static InputStream wrapper(String local) {
        try {
            if (new File(local).exists()) {
                return new FileInputStream(local);
            }
        } catch (Exception ee) {
        }

        return  ClassLoader.getSystemResourceAsStream(local);
    }

    /////////////////// COPY FROM RESOURCES /////////////////////
    public static void Copy(InputStream fromStream, String toFile) {
        try {
            FileOutputStream fout = new FileOutputStream(toFile);

            for (int q = 0; (q = fromStream.read()) != -1;)
                fout.write(q);

            fout.flush();
            fout.close();
        } catch (Exception exc) {
        }
    }

    /////////////////// SET FILE FROM RESOURCES /////////////////
    public static void putFile(String resource, String localfile) {
        if (!new File(localfile).exists()) {
            Copy(wrapper(resource), localfile);
        }
    }

    ////////////// SPACE CRUNCHER ///////////////////////////////
    public static String crunch(String in) {
        char[] z = in.toCharArray();

        String y = "";

        for (char v : z) {
            if (!Character.isSpaceChar(v)) {
                y += String.valueOf(v);
            }
        }

        return y;
    }

    ///////////////// SPLASH STARTUP ////////////////
    public void showSplash(int _locx, int _locy, int _localhght) {
        Graphics g = daki.getGraphics();

        g.setColor(Color.white);

        FontMetrics ftm = getFontMetrics(new Font("Times", Font.PLAIN, 24));
        g.setFont(new Font("Lucida Bright", Font.ITALIC, 36));

        try {
            Thread.sleep(850);

            g.drawString("********** Welcome to Zigli's Editor **********", _locx, _locy + 15);
            g.setFont(new Font("Lucida Sans", Font.PLAIN, 24));

            g.drawString("Right-Click anywhere in this window to start editing",
                _locx + 20, (int) Math.round(_locy + (_localhght / 8) + (4 * ftm.getHeight())));

            g.setFont(new Font("Lucida Sans", Font.PLAIN, 18));

            g.drawString("At the Open File dialog: Click 'Cancel' to get started with a default file ",
                _locx + 28, (int) Math.round(_locy + (_localhght / 8) + (6 * ftm.getHeight())));

            g.drawString("Click 'Go Help' on the WebView menu for Help home page",
                _locx + 28, (int) Math.round(_locy + (_localhght / 8) + (7 * ftm.getHeight())));

            g.drawString("Add bookmarks via the Bookmarks menu on an editor window",
                _locx + 28, (int) Math.round(_locy + (_localhght / 8) + (9 * ftm.getHeight())));

        } catch (Exception intex) {
        }
    }

    ////////////////// Commands and Actions //////////////////////
    public void actionPerformed(ActionEvent ae) {
        String cmd = ae.getActionCommand();

        size = daki.getSize();
        wdth = size.width;
        hght = size.height;

        if (cmd.equals("Go Help")) {
            try {
                new Helper(null, "HelpContents.html");
            } catch (Exception exc) {
            }
        }

        if (cmd.equals("Go Viewer")) {
            try {
                // Webby wally = new Webby();
                    WebCP wally = new WebCP();
                daki.add((JInternalFrame) wally);
                wally.moveToFront();
            } catch (Exception exc) {
            }
        }

        if (cmd.equals("New Buffer")) {
            try {
                Buffer bufi = new Buffer();

                if (!bufi.empty) {
                    bufi.setTitle(bufi.filename);
                    daki.add(bufi);
                    tiling();
                }
            } catch (Exception ex) {
                System.out.println(ex.getMessage());
            }

            return;
        }

        if (cmd.equals("Tile Windows")) {
            tiling();

            return;
        }

        if (cmd.equals("Maximize All") || cmd.equals("Minimize All")) {
            boolean min = false;

            if (cmd.equals("Minimize All")) {
                min = true;
            }

            try {
                for (JInternalFrame jj : daki.getAllFrames()) {
                    jj.setIcon(min);

                    if (!min) {
                        jj.reshape(0, 0, wdth, hght);
                    }
                }
            } catch (Exception ex) {
                return;
            }
        }

        if (cmd.equals("Next Window")) {
            daki.getSelectedFrame().moveToBack();
        }

        if (cmd.equals("One Window") || cmd.endsWith("**")) {
            JInternalFrame jaki = daki.getSelectedFrame();

            try {

                if (cmd.endsWith("***")) {

                      	    if(initializing) initializing = false;

   		 String filename = cmd.substring(0,cmd.indexOf("***"));
	try{  
		String filechosen = filename;

		  if(new File(filename).isDirectory()) {

		TPEditorX.filii.setCurrentDirectory(new File(filename));

	    	int returnVal = 0;
       
       		 returnVal = TPEditorX.filii.showOpenDialog(TPEditorX.filii.getParent());

       	if(returnVal == JFileChooser.APPROVE_OPTION) {	
try{
          	              filechosen = TPEditorX.webstyle(TPEditorX.filii.getSelectedFile().getCanonicalPath()); 

	}catch(Exception pathio){ filechosen =  "File Not Found"; return;}
	              
		}
	}
	                        TPEditorX newBuffer = new TPEditorX(filechosen, filechosen);
                            	daki.add(newBuffer);
                            	daki.setSelectedFrame(newBuffer);
			tiling();
			return;
		}catch(Exception e){}
	}

                if (cmd.endsWith("**")) {
                    String localname = cmd.substring(0, cmd.indexOf("*"));
                    JInternalFrame jframe = (JInternalFrame) harry.get(localname);

                    jframe.setIcon(false);
                    jaki = jframe;
                }

                if (cmd.equals("One Window")) {
                    for (JInternalFrame jj : daki.getAllFrames()) {
                        jj.setIcon(true);
                    }

                    jaki.setIcon(false);
                }

                if (jaki != null) {
                    jaki.reshape(0, 0, wdth, hght);
                    jaki.moveToFront();
                }
            } catch (Exception ex) {
                return;
            }

            return;
        }

        if (cmd.equals("Quit")) {
		System.out.println("Exiting");
		DOps.stopMySQL();
            this.dispose();
        }
    }

	static void doFrames() {

      if (recentlist.size() > 8) {
            recentlist.removeElementAt(recentlist.size() - 1);
        }

	String[] frms = new String[recentlist.size()];
	recentlist.toArray(frms);

try{
	PrintWriter pw = new PrintWriter(new FileWriter("frames.tmp"),true);

	for( String v  : frms) pw.println(v);

		pw.close();
	
	}catch(Exception ioe){System.out.println(ioe.getMessage());}

	}
}
