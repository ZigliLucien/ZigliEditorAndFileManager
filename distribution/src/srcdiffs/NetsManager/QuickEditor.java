package NetsManager;

import ZEdit.*;


import java.awt.*;
import java.awt.event.*;
import java.awt.font.*;

import java.io.*;

import java.lang.reflect.*;

import java.net.*;
import java.util.*;
import java.util.regex.*;

import javax.swing.*;
import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.undo.*;

import java.sql.*;


public class QuickEditor extends JFrame implements ActionListener,
    UndoableEditListener {
    // Class 
              JScrollPane jazz;
    static JFrame showoutput;
    static JDialog smlx;
    static JTextField textfill;
    static JTextField textfill2;
    static JTextField nickname;
    static JTextField address;
    static JTextField instring;
    static JTextField outstring;
    static JTextField hostfield;
    static JTextField filefield;
    static JTextField upfield;
    static JPasswordField pwfield;
    static JTextField pwordsfield;
    static JTextField portfield;
    static JTextField userfield;
    static JPanel sml;
    static JPanel info;
    static QuickDialog dialog;
    static String outfile;
             String dir = System.getProperty("user.dir");
    static String lookfor;
    static String replaced;
    static String hosttext = "";
    static String uphosttext = "";
    static String filetext = "";
    static String upfiletext = "";
    static String uptext = "";
    static String picturetext = "";
    static String pwtext = "";
    static String pwordstext = "";
    static String porttext = "";
    static String usertext = "";
    static String mailto;
    static String subject;
    static String mailFrom;
    static String mailer;
    static String fileattachment = "";
    static String unpacked = "";
    static String packed = "";
              String diff1="";
              String diff2="";
    static int fcolor;
    static int bcolor;
    static int kbSize;
    static int direct;
    static int fntSize;
    static JButton[] letters;
    static JButton verify;
    static JButton cancel;
    static JMenuItem menuItem;
    static JMenuItem item;
    static Vector searchlist = new Vector();
    public static final JColorChooser chance = ZEditor.chauncy;
    static String[] actcmds;
    static int[] strokes;
    static int[] modifiers;
    static final int ctrl = Event.CTRL_MASK;
    static final int alt = Event.ALT_MASK;
    static final int shft = Event.SHIFT_MASK;
    static String[] bkmrx;
             StringBuilder chary;
    static int howmuchusyms;
    static Stack<String> tries;
    static String[] completions;
    static StreamTokenizer stro;
    public static final Properties edinfo = new Properties();
    static Properties extinfo = new Properties();
    static Properties modesinfo = new Properties();
    static Properties mailinfo = new Properties();
    static Properties getmailinfo = new Properties();
    static String[] modes;
    static String mode;
    static String extension;
    static final String[] filechoices = {
        "Open", "Save", "Save As", "DocSave", "Revert File", "Print", "Quit"
    };
    static final String[] edits = {
        "Refresh Buffer", "Clear", "Redo", "Undo", "Line Numbers", "Find",
        "Replace", "Continue Find or Replace", "Toggle ClickPad"
    };
    static String[] quickwords;
    static final String[] runs = {
        "Shell", "Compile", "Close Shell Window", "QuickMail", "Get Mail",
        "Trace"
    };
    static final String[] addem = {
        "Add new email address", "Add new quickwords", "Delete quickwords",
        "Remove address", "Reload quickwords", "Diff Files","START",
        "Remote Save", "Remote Edit", "Upload", "FTP Get File",
        "Toggle Character Paragraph Attributes", "Font Color", "Print",
        "Add Picture", "UnPack64", "Pack64"
    };
    static String startup;
    static String stylefile;

	String title;

    static boolean addingaddr;
    static boolean shell;
    static boolean jxml;
    static boolean open;
    static boolean replaceString;

    static Point pt;
    static SoftBevelBorder emborder = new SoftBevelBorder(BevelBorder.LOWERED);
    static BevelBorder bborder = new BevelBorder(BevelBorder.LOWERED,
            Color.yellow, Color.yellow);
    static ZEdit.Commands runapp;

    static Stack <KeyEvent> makStak;
    static KeyEvent[] kev;
   
    static String[] syml;
    static String[] texsyml;

		                 int linenum;

     BufferedReader bin;
   static DataInputStream din;

    JTextPane writer = new JTextPane();
    JTextField fillin = new JTextField(40);
    JTextField currentinfo = new JTextField("Welcome to Zigli's Editor");
    JPanel textin = new JPanel();
    JPanel southpanel = new JPanel();
    String currentfile;
    String currenttmp;
    String outname;
    String shellcommand;
    int fontSize;
    String fontFamily;
    String fontStyle;
    String fntstyle;
    int fStyle;
    Font currentFont;
    JLabel fontInfo = new JLabel();
    JMenu fifi = new JMenu("File");
    JMenu eded = new JMenu("Edit");
    JMenu qwqw = new JMenu("Quickwords");
    JMenu qwpop = new JMenu("Quickwords");
    JMenu adad = new JMenu("Utils");
    JMenu ruru = new JMenu("Run");
    JMenu gogo = new JMenu("Go");
    JMenu emem = new JMenu("SendEMail");
    JMenu geteml = new JMenu("GetEMail");
    JMenu bookmarks = new JMenu("Bookmarks");
    JMenu symsym = new JMenu("MLSyms");
    JMenu textex = new JMenu("TeXSyms");
    JMenu sympop = new JMenu("MLSyms");
    JMenu texpop = new JMenu("TeXSyms");
    JMenu usym = new JMenu("UniSyms");
    JMenu ldsym = new JMenu("UniBlox");
    JMenuBar jiji = new JMenuBar();
    JMenu txtx = new JMenu("Text");
    JMenu txtxpop = new JMenu("Text");
    JMenu noto = new JMenu("Notes");
    JMenu momo = new JMenu("Modes");
    JMenu momopop = new JMenu("Modes");
    JMenu dada = new JMenu("Data");
    JMenu dapop = new JMenu("Data");
    JPopupMenu unipop = new JPopupMenu();
    JMenu lingling = new JMenu("Alphabet");
    JMenu alal = new JMenu("English");
    JMenu alapop = new JMenu("English");
    JMenu padpop = new JMenu("Pad");
    JMenu fofam = new JMenu("FontFamily");
    JMenu fosize = new JMenu("FontSize");
    JMenu fostyle = new JMenu("FontStyle");
    JMenu fontms = new JMenu("Fonts");
    JMenu mailmail = new JMenu("EMail");
    JMenu subusym1;
    JMenu subusym2;
    JComboBox findList;
    HashMap unimenus = new HashMap();
    HashMap lettermap = new HashMap();
    HashMap harry = new HashMap();
    public static JFileChooser filii = new JFileChooser();
    JDialog jodi;
    int lineco = 0;
    int position = 0;
    int index;
    String scratch;
    String localword;
    String alph;
    String srchwd;
    boolean language;
    boolean dictionary;
    boolean bold = true;
    boolean italic;
    boolean charset = true;
    boolean helping;
    boolean showpads = true;
    boolean goApp;
    String[] keywords = {  };
    Modes mod;
    String cmd;
    boolean notmp;
    boolean numson;
    boolean traceon;
    boolean completing;
    int mathmode = 0;
    int mathflip = 1;
    int bracecount = 0;
    int parencount = 0;
    int bracecolor;
    int parencolor;
    Stack <Color> colorstack = new Stack<Color>();
    boolean controlsq;
    boolean loadmlsyms;
    SimpleAttributeSet attrs = new SimpleAttributeSet();
    UndoManager undo = new UndoManager();
    boolean makemak;
    boolean holding;
    boolean propsdata;
    boolean styled;
    String filechosen;

    SMailClient smc;
    Pattern eol;

    static final int[] header = new int[]{-84,-19,0,5,115,114,0,38,106,97,118,97};

    //////////////////////////////////////////////////////////////////
    ////////////////////// CONSTRUCTOR: title ////////////////////////
    //////////////////////////////////////////////////////////////////
    public QuickEditor(String _title) throws Exception {
        //Constructor	


	if(_title.contains("!X!") ) {
		String[] input = _title.split("!X!");
		          linenum = Integer.parseInt(input[0]);
      		this.title = input[1];
		System.out.println("Editing "+title+" at line "+linenum);
	}else{
		          linenum = 0;
		this.title = _title;
		System.out.println(title);
	}

        	new JFrame(title);


	Class cappi = Class.forName("NetsManager.QuickEditor");

            Method[] moti = cappi.getDeclaredMethods();

	eol = Pattern.compile("\n");

        for (Method v : moti)
            harry.put(v.getName(), v);

        try {
            InputStream infile1 = new FileInputStream("Mail.properties");
            InputStream infile2 = new FileInputStream("Modes.properties");
            InputStream infile3 = new FileInputStream("Extensions.properties");
            InputStream infile4 = new FileInputStream("Editor.properties");

            mailinfo.load(infile1);
            modesinfo.load(infile2);
            extinfo.load(infile3);
            edinfo.load(infile4);

            if (new File("GetMail.properties").exists()) {
                InputStream infile5 = new FileInputStream("GetMail.properties");
                getmailinfo.load(infile5);
            }

            System.out.println("Loaded");
        } catch (IOException ioex) {
            System.out.println(ioex.getMessage());
        }

        mailFrom = mailinfo.getProperty("~~_from");
        mailer = mailinfo.getProperty("~~_by");

        String bkcolorin = edinfo.getProperty("BACKGROUNDCOLOR");
        String fgcolorin = edinfo.getProperty("FOREGROUNDCOLOR");
        String fntsize = edinfo.getProperty("FONTSIZE");
        fntstyle = null;

        fontFamily = "Lucida Typewriter";

        String mathslashin = edinfo.getProperty("MATHSLASH");
        String slashin = edinfo.getProperty("SLASH");
        String dollarin = edinfo.getProperty("DOLLAR");
        String mthmodein = edinfo.getProperty("MATHMODE");
        final int mathslash = rgb(mathslashin);
        final int slash = rgb(slashin);
        final int dollar = rgb(dollarin);
        final int mthmode = rgb(mthmodein);

        if (edinfo.containsKey("FONTSTYLE")) {
            fntstyle = edinfo.getProperty("FONTSTYLE");
        }

        if (edinfo.containsKey("FONTFAMILY")) {
            fontFamily = edinfo.getProperty("FONTFAMILY");
        }

        if (edinfo.containsKey("INITDIR")) {
            dir = edinfo.getProperty("INITDIR");
        }

        if (edinfo.containsKey("CLICKPADS")) {
            if (edinfo.getProperty("CLICKPADS").equals("off")) {
                showpads = false;
            }
        }

        if (edinfo.containsKey("LOADMLSYMBOLS")) {
            if (edinfo.getProperty("LOADMLSYMBOLS").equals("yes")) {
                loadmlsyms = true;
            }
        }

        if (edinfo.containsKey("LOADUSYMBOLS")) {
            howmuchusyms = Integer.parseInt(edinfo.getProperty("LOADUSYMBOLS"));
        }

        if ((fntsize != null) && !fntsize.equals("default")) {
            fontSize = Integer.parseInt(fntsize);
        } else {
            fontSize = 18;
        }

        fntSize = fontSize;
        bcolor = -1;
        fcolor = -1;

        if ((bkcolorin != null) && !bkcolorin.equals("default")) {
            bcolor = rgb(bkcolorin);
        }

        if ((fgcolorin != null) && !fgcolorin.equals("default")) {
            fcolor = rgb(fgcolorin);
        }

       if (bcolor == -1) {
            writer.setBackground(new Color(0x80, 0x80, 0x80));
            writer.setSelectedTextColor(new Color(0x80, 0x80, 0x80));
        } else {
            writer.setBackground(new Color(bcolor));
            writer.setSelectedTextColor(new Color(bcolor));
        }

        if (fcolor == -1) {
            writer.setForeground(Color.white);
            writer.setSelectionColor(Color.white);
        } else {
            writer.setForeground(new Color(fcolor));
            writer.setSelectionColor(new Color(fcolor));
        }

        fStyle = Font.BOLD;

        if (fntstyle != null) {
            fStyle = Font.PLAIN;
            bold = false;
        }

        currentFont = new Font(fontFamily, fStyle, fontSize);
        writer.setFont(currentFont);

        setAttrs(); // Sets default font attributes    

        unipop.add(fontInfo);
        unipop.add(momopop);
  
        cmd = "Open";
        setProps(mailinfo, emem, true); // this sets the menu emem
        setProps(getmailinfo, geteml, true); // this sets the menu 
        modes = setProps(modesinfo, false); //sets modes menu
        setProps(extinfo, false); //prepares extension list

        //
        setJMenu(momo, modes);
        setJMenu(momopop, modes);
        //
        strokes = new int[] { 0x78, 0x70, 0x72, 0x70, 0x78, 0x50, 0x51 };
        modifiers = new int[] { 0, 0, 0, shft, ctrl, ctrl, ctrl, ctrl };

        setJMenu(fifi, filechoices, strokes, modifiers);

        strokes = new int[] { 0x76, 0x77, 0x75, 0x74, 0x71, 0x53, 0x52, 0x52, 0x46 };
        modifiers = new int[] { 0, 0, 0, 0, ctrl, ctrl, ctrl | shft, ctrl, ctrl };

        setJMenu(eded, edits, strokes, modifiers);

        strokes = new int[] { 0x5a, 0x73, 0x57, 0x4d, 0x4d, 0x4f };
        modifiers = new int[] { ctrl | shft, 0, ctrl, ctrl, ctrl | shft, ctrl };

        setJMenu(ruru, runs, strokes, modifiers);

        strokes = new int[] {
                0x41, 0x42, 0x43, 0x44, 0x45, 0x44, 0x47, 0x7a, 0x7b, 0x7a, 0x7b,
                0x50, 0x43, 0x73, 0x77, 0x79, 0x79
            };
        modifiers = new int[] {
                ctrl | shft, ctrl, ctrl | shft, ctrl, ctrl, ctrl | shft, ctrl, 0, 0, ctrl,
                ctrl, ctrl | shft, ctrl | alt, ctrl, ctrl, ctrl, ctrl | shft
            };

        setJMenu(adad, addem, strokes, modifiers);
        addHelp(adad, "Utils");

        if (edinfo.containsKey("DEFAULTALPHABET")) {
            alph = edinfo.getProperty("DEFAULTALPHABET");

            if (!alph.equals("English")) {
                mode = "Lang";
            }
        } else {
            alph = "English";
            mode = "Text";
        }

        setQuickwords(); // this sets the menu qwqw
        addHelp(qwqw, "Quickwords");

        jiji.add(fifi);
        jiji.add(eded);
        jiji.add(ruru);
        jiji.add(qwqw);

        // Setting menus	
        // Setting the go menu
        String dataname = dir + "/new.txt";

        for (int i = 0; i < 8; i++) {
            menuItem = new JMenuItem(dataname);
            menuItem.setActionCommand(dataname + "**");
            menuItem.addActionListener(this);
            gogo.add(menuItem);
        }

        addHelp(gogo, "Go");

        // Setting font size menu
        setJMenu(fosize, ZEditor.fontsizes, ZEditor.fosizecmds);
        addHelp(fosize, "FontSize");

        // Setting font family menu            
        setJMenu(fofam, ZEditor.fontfamilies, ZEditor.fofamcmds);
        addHelp(fofam, "FontFamily");

        // Setting font styles menu
        setJMenu(fostyle, ZEditor.fontstyles, ZEditor.fostylecmds);
        addHelp(fostyle, "FontStyle");

        // Setting EMail menus      
        addHelp(emem, "Send EMail");
        addHelp(geteml, "Get EMail");
        addHelp(mailmail, "EMail");

        /*
                ImageIcon ike0 = new ImageIcon(ClassLoader.getSystemResource("ServPak/SendMail16.gif"));
                mailmail.setIcon(ike0);
                mailmail.setToolTipText("EMail");
        */
        jiji.add(mailmail);
        mailmail.add(geteml);
        mailmail.add(emem);

        /*
                ImageIcon ike1 = new ImageIcon(ClassLoader.getSystemResource("ServPak/History16.gif"));
                gogo.setIcon(ike1);
                gogo.setToolTipText("Go/History");
        */
        jiji.add(gogo);

             syml = getJMenu("data/Symbols.data");

        texsyml = new String[syml.length];

        for (int q = 0; q < syml.length; q++) {
            String term = syml[q];
            texsyml[q] = "\\" + term.substring(1, term.length() - 1) + "*";
        }

        setJMenu(texpop, texsyml);

        setJMenu(textex, texsyml);
        addHelp(textex, "TeXSyms");
        texpop.setMnemonic('S');

        // Set symbols menus
        if (loadmlsyms) {
            Arrays.sort(syml);
            setJMenu(symsym, syml, jiji);
            setJMenu(sympop,syml);	
            addHelp(symsym, "MLSyms");
            sympop.setMnemonic('S');
        }

        /// Unicode Blocks
        if (howmuchusyms != 0) {
            String[] uniblx = getJMenu("data/UniBlox.data");
            int size = 0;

            actcmds = prefixed(uniblx,"Bl@@k-");

            setJMenu(ldsym, uniblx, actcmds);
            addHelp(ldsym, "UniBlox");

            /// Unicode Symbols Menus usym is added to hold unicode block menus as requested
            addHelp(usym, "UniSyms");
            jiji.add(usym);
            jiji.add(ldsym);
        }

        jiji.add(Box.createHorizontalGlue());
        adad.add(momo);

        addHelp(fontms, "Fonts");
        fontms.add(fofam);
        fontms.add(fosize);
        fontms.add(fostyle);
        jiji.add(fontms);
        jiji.add(Box.createHorizontalGlue());
        jiji.add(adad);

        // set menu of available alphabets

        String[] alphabets = getJMenu("Data/Alphabets.data", false);
        actcmds = prefixed(alphabets,"@lph@bet-");

        setJMenu(lingling, alphabets, actcmds);
        addHelp(lingling, "Alphabet");
        jiji.add(lingling);
        jiji.add(Box.createHorizontalGlue());
        bkmrx = getJMenu("Data/bookmarks.data", false);
        actcmds = new String[bkmrx.length];
        actcmds[0] = "Add Bookmarks";
        actcmds[1] = "Delete Bookmarks";

        for (int i = 2; i < bkmrx.length; i++) {
            actcmds[i] = "b@km@rk-" + bkmrx[i];
        }

        setJMenu(bookmarks, bkmrx, actcmds);
        jiji.add(bookmarks);
        addHelp(bookmarks, "Bookmarks");
        jiji.add(Box.createHorizontalGlue());
        jiji.add(txtx);
        jiji.add(dada);
        jiji.add(Box.createHorizontalGlue());
        addHelp(noto, "Notes");
        jiji.add(noto);
        jiji.add(Box.createHorizontalGlue());

        jiji.setBorderPainted(true);

        getAlphabet(alph);

        System.out.println("JMenus added");

         jazz = new JScrollPane(writer);

	  jazz.setComponentOrientation(ComponentOrientation.RIGHT_TO_LEFT);

                jazz.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED);
                jazz.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        southpanel.setBorder(bborder);
        southpanel.setLayout(new BorderLayout());
        southpanel.add("North", currentinfo);

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add("Center", jazz);
        getContentPane().add("South", southpanel);
        getContentPane().add("North", jiji);

 

        ////////////////////////////////////////////////////
        //////////////////// KEY EVENTS /////////////////////////
        ////////////////////////////////////////////////////
        writer.addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {

                    int code = e.getKeyCode();

	      boolean texing = false;

                    Stack <Integer> attrgaps = mod.attgaps;

                    if ((code == KeyEvent.VK_TAB) &&
                            !attrgaps.empty()) {
                        e.setKeyCode(KeyEvent.VK_UNDEFINED);
                        writer.setCaretPosition(writer.getCaretPosition() + attrgaps.pop());

                        return;
                    }

                    ////////////////////////////// HILITING //////////////////////
                    if ((keywords.length > 0) &&
                            ((code == 0x5b) || (code == KeyEvent.VK_SPACE) ||
                            (code == KeyEvent.VK_ENTER) ||
                            (code == KeyEvent.VK_SHIFT) ||
                            (code == KeyEvent.VK_PERIOD))) {
                        int localpos = writer.getCaretPosition();

                        try {
                            String logos = localWord(localpos);
                            boolean isinit = false;

                            for (String v : keywords) {
                                if (v.equals(logos)) {
                                    isinit = true;

                                    break;
                                }
                            }

                            if (isinit) {
                                setAttrs(Color.blue);
                            }

                            writer.getCaret().setDot(localpos);
                        } catch (Exception lex) {
                            System.out.println(lex.getMessage());
                        }
                    }

	try{

                      if ((code == KeyEvent.VK_SPACE) && modifs(e,"cAS")) {
	             Point pp = writer.getCaret().getMagicCaretPosition();
                           unipop.show(writer, pp.x, pp.y);
                        }

                    if ((code == KeyEvent.VK_U) && modifs(e,"cAs")) {
                        upCase();
                    }

                    if ((code == KeyEvent.VK_L) && modifs(e,"cAs")) {
                        downCase();
                    }

                    if ((code == KeyEvent.VK_BACK_SPACE) && modifs(e,"CaS")) {
                        deleteWord();
                    }
	}catch(Exception nullex){return;}

                    if (( (code == KeyEvent.VK_Z) || (code == KeyEvent.VK_L) ) && modifs(e,"cAS")) {

		FontMetrics ftm = getFontMetrics(writer.getFont());

		int padcorrection = 0;
		int location = writer.getCaret().getMagicCaretPosition().y;

		if(textin.isVisible()) padcorrection = ftm.getHeight()*(1+mod.rows);

		JViewport jvp = jazz.getViewport();
	
		int ht = ZEditor.hght-5*ftm.getHeight()-padcorrection;

		if(code == KeyEvent.VK_L) location = location-ht/2;

		if(location<0) {
		 jvp.setViewPosition(new Point(0,0));	
		 return;
		} 

		int checksize = location+ht-jvp.getViewSize().height+3*ftm.getHeight();

		if(checksize>0) {
				int numlines = (int) Math.ceil(checksize/ftm.getHeight());

				StringBuilder bfy = new StringBuilder(numlines);
				for (int q=0;q<numlines;q++) bfy.append("\r\n");
	try{
	      writer.getDocument().insertString(writer.getDocument().getLength(), bfy.toString(), attrs);
		
			}catch(Exception locex){System.out.println(locex.getMessage());}

		        	               jvp.setViewSize(new Dimension(
				 jvp.getViewSize().width, jvp.getViewSize().height+checksize));
		                           }
		 jvp.setViewPosition(new Point(0,location));	
		 writer.requestFocus();
	}

                    ////////////////////////// DICTIONARY IN/ DICTIONARY OUT ///////////////////
                    if ((code == KeyEvent.VK_SPACE) && e.isAltDown()) {
                        Alphabet.fontSize = fontSize;
                        Alphabet.fontFamily = fontFamily;

                        if (e.isShiftDown()) {
	Connection ccc = getConn();
                            Alphabet.dictionaryin(alph, localWord(writer.getCaretPosition()), ccc);
                        } else {
                            Alphabet alphi = new Alphabet(alph);

                            Point pp = writer.getCaret().getMagicCaretPosition();
                            int locus = writer.getCaretPosition();

                            srchwd = localWord(locus);

		     Connection ccc = getConn();
                            String[] dtems = alphi.dictionaryout(alph, srchwd, ccc);

                            String[] ditems = new String[dtems.length + 1];
                            ditems[0] = alphi.wordkey;

                            if (dtems.length > 0) {
                                for (int q = 0; q < dtems.length; q++) {
                                    ditems[q + 1] = dtems[q];
                                }

                                JPopupMenu dictitems = new JPopupMenu();
                                setJMenu(dictitems, ditems);
                                dictitems.show(writer, pp.x, pp.y);
                                dictionary = true;
                            } else {
                                dictionary = false;

                                return;
                            }
                        }
                    }

                    if ((code == 0x4e) && modifs(e,"caS")) {
//                        moveToBack();
                    }

                    if ((code == 0x4a) && modifs(e,"cAS")) {
                        bold = !bold ;
                        setAttrs();
                    }

                    if ((code == 0x49) && modifs(e,"cAS")) {
                        italic = !italic ;
                        setAttrs();
                    }

                    ////////////////////// NOTES ////////////////////////////
                    currentfile = webstyle(currentfile);

                    if ((code == 0x54) && modifs(e,"cAS")) {
                        new Annotate(localWord(writer.getCaretPosition()),
                            currentfile);
                    }

                    if ((code == 0x59) && modifs(e,"cAS")) {
                        localword = localWord(writer.getCaretPosition());

                        Annotate anni = new Annotate(localword, currentfile);

                        highLight(writer.getCaretPosition());

		String link = NetsManager.XCommands.hexml(localword);

                        writer.replaceSelection(
"\n<notes file=\""+currentfile+"\" link=\""+link+"\">"+localword +"</notes>\n");

                        setNotes(currentfile);
                    }

                    ///////////////////////// WORD COMPLETION /////////////////////////

	        if (code == KeyEvent.VK_TAB && modifs(e,"CAs")) {
try{
                                    writer.getDocument().insertString(writer.getCaretPosition(), "          ", attrs);
}catch(Exception etab){}
			}


                    if (mod.modename.endsWith("Tex")) {
                        if (code == KeyEvent.VK_TAB && !modifs(e,"CAs")) {
                             e.setKeyCode(KeyEvent.VK_UNDEFINED);
		texing = true;
		}
	}

                    if ((code != KeyEvent.VK_BACK_SPACE) &&  
                            (code != KeyEvent.VK_SHIFT) && (!texing) &&
                            ((code < 48) || (code > 122) ||
                            ((code >= 91) && (code <= 96)) ||
                            ((code <= 64) && (code >= 58)))) {
                        scratch = "";
                        chary = new StringBuilder();
                        completing = false;
                        currentinfo.setText(currentfile);
                    }

                    if (code == KeyEvent.VK_BACK_SPACE) {
                        if (chary.length() > 0) {
                            chary = chary.deleteCharAt(chary.length() - 1);
                            completing = false;
                        }
                    }

                    if (!completing) {
                        scratch = chary.toString();
                    }

                    if ((code < 123) && (code > 47) && (code != 91) &&
                            (code != 93) && !((code <= 64) && (code >= 58))) {
                        chary.append(e.getKeyChar());
                    }

              if ( code == 0x71 && modifs(e,"CAS") ) {
		     CompleteWord();
		}

                    //////////////////////// TEX COLORS ///////////////////////////
                    if (mod.modename.endsWith("Tex")) {

	          if(code == KeyEvent.VK_TAB && !modifs(e,"CAs")) CompleteWord();

                        if ((code == KeyEvent.VK_K) && modifs(e,"cAS")) {
                            mathmode = (mathmode == 0) ? 1 : 0;

                            if (mathmode == 1) {
                                setAttrs(new Color(dollar));
                                currentinfo.setText(
                                    "		                                                                           TexColorsOn");
                            }

                            if (mathmode == 0) {
                                currentinfo.setText(
                                    "		                                                                           TexColorsOff");
                                setAttrs();
                            }
                        }

                        if (code == KeyEvent.VK_BACK_SLASH) {
                            if (mathmode > 0) {
                                setAttrs(new Color(mathslash));
                            }

                            if (mathmode <= 0) {
                                setAttrs(new Color(slash));
                            }

                            controlsq = true;
                        }

                        if (e.isShiftDown() && (code == KeyEvent.VK_4)) {
                            setAttrs(new Color(dollar));
                            mathmode += mathflip;

                            if (mathmode > 0) {
                                currentinfo.setText(
                                    "		                                                                           TexColorsOn");
                            } else {
                                currentinfo.setText(
                                    "		                                                                           TexColorsOff");
                            }
                        }
                    }

                    if (controlsq &&
                            ((code == KeyEvent.VK_SPACE) ||
                            (code == KeyEvent.VK_ENTER))) {
                        controlsq = false;
                    }

                    if ((code != (0x24 | KeyEvent.VK_SHIFT)) && !controlsq) {
                        if (mathmode <= 0) {
                            mathflip = 1;
                            setAttrs();
                        }

                        if (mathmode > 0) {
                            setAttrs(new Color(mthmode));
                            mathflip = -1;
                        }
                    }

                    ////////////////////////// BRACES and PARENS ///////////////////////////
                    if (mod.modename.equals("Tex") ||
                            mod.modename.equals("LaTex") ||
                            mod.modename.equals("Java") ||
                            mod.modename.equals("Jv") ||
                            mod.modename.equals("Perl")) {
                        if ((code == KeyEvent.VK_OPEN_BRACKET) &&
                                e.isShiftDown()) {
                            if (bracecount < 0) {
                                bracecount = 0;
                            }

                            int bracecolrs = bracecount * 32;

                            if (bracecolrs > 255) {
                                bracecolrs = 155;
                            }

                            int reds = 255 - bracecolrs;

                            if ((bracecount % 2) == 1) {
                                bracecolor = (bracecolrs << 16) + reds +
                                    (bracecolrs << 8);
                            }

                            if ((bracecount % 2) == 0) {
                                bracecolor = (reds << 16) + bracecolrs +
                                    (bracecolrs << 8);
                            }

                            colorstack.push(new Color(bracecolor));
                            setAttrs(new Color(bracecolor));
                            bracecount++;
                        }

                        if ((code == KeyEvent.VK_CLOSE_BRACKET) &&
                                e.isShiftDown()) {
                            bracecount--;

                            try {
                                setAttrs(colorstack.pop());
                            } catch (Exception colorex) {
                                setAttrs(Color.blue);
                            }
                        }

                        if ((code == KeyEvent.VK_9) && e.isShiftDown()) {
                            if (parencount < 0) {
                                parencount = 0;
                            }

                            int parencolrs = 200;

                            if ((parencount % 2) == 1) {
                                parencolor = (parencolrs << 16);
                            }

                            if ((parencount % 2) == 0) {
                                parencolor = (parencolrs << 8);
                            }

                            colorstack.push(new Color(parencolor));
                            setAttrs(new Color(parencolor));
                            parencount++;
                        }

                        if ((code == KeyEvent.VK_0) && e.isShiftDown()) {
                            parencount--;

                            try {
                                setAttrs(colorstack.pop());
                            } catch (Exception colorex) {
                                setAttrs(Color.red);
                            }
                        }
                    }

                    if (code == 145) {
                        holding = !holding ;

                        if (holding) {
                            lettermap = new HashMap(Alphabet.alphmap);
                        }

                        if (!holding) {
                            writer.setEditable(true);
                        }
                    }

                    if (holding) {
                        int locus = writer.getCaretPosition();
                        String entry = getAlphSymbol(lettermap, code, e.getModifiers());

                        try {
                            writer.getDocument().insertString(locus, entry, attrs);
                        } catch (Exception exx) {
                        }

                        writer.setEditable(entry.equals(""));

                        if ((e.getModifiers() & Event.ALT_MASK) == Event.ALT_MASK) {
                            writer.setEditable(false);
                        }
                    }

	               ///////////////////////// KEYSTROKE MACROS /////////////////////
   
                    if (makemak) {
                        makStak.push(e);
                    }

                 if ((code == 0x74) && modifs(e,"CAs")) {
                        makemak = true;
                        currentinfo.setText("Recording macro");
                        makStak = new Stack<KeyEvent>();
                        lettermap = new HashMap(Alphabet.alphmap);
                    }

                 if ((code == 0x75) && modifs(e,"CAs")) {
                        makemak = false;
                        currentinfo.setText("End macro record");

		makStak.pop();

                        kev = new KeyEvent[makStak.size()];
		makStak.toArray(kev);
		makStak.clear();

                    }
   
                    if ((code == 0x76) && modifs(e,"CAs")) {
   
                        try {

                            for (KeyEvent kevin : kev) {

                                int locus = writer.getCaretPosition();
                                int rowstart = Utilities.getRowStart(writer, locus);
                                int rowend = Utilities.getRowEnd(writer, locus);
                                int offset = locus - rowstart;
                                int codenum = kevin.getKeyCode();
                                int modif = kevin.getModifiers();
                                String entry = String.valueOf(kevin.getKeyChar());

                                if (modif == Event.CTRL_MASK) {
                                    if (codenum == KeyEvent.VK_R) {
                                        findString();
                                    }

                                    if (codenum == KeyEvent.VK_S) {
                                        findString();
                                    }

                                    if (codenum == KeyEvent.VK_V) {
                                        writer.paste();
                                    }

                                    if (codenum == KeyEvent.VK_X) {
                                        writer.cut();
                                    }

                                    if (codenum == KeyEvent.VK_C) {
                                        writer.copy();
                                    }

                                    continue;
                                }

                                if ((modif & Event.ALT_MASK) == Event.ALT_MASK) {
                                    entry = getAlphSymbol(lettermap, code, modif);
                                }

                                if (((codenum > 14) && (codenum < 18))) {
                                    entry = "";

                                    continue;
                                }

                                if (((codenum < 41) && (codenum > 34)) ||
                                        (codenum == 127) || (codenum == 8)) {
                                    //8 backspace
                                    if (codenum == 8) {
                                        writer.moveCaretPosition(locus - 1);
                                        writer.replaceSelection("");
                                    }

                                    //35 end
                                    if (codenum == 35) {
                                        if (modif > 0) {
                                            writer.moveCaretPosition(rowend);
                                        } else {
                                            writer.setCaretPosition(rowend);
                                        }
                                    }

                                    //36 home
                                    if (codenum == 36) {
                                        if (modif > 0) {
                                            writer.moveCaretPosition(rowstart);
                                        } else {
                                            writer.setCaretPosition(rowstart);
                                        }
                                    }

                                    //37 left
                                    if (codenum == 37) {
                                        if (modif > 0) {
                                            writer.moveCaretPosition(locus - 1);
                                        } else {
                                            writer.setCaretPosition(locus - 1);
                                        }
                                    }

                                    //38 up
                                    if (codenum == 38) {
                                        int uprow = Utilities.getRowStart(writer,
                                                rowstart - 1);
                                        writer.setCaretPosition(uprow + offset);
                                    }

                                    //39 right
                                    if (codenum == 39) {
                                        if (modif > 0) {
                                            writer.moveCaretPosition(locus + 1);
                                        } else {
                                            writer.setCaretPosition(locus + 1);
                                        }
                                    }

                                    //40 down
                                    if (codenum == 40) {
                                        int dnrow = rowend + 1;
                                        writer.setCaretPosition(dnrow + offset);
                                    }

                                    //127 delete
                                    if (codenum == 127) {
                                        writer.moveCaretPosition(locus + 1);
                                        writer.replaceSelection("");
                                    }
                                } else {
                                    writer.getDocument().insertString(locus, entry, attrs);
                                }
                            }
                        } catch (Exception makx) {
                            return;
                        } finally {
                            return;
                        }
                    }
                }
            });

        ////////////////////////////////////////////////////
        //////////////////// MOUSE EVENTS //////////////////////
        ////////////////////////////////////////////////////
        writer.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (e.getClickCount() > 1) {
                        refresh();
                        System.out.println("Refreshing");

                        return;
                    }

                    if (SwingUtilities.isMiddleMouseButton(e)) {
                        try {
                            if (!e.isControlDown() && !e.isShiftDown()) {
                                writer.paste();
                            }
                        } catch (Exception exmiddle) {
                        }
                    }

                    if (SwingUtilities.isRightMouseButton(e)) {
                        if (modifs(e,"CAS")) {
                            unipop.show(e.getComponent(), e.getX(), e.getY());
                        }

                        if (modifs(e,"cAS")) {
                            writer.cut();
                        }
//////////// DICTIONARY IN-OUT MOUSE CONTEXT /////////////

                        if (modifs(e,"Cas")) {
                            Alphabet.fontSize = fontSize;
                            Alphabet.fontFamily = fontFamily;

		     Connection ccc = getConn();
                            Alphabet.dictionaryin(alph, localWord(writer.getCaretPosition()), ccc);
                        }

                        if (modifs(e,"CAs")) {
                            try {
                                Alphabet.fontSize = fontSize;
                                Alphabet.fontFamily = fontFamily;

                                Alphabet alphi = new Alphabet(alph);

                                Point pp = writer.getCaret().getMagicCaretPosition();
                                int locus = writer.getCaretPosition();

                                srchwd = localWord(locus);


		     Connection ccc = getConn();
                                String[] dtems = alphi.dictionaryout(alph, srchwd, ccc);

                                String[] ditems = new String[dtems.length + 1];
                                ditems[0] = alphi.wordkey;

                                if (dtems.length > 0) {
                                    for (int q = 0; q < dtems.length; q++) {
                                        ditems[q + 1] = dtems[q];
                                    }

                                    JPopupMenu dictitems = new JPopupMenu();
                                    setJMenu(dictitems, ditems);
                                    dictitems.show(writer, pp.x, pp.y);
                                    dictionary = true;
                                } else {
                                    dictionary = false;

                                    return;
                                }
                            } catch (Exception lx) {
                            }
                        }
                    }

                    if (SwingUtilities.isLeftMouseButton(e)) {
                        try {
                            if (!e.isControlDown() && !e.isShiftDown()) {
                                currentinfo.setText(currentfile);
                            }

                            if (!e.isShiftDown() && e.isControlDown()) {
//                                moveToBack();
                            }
                        } catch (Exception ex) {
                        }
                    }

                    //////////////// Reset scratch string for word completion /////////////////
                    scratch = "";
                    chary = new StringBuilder();
                    completing = false;
                    currentinfo.setText(currentfile);
                }

                public void mouseEntered(MouseEvent e) {
                    refresh();
                }
            });


  currentinfo.addMouseListener(new MouseAdapter() {

                public void mousePressed(MouseEvent e) {

                    if (SwingUtilities.isLeftMouseButton(e)) {
                        try {
                            if (!e.isControlDown() && !e.isShiftDown()) {
                                currentinfo.setText(currentfile);
                            }
                        } catch (Exception ex) { }
                      }
                   }
            });

        currentinfo.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    String getFile = currentinfo.getText();
                    setGoJMenu(getFile);

                    if (getFile.startsWith("http://")) {
                        int cut1 = getFile.indexOf("://");
                        int cut2 = getFile.indexOf("/", cut1 + 3);
                        hosttext = getFile.substring(cut1 + 3, cut2);
                        filetext = getFile.substring(cut2);

                        try {
                            SFileClient abc = new SFileClient(hosttext, filetext);
                            System.out.println(abc.sysout.toString());
                            callPage(abc.fileout);
                        } catch (Exception exc) {
                        }
                    } else {
                        callPage(currentinfo.getText());
                    }
                }
            });


            /////////////////// Set up File Chooser ////////////////////

        String[] filefilters = getJMenu("Data/Filefilters.data");
        String[] extensions;
        String description;

        for (String localstring : filefilters) {

            int cut = localstring.indexOf("|");
            description = localstring.substring(cut + 1);
            extensions = localstring.substring(0, cut).split(",");

        filii.addChoosableFileFilter(new ZFileFilter(extensions, description));
        }

        filii.addChoosableFileFilter(filii.getAcceptAllFileFilter());

        chary = new StringBuilder();
        writer.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        writer.setCaretColor(Color.red);
        writer.getCaret().setVisible(true);

        if (!new File(dir + "/" + "new.txt").exists()) {
            new File(dir + "/" + "new.txt").createNewFile();
        }

        currentfile = webstyle(dir + "/" + "new.txt");

        Dimension dsize = this.getSize();
        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        int locx = 0;
        int locy = scrsize.height  / 5;


        int localwdth = scrsize.width;
        int localhght = (int) (0.75*scrsize.height);
        this.setSize(new Dimension(localwdth, localhght));
        this.setMinimumSize(new Dimension(localwdth, localhght));
        this.setPreferredSize(new Dimension(localwdth, localhght));
	this.setLocation(locx,locy);

        pack();
        setVisible(true);

	currentfile = webstyle(title);
	dir = currentfile.substring(0,currentfile.lastIndexOf("/"));

	try{

	if(linenum !=0){

	FileInputStream bin = new FileInputStream(title);
	 byte[] contents = new byte[bin.available()];
	 bin.read(contents);

	  	Scanner sc = new Scanner(new ByteArrayInputStream(contents));

	int where =0;
	int numlines = 0;
	int lastlength = 0;

	while(sc.hasNextLine() && numlines < linenum) {
		String v = sc.nextLine();
		lastlength = v.length();
		where++;
		if(lastlength>0) where += lastlength;
		numlines++;
	}
     	
		int ww = where-lastlength-1;
		if(ww<0)  ww = where;

		writer.getDocument().insertString(0,new String(contents,"UTF-8"),null);
		 writer.requestFocus();

		extension = currentfile.substring(currentfile.lastIndexOf(".") + 1);

            if (extinfo.containsKey(extension)) {
                mode = extinfo.getProperty(extension);
            } else {
                mode = "Text";
            }

            mod = new Modes(mode, modesinfo);

	if(mod.modename.equals("LaTex") && !texChecker()) mode="Tex";

            setMode();
            setNotes(title);
	setModeMenu();

		JViewport jvp = jazz.getViewport();
		 jvp.setViewPosition(new Point(0,linenum));		

		 writer.requestFocus();
		 writer.setCaretPosition(ww);

	} else {

			callPage(currentfile);
	}

	}catch(Exception locex){System.out.println(locex.getMessage());}

    }

    //////////////  Constructor Dummy //////////////////////////
    public QuickEditor() {
    }

    //////////////////////////////////////////////////////////////      
    ////////////// Constructor: title and initial file ////////////  
    //////////////////////////////////////////////////////////////
    public QuickEditor(String _title, String filename) throws Exception {
        this(_title);

        currentfile = webstyle(filename);
        callPage(filename);
    }

    ////////////////////////  Constructors End /////////////////////////
    ////////////////////////////////////////////////////////////// 
    /////////////////////////// SET JMENU //////////////////////
    //////////////////////////////////////////////////////////////
    public void setJMenu(JMenu mimi, String[] words, int[] pstrokes,
        int[] pmodifiers) {
        setJMenu(mimi, words, pstrokes, pmodifiers, null);
    }

    public void setJMenu(JPopupMenu mimi, String[] words) {
        for (String v : words) {
            menuItem = new JMenuItem(v);
            menuItem.setBackground(Color.white);
            menuItem.setFont(new Font("Lucida Typewriter", Font.PLAIN, fontSize));
            menuItem.addActionListener(this);
            mimi.add(menuItem);
        }
    }

    public void setJMenu(JMenu mimi, String[] words, JMenuBar bibi) {
        setJMenu(mimi, words);
        bibi.add(mimi);
    }

    public void setJMenu(JMenu mimi, String[] words) {
        setJMenu(mimi, words, null, null, null);
    }

    public void setJMenu(JMenu mimi, String[] words, String[] actioncmds) {
        setJMenu(mimi, words, null, null, actioncmds);
    }

    public void setJMenu(JMenu mimi, String[] words, int[] pstrokes,
        int[] pmodifiers, String[] actioncmds) {
        int wl = words.length;

        int rem = wl % 9;
        int nummenus = (rem == 0) ? (wl / 9) : (1 + ((wl - rem) / 9));
        int len = 0;

        if (nummenus > 1) {
            for (int q = 0; q < nummenus; q++) {
                if (q < (nummenus - 1)) {
                    len = 9;
                } else {
                    len = (rem == 0) ? 9 : rem;
                }

                JMenu submenu = new JMenu();

                for (int i = 0; i < len; i++) {
                    int localindex = (q * 9) + i;

                    if (i == 0) {
                        String term = words[localindex];

                        if (term.indexOf("*") > 0) {
                            term = term.substring(0, term.indexOf("*"));
                        }
                        submenu.setText(term);
                    }

                    menuItem = menuSetter(words[localindex]);
                    menuItem.setBackground(Color.white);
                    menuItem.setFont(new Font(fontFamily, Font.PLAIN,
                            (int) Math.round(.85 * fontSize)));

                    if (pstrokes != null) {
                        menuItem.setAccelerator(KeyStroke.getKeyStroke(
                                pstrokes[localindex], pmodifiers[localindex]));
                    }

                    if (actioncmds != null) {
                        menuItem.setActionCommand(actioncmds[localindex]);
                    }

                    menuItem.addActionListener(this);

                    submenu.add(menuItem);
                }

                mimi.add(submenu);
            }
        } else {
            for (int i=0; i < words.length; i++) {
                menuItem = menuSetter(words[i]);
                menuItem.setBackground(Color.white);
                menuItem.setFont(new Font(fontFamily, Font.PLAIN,
                        (int) Math.round(.85 * fontSize)));

                if (pstrokes != null) {
                    menuItem.setAccelerator(KeyStroke.getKeyStroke(
                            pstrokes[i], pmodifiers[i]));
                }

                if (actioncmds != null) {
                    menuItem.setActionCommand(actioncmds[i]);
                }

                menuItem.addActionListener(this);
                mimi.add(menuItem);
            }
        }
    }

    ///////////////////////// End set JMenu //////////////////////


    ///////////////////////////////////////////////////////
    ///////////////////////// GET JMENU /////////////////////
    //////////////////////////////////////////////////
    public static String[] getJMenu(String filein) {
        return getJMenu(filein, true);
    }

    public static String[] getJMenu(String filein, boolean wrap) {

	String[] stary = new String[]{ };

        try {

            if (wrap) {
		din = new DataInputStream(ZEditor.wrapper(filein));
          } else {
		din = new DataInputStream(new FileInputStream(filein));
            }

	Scanner sc = new Scanner(din,"UTF-8").useDelimiter("\\n");

	Stack<String> staci = new Stack<String>();

	String v = null;

	while(sc.hasNext()) {
		v = sc.next();
		if(v.trim().length()>0) staci.push(v);
	}

	stary = new String[staci.size()];
	staci.toArray(stary);
	
        } catch (Exception ex) {
        }

        return stary;
    }

    //////////////////////////////////////////////////
    ///////////////// setQuickwords //////////////////
    //////////////////////////////////////////////////
    public void setQuickwords() { ///////////////////////////// setQuickwords ///////////////////////

        String datafile = "Quickwords/Quickwords.data." + mode.toLowerCase();
        String quickdatafile = mode.toLowerCase() + "/Quickwords.data." +
            mode.toLowerCase();

        ZEditor.putFile(quickdatafile, datafile);

        quickwords = getJMenu(datafile, false);
        Arrays.sort(quickwords);
        qwqw.removeAll();
        qwpop.removeAll();

        for (String v : quickwords) {
            menuItem = menuSetter(v);
            menuItem.addActionListener(this);
            qwqw.add(menuItem);
        }

        for (String v : quickwords) {
            menuItem = menuSetter(v);
            menuItem.addActionListener(this);
            qwpop.add(menuItem);
        }
	qwpop.setMnemonic('Q');
	unipop.add(qwpop);
    }

    //////////////////////////////////////////////////
    ///////////////// set Notes //////////////////
    //////////////////////////////////////////////////
    public void setNotes(String _fileName) {
        String[] notesdata = new String[] {  };

        int cut = _fileName.lastIndexOf("/");

        String fileName = _fileName.substring(0, cut + 1) + "." + _fileName.substring(cut + 1);
        String notesfile = fileName + ".aux";

        if (new File(notesfile).exists()) {
            noto.removeAll();			
            notesdata = getJMenu(notesfile, false);
        } else {
            return;
        }

        Arrays.sort(notesdata);

        for (String v : notesdata) {

	String y = v;

if(v.indexOf(String.valueOf('\u0660'))>-1) {	

            StringTokenizer stin = new StringTokenizer(v, String.valueOf('\u0660'));

            	    y = stin.nextToken();
	            while (stin.hasMoreTokens()) y += (" " + stin.nextToken());
	}

            menuItem = menuSetter(y);
            menuItem.setActionCommand("n@t@-" + y);
            menuItem.addActionListener(this);
            noto.add(menuItem);
        }
    }

    //////////////////////////////// SET GOJMENU //////////////////////////
    public void setGoJMenu(String filename) {
        String[] checkgo = new String[gogo.getItemCount()];

        for (int q = 0; q < checkgo.length; q++) {
            if (gogo.getItem(q).getText().equals(filename)) {
                return;
            }
        }

        gogo.remove(0);
        menuItem = new JMenuItem(filename);
        menuItem.setActionCommand(filename + "**");
        menuItem.addActionListener(this);
        gogo.add(menuItem);
    }

    /////////////////////// UNDOABLE EDIT HAPPENED ///////////////////////       
    public void undoableEditHappened(UndoableEditEvent e) {
        undo.addEdit(e.getEdit());
    }

    ///////////////////////////////////////////////////////
    //////////////////// SET ATTRIBUTES //////////////////
    ///////////////////////////////////////////////////////       
    public void setAttrs() { ///////////////////////////// setAttrs ///////////////////////

        if (fcolor == -1) {
            setAttrs(Color.white);
        } else {
            setAttrs(new Color(fcolor));
        }
    }

    public void setAttrs(Color color) {
        StyleConstants.setFontSize(attrs, fontSize);
        StyleConstants.setFontFamily(attrs, fontFamily);
        StyleConstants.setForeground(attrs, color);
        StyleConstants.setBold(attrs, bold);
        StyleConstants.setItalic(attrs, italic);
        fontStyle = "plain";

        if (bold & !italic) {
            fStyle = Font.BOLD;
            fontStyle = "bold";
        }

        if (!bold & italic) {
            fStyle = Font.ITALIC;
            fontStyle = "italic";
        }

        if (bold & italic) {
            fStyle = Font.BOLD | Font.ITALIC;
            fontStyle = " bold-italic";
        }

        currentFont = new Font(fontFamily, fStyle, fontSize);
        fontInfo.setText("Font: " + fontFamily + " " + fontStyle + " " +
            String.valueOf(fontSize));

        if (charset) {
            writer.setCharacterAttributes(attrs, true);
        } else {
            writer.setParagraphAttributes(attrs, true);
        }
    }

    ////////////////////////////////////////////////////
    //////////////// CALL PAGE //////////////////////////
    ////////////////////////////////////////////////////
    
  public void callPage(String filename) {

	if(filename.equals("")) { 
		writer.setDocument(writer.getEditorKit().createDefaultDocument());
		writer.getDocument().addUndoableEditListener(this);
	            callPage(dir+"/new.txt");
		return;
	}

        filename = webstyle(filename);

        try {

	FileInputStream chek = new FileInputStream(filename);

	byte[] checktype = new byte[12];
	chek.read(checktype);

	styled = chekstyle(checktype);

	FileInputStream fis = new FileInputStream(filename);

            currentfile = webstyle(new File(filename).getCanonicalPath());
            dir = currentfile.substring(0, currentfile.lastIndexOf("/"));

            currentinfo.setText(currentfile);

	if(currentfile.endsWith(".styl")) {
		String localfile = currentfile.substring(0,currentfile.lastIndexOf(".styl"));
            	extension = localfile.substring(localfile.lastIndexOf(".") + 1);
	} else {
		extension = currentfile.substring(currentfile.lastIndexOf(".") + 1);
	}

            if (extinfo.containsKey(extension)) {
                mode = extinfo.getProperty(extension);
            } else {
                mode = "Text";
            }

            mod = new Modes(mode, modesinfo);

	if(mod.modename.equals("LaTex") && !texChecker()) mode="Tex";

            setMode();
            setNotes(filename);

            this.setTitle(filename);
            this.setVisible(true);

if(styled){
		ObjectInputStream xmlin = 
		new ObjectInputStream(new FileInputStream(filename));
		Document docin = (Document) xmlin.readObject();
            	writer.setDocument(docin);
		writer.getDocument().addUndoableEditListener(this);

	}else{
            writer.getDocument().removeUndoableEditListener(this);
	writer.getDocument().remove(0,writer.getDocument().getLength());

	EditorKit kati = writer.getEditorKit();
	kati.read(new InputStreamReader(fis,"UTF-8"),writer.getDocument(),0);
	writer.getDocument().addUndoableEditListener(this);

	}

            setModeMenu();

            writer.setCaretPosition(0);
            writer.requestFocus();

            if (!notmp) {
                currenttmp = "TmpZefm/" + filename.replace('/', '_');
                savePage(currenttmp);
                setGoJMenu(filename);
            } else {
                notmp = false;
            }
        } catch (Exception e) {
            System.out.println(e.getMessage());

            return;
        }
    }

    //////////////////////////////////////////////////
    ///////////////////////// SAVE PAGE /////////////////////////
    //////////////////////////////////////////////////
  public void savePage(String filename) {
        if (numson) {
            numsWarning();

            return;
        } else {

	if(filename.endsWith(".styl")) styled = true;

if(!styled){
            try {
                FileOutputStream fileout = new FileOutputStream(filename);

	EditorKit kati = writer.getEditorKit();

	kati.write(
new OutputStreamWriter(fileout,"UTF-8"),writer.getDocument(),0,writer.getDocument().getLength());

                fileout.flush();
                fileout.close();
            } catch (Exception ioex) {
                currentinfo.setText("File not found. Not saved.");

                return;
            }
      }
            if (!filename.startsWith("TmpZefm/")) {
                setGoJMenu(filename);
                this.setTitle(filename);
            }

            this.setVisible(true);
        }

if(styled) {

          try {

	String localname = filename;

	if(!filename.endsWith(".styl")) filename = filename+".styl";

                ObjectOutputStream fileout = 
		new ObjectOutputStream(new FileOutputStream(filename));

	Document doc = writer.getDocument();

	   String ext = filename.substring(filename.lastIndexOf(".")+1);

	    if(!ext.equals("styl")) throw new Exception("namerror");

	   String basename = filename.substring(0,filename.lastIndexOf("."));
               FileOutputStream ft = new FileOutputStream(basename);

	EditorKit kati = writer.getEditorKit();

	kati.write(new OutputStreamWriter(ft,"UTF-8"),doc,0,doc.getLength());

                ft.flush();
                ft.close();
	
	System.out.println("Saved "+basename);
	
	doc.removeUndoableEditListener(this);

	fileout.writeObject(doc);
	fileout.flush();
	fileout.close();

            doc.addUndoableEditListener(this);

	if(!localname.endsWith(".styl")) {
		styled = false;
		currentinfo.setText(
		"Saving "+localname+" as "+filename+". You may open it via the Go Menu.");
	            setGoJMenu(filename);
		return;
	} 

            } catch (Exception ioex) {}
        }	
              currentinfo.setText("Saved " + currentfile);
    }

    //////////////////////////////////////////////////
    ////////////////////// SET PROPS //////////////////
    //////////////////////////////////////////////////
    public void setProps(Properties propinfo, JMenu mimi, boolean sort) {
        String[] props = setProps(propinfo, sort);
        mimi.removeAll();
        actcmds = prefixed(props,"s@tpr@ps-");

        setJMenu(mimi, props, actcmds);
    }

    public String[] setProps(Properties propinfo, boolean sort) {
        int maxcounter = propinfo.size();

        Stack<String> preprops = new Stack<String>();

        for (Enumeration enume = propinfo.keys();enume.hasMoreElements();) {
             String tmp = enume.nextElement().toString();

            if ( tmp.indexOf("Start") >= 0 || tmp.indexOf("Size") >= 0 ||
                    tmp.indexOf("commentstring") >= 0 || tmp.startsWith("~~") ) {

                maxcounter -= 1;
                continue;
            }
            	  preprops.push(tmp);
        }

	
	String[] props = new String[maxcounter];
	preprops.toArray(props);

        if (sort) {
            Arrays.sort(props);
        }
	        return props;
    }

    //////////////////////////////////////////
    ///////////////// SET PAD /////////////////
    //////////////////////////////////////////
    public void setPad(String datafile, int rows, int columns) {
        setPad(datafile, rows, columns, true);
    }

    public void setPad(String indata, int rows, int columns, boolean isfileinput) {
        //setPad
        int localwdth = this.getSize().width;
        int localhght = this.getSize().height;

        southpanel.remove(textin);

        textin = new JPanel();

        kbSize = rows * columns;

        letters = new JButton[kbSize];

        textin.setLayout(new GridLayout(rows, columns));

        try {
            String[] dani = new String[kbSize];

            if (isfileinput) {
                 FileInputStream fins = new FileInputStream(indata);
                bin = new BufferedReader(new InputStreamReader(fins, "UTF-8"));
            } else {
                bin = new BufferedReader(new StringReader(indata));
            }

            int kk = 0;

            for (String vv; (vv = bin.readLine()) != null;) {
                dani[kk] = vv;
                kk++;
            }

            for (int q = kk; q < kbSize; q++) {
                dani[q] = "-";
            }

            String v;
            String[] data = new String[kbSize];

            for (int s = 0; s < kbSize; s++) {
                int r = s % rows;
                int q = (s - r) / rows;
                int k = (columns * r) + q;

                data[k] = dani[s];
            }

	String[] popcmds = new String[kbSize];

            for (int k = 0; k < kbSize; k++) {
                v = data[k];

                String w = v;

                if (v.indexOf("|") > 0) {
                    int cut = v.indexOf("|");
                    w = v.substring(0, cut);
                }

	  data[k] = w;

                letters[k] = new JButton(w);
                letters[k].setBorder(emborder);
                letters[k].setFont((new Font(fontFamily, Font.BOLD,
                        (int) Math.round(0.85 * fontSize))));
                letters[k].setActionCommand(v);
                letters[k].addActionListener(this);

	 popcmds[k] = v;

                final String lable = w;
                letters[k].addMouseListener(new MouseAdapter() {
                        public void mousePressed(MouseEvent e) {
                            if (SwingUtilities.isRightMouseButton(e)) {
                                Helper hlp = new Helper(lable, "PadHelp.xml");
                                helping = true;
                            }
                        }
                    });	  
		   textin.add(letters[k]);
            }

	unipop.remove(padpop);
	padpop = new JMenu(mode+" Pad");
	setJMenu(padpop,data,popcmds);
	char[] menuname = mode.toCharArray();
	padpop.setMnemonic(menuname[0]);
	unipop.add(padpop);

        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        southpanel.add("Center", textin);

        this.setSize(new Dimension(localwdth, localhght));
        this.setMinimumSize(new Dimension(localwdth, localhght));
        this.setPreferredSize(new Dimension(localwdth, localhght));

        textin.setVisible(showpads);
        this.pack();
        writer.requestFocus();
        writer.getCaret().setVisible(true);
    }

    ////////////////////////////////////////////////// 
    //////////////////// RUNIT ////////////////////////
    //////////////////////////////////////////////////
    public void runIt(String _runcommand, String _currentfile) {

	if(_currentfile.endsWith(".styl")) 
		_currentfile = _currentfile.substring(0,_currentfile.lastIndexOf(".styl"));

	

        if (_runcommand.startsWith("latex")) {

if(!texChecker(_currentfile)){

	String part = _runcommand.substring(_runcommand.indexOf("latex")+5);
	_runcommand = "tex "+part;	
	System.out.println("Processing TeX file");
            setMode();
            setModeMenu();
	setNotes(_currentfile);
	}
     }
       	 runIt(_runcommand + " " + _currentfile);
    }

    public void runIt(String _shellcommand) {
        //runIt

        String []shellcommand = _shellcommand.split("\\s+");

        showoutput = new JFrame("Shell Output");

        JTextArea outview = new JTextArea("", 25, 70);
        JScrollPane scrollpane = new JScrollPane(outview,
                JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

        int[] loc = locationSet(10, 7);

        showoutput.setLocation(loc[0], loc[1]);

        showoutput.getContentPane().add(scrollpane);
        showoutput.pack();
        showoutput.setVisible(true);

        showoutput.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
                    showoutput.dispose();

                    return;
                }
            });

        outview.addMouseListener(new MouseAdapter() {
                public void mouseExited(MouseEvent e) {
                    showoutput.dispose();
                }
            });

        try {


	ProcessBuilder pb = new ProcessBuilder(shellcommand);
	pb.directory(new File(dir)); 
	Process out = pb.start();

            InputStream infoout = out.getInputStream();
            InputStream errout = out.getErrorStream();

            ByteArrayOutputStream stdout    = new ByteArrayOutputStream();
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

            if (shell) {
                dialog.dispose();
            }
        } catch (Exception e) {
            System.out.println(e.getMessage());
            showoutput.dispose();
        } finally {
            return;
        }
    }

    //////////////////////////////////////////////////
    ////////////////// FIND STRING //////////////////
    //////////////////////////////////////////////////
    void FindString() {
        findString();
    }

    void findString() { ///////////////////////////// findString ///////////////////////

try{
        writer.requestFocus();

        if (!replaceString) {
            lookfor = findList.getSelectedItem().toString();
        }

        searchlist.remove(lookfor);
        searchlist.add(0, lookfor);

            Document doc = writer.getDocument();
	String buffer = doc.getText(0,doc.getLength());

        boolean wrap = false;

        int gog = buffer.indexOf(lookfor, writer.getCaretPosition() + 1);

        if (gog < 0) {
            gog = buffer.indexOf(lookfor);
            wrap = true;
        }

        if (gog > -1) {
            writer.setCaretPosition(gog);
            writer.moveCaretPosition(gog + lookfor.length());

            if (replaceString) {
                writer.replaceSelection(replaced);
                writer.setCaretPosition(gog);
                writer.moveCaretPosition(gog + replaced.length());
            }
        }

        if (wrap) {
            currentinfo.setText("Wrapping lookup.");
        }

        if (gog < 0) {
            currentinfo.setText("NOT FOUND.");
        }
	}catch(Exception gtex){}

        dialog.dispose();
        writer.setEditable(true);
    }

    //////////////////////////////////////////////////
    ////////////////// REPLACE STRING //////////////////
    //////////////////////////////////////////////////
    void ReplaceString() {
        replaceString();
    }

    void replaceString() { ///////////////////////////// replaceString ///////////////////////
        lookfor = instring.getText();
        replaced = outstring.getText();

        replaceString = true;
        findString();
    }

    //////////////////////////////////////////////////
    ////////////////// MENU SETTER //////////////////
    //////////////////////////////////////////////////
    JMenuItem menuSetter(String tempword) {
        boolean tip = false;
        String tipwords = "";
        boolean noxml = false;

        if (tempword.indexOf("*") > 0) {
            int cut = tempword.indexOf("*");
            tempword = tempword.substring(0, cut);
            noxml = true;
        }

        if (tempword.indexOf("|") > 0) {
            int cut = tempword.indexOf("|");
            tipwords = tempword.substring(cut + 1);
            tempword = tempword.substring(0, cut);
            tip = true;
        }

        JMenuItem mItem = new JMenuItem(tempword);

        if (tip) {
            mItem.setToolTipText(tipwords);
        }

        if (noxml) {
            mItem.setActionCommand(tempword + "*");
        }

        final String cmmnd = tempword;

        mItem.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (SwingUtilities.isRightMouseButton(e)) {
                        Helper hlp = new Helper(cmmnd, "HelpFile.xml");
                        helping = true;
                    }
                }
            });

        return mItem;
    }

    //////////////////////////////////////////////////
    ////////////////// NUMS WARNING //////////////////
    //////////////////////////////////////////////////
    void numsWarning() { ///////////////////////////// numsWarning ///////////////////////
        sml = new JPanel();
        sml.setLayout(new GridLayout(2, 1));
        sml.add(new JLabel("Line Numbers are on."));
        sml.add(new JLabel("Turn them off before saving. Ctrl-F2 toggles."));

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Line Number Warning", sml);

        dialog.addMouseListener(new MouseAdapter() {
                public void mouseEntered(MouseEvent e) {
                    dialog.dispose();
                }
            });
    }

    //////////////////////////////////////////////////
    ////////////////// CHOOSE FILE //////////////////
    //////////////////////////////////////////////////

	 public void chooseFile(String _dir, boolean _open) {

		filechosen =currentfile;

		filii.setCurrentDirectory(new File(_dir));
	    	int returnVal = 0;
       
    if(_open) {
       		 returnVal = filii.showOpenDialog(filii.getParent());
      } else {
    	           returnVal = filii.showSaveDialog(filii.getParent());
    }
       	if(returnVal == JFileChooser.APPROVE_OPTION) {
	
try{
          	              filechosen = webstyle(filii.getSelectedFile().getCanonicalPath()); 
          	             dir = filechosen.substring(0,filechosen.lastIndexOf("/"));
}catch(Exception pathio){ filechosen =  "File Not Found";}
	              
       } else {

	if(currentfile.length()==0){
		if(edinfo.containsKey("INITDIR")) {
			dir = edinfo.getProperty("INITDIR");
				} else { 
			dir = System.getProperty("user.dir");
	}
          		filechosen = dir;	   
         }
     }	
  }

 
    //////////////////////////////////////////////////////////////	
    //////////////////////// SET MODE ///////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////// setModeMenu ///////////////////////////////
    public void setModeMenu() {
        jiji.remove(txtx);
        unipop.remove( txtxpop );
        txtx = new JMenu(mode);
        txtxpop = new JMenu(mode);

        ZEditor.putFile(mode.toLowerCase() + "/" + mod.menufile,
            "Data/" + mod.menufile);

        String[] modemenu = {  };
        String findtext = "";
        String patternstring = mod.modestring;
        HashSet<String> jumps = new HashSet<String>();

      try{

            Document doc = writer.getDocument();
	String text = doc.getText(0,doc.getLength());

        bin = new BufferedReader(new StringReader(text));

            if (patternstring.equals("<>")) {
                for (String v; (v = bin.readLine()) != null;) {
                    if (v.indexOf("<") < 0) {
                        continue;
                    }

                    int cut = v.indexOf("<");
                    findtext = v.substring(cut + 1);

                    if (findtext.startsWith("/")) {
                        continue;
                    }

                    jumps.add(findtext.substring(0, findtext.indexOf(">")));
                }
            } else {
                for (String v; (v = bin.readLine()) != null;) {
                    if (v.indexOf(patternstring + " ") < 0) {
                        continue;
                    }

                    int cut = v.indexOf(patternstring + " ");
                    findtext = v.substring(cut + patternstring.length());

                    if (findtext.indexOf(patternstring) >= 0) {
                        findtext = findtext.substring(0, findtext.indexOf(patternstring));
                    }
                    findtext = findtext.trim();
                    jumps.add(findtext);
                }
            }
        } catch (Exception ioe) {
        }

         modemenu = new String[jumps.size()];

         jumps.toArray(modemenu);
        Arrays.sort(modemenu);

         actcmds = prefixed(modemenu,"n@t@-");

        setJMenu(txtx, modemenu, actcmds);
        setJMenu(txtxpop, modemenu, actcmds);
        addHelp(txtx, mod.modename);
        jiji.add(txtx);
        unipop.add(txtxpop);
    }

    public void setMode() { ///////////////////////////// setMode ///////////////////////

        try {

            if (mod.modename.endsWith("Tex")) {
                jiji.remove(symsym);
                jiji.add(textex);
                unipop.remove(sympop);
                unipop.add(texpop);
            } else {
                jiji.remove(textex);
                jiji.add(symsym);
                unipop.remove(texpop);
                unipop.add(sympop);
            }

            String[] modemenu = {  };
            jiji.remove(dada);
           unipop.remove(dapop);

            if (new File("Data/" + mod.menufile).length() > 0) { 
                modemenu = getJMenu("Data/" + mod.menufile, false);
                dada = new JMenu(mod.modename + "Data");
                addHelp(dada, mod.modename + "Data");
                actcmds = new String[modemenu.length];

                for (int q = 0; q < modemenu.length; q++) {
                    actcmds[q] = modemenu[q] + "*";
                }

	 dapop = new JMenu(mod.modename + "Data");

                 setJMenu(dada, modemenu, actcmds);
	  setJMenu(dapop, modemenu, actcmds);

	char[] menuname = (mod.modename).toCharArray();
	dapop.setMnemonic(menuname[0]);

                 jiji.add(dada);
	  unipop.add(dapop);
            }			
        } catch (Exception ex) {
        }

        ZEditor.putFile(mode.toLowerCase() + "/" + mod.keywordfile,
            "Keywords/" + mod.keywordfile);	
        keywords = getJMenu("Keywords/" + mod.keywordfile, false);

        setQuickwords();

        if (mode.equals("Lang")) {
            String fntsize = edinfo.getProperty("FONTSIZELANG");

            if (fntsize != null) {
                fontSize = Integer.parseInt(fntsize);
            }

            writer.getDocument().putProperty(TextAttribute.RUN_DIRECTION,
                TextAttribute.RUN_DIRECTION_RTL);
            StyleConstants.setAlignment(attrs, StyleConstants.ALIGN_RIGHT);
            writer.setParagraphAttributes(attrs, true);
        } else {
            String fntsize = edinfo.getProperty("FONTSIZE");

            if (fntsize != null) {
                fontSize = Integer.parseInt(fntsize);
            }

            StyleConstants.setAlignment(attrs, StyleConstants.ALIGN_LEFT);
            writer.getDocument().putProperty(TextAttribute.RUN_DIRECTION,
                TextAttribute.RUN_DIRECTION_LTR);
        }

        ZEditor.putFile(mode.toLowerCase() + "/" + mod.datafile,
            "ClickPads/" + mod.datafile);
        setPad("ClickPads/" + mod.datafile, mod.rows, mod.columns);

        setAttrs();

    }

    ////////////////////////////////////////////
    ///////////// ALPHABET SETTINGS ////////////
    ////////////////////////////////////////////
    public void getAlphabet(String _alphabet) {
        language = false;

        alph = (_alphabet.indexOf(",") > 0)
            ? _alphabet.substring(0, _alphabet.indexOf(",")) : _alphabet;

        if (_alphabet.indexOf(",") > 0) {
            language = true;
        }

        Alphabet alphi = new Alphabet(alph);

        jiji.remove(alal);
        unipop.remove(alapop);

        alal = new JMenu(alph);
        alapop = new JMenu(alph);

        int longth = alphi.outstrokes.length;
        String[] ostrks = new String[longth];

        for (int q = 0; q < longth; q++) {
            String temp = alphi.outstrokes[q];
            ostrks[q] = temp.substring(0, temp.indexOf("*"));
        }

        setJMenu(alapop, ostrks, alphi.strokes, alphi.modifiers, alphi.outstrokes);
        setJMenu(alal, ostrks, alphi.strokes, alphi.modifiers, alphi.outstrokes);

	char[] menuname = alph.toCharArray();
	alapop.setMnemonic(menuname[0]);

        jiji.add(alal);
        unipop.add(alapop);

        StringBuilder outstr = new StringBuilder();

        for (int q = 0; q < longth; q++) {
            String temp = alphi.outstrokes[q];
            outstr.append(temp.substring(0, temp.indexOf("*")) + "\n");
        }

        int side = (int) Math.sqrt(longth);
        int rem = longth - (side * side);
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

        int rows = side;
        int columns = side + shift;
        int size = rows * columns;

        mode = (language) ? "Lang" : "Text";

        mod = new Modes(mode, modesinfo);

        if (mod.runcommand.equals("RTL")) {
            writer.getDocument().putProperty(TextAttribute.RUN_DIRECTION,
                TextAttribute.RUN_DIRECTION_RTL);
            StyleConstants.setAlignment(attrs, StyleConstants.ALIGN_RIGHT);

            String fntsizelang = edinfo.getProperty("FONTSIZELANG");

            if (fntsizelang != null) {
                fontSize = Integer.parseInt(fntsizelang);
            }
        } else {
            StyleConstants.setAlignment(attrs, StyleConstants.ALIGN_LEFT);
            writer.getDocument().putProperty(TextAttribute.RUN_DIRECTION,
                TextAttribute.RUN_DIRECTION_LTR);

            String fntsize = edinfo.getProperty("FONTSIZE");

            if (fntsize != null) {
                fontSize = Integer.parseInt(fntsize);
            }
        }

        setPad(outstr.toString(), rows, columns, false);
        setAttrs();
    }

    ///////////////////////////////////////////////////////////////////////////
    //////////////////////////// ADD HELP TO MENUBAR  /////////////////////////
    ///////////////////////////////////////////////////////////////////////////
    public void addHelp(JMenu mimi, String title) {
        final String ttl = title;
        mimi.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (SwingUtilities.isRightMouseButton(e)) {
                        Helper hlp = new Helper(ttl, "HelpFile.xml");
                        helping = true;
                    }
                }
            });
    }

    ///////////////////////////////////////////////////////////////////////////
    /////////////////// CONVERT COLOR STRINGS TO RGB  ///////////////////////
    ///////////////////////////////////////////////////////////////////////////
    public static int rgb(String colorin) {
        int cutone = colorin.indexOf(",");
        int lastcut = colorin.lastIndexOf(",");

        int cred = Integer.parseInt(colorin.substring(0, cutone));
        int cgreen = Integer.parseInt(colorin.substring(cutone + 1, lastcut));
        int cblue = Integer.parseInt(colorin.substring(lastcut + 1));

        return (cred << 16) + (cgreen << 8) + cblue;
    }

    ///////////////////////////////////////////////////////////////////////////
    /////////////////// CLICK GET LOCAL WORD  ///////////////////////
    ///////////////////////////////////////////////////////////////////////////
    String localWord(int locus) {
        if (writer.getSelectedText() != null) {
            return writer.getSelectedText();
        }

        highLight(locus);

        return writer.getSelectedText();
    }

    void highLight(int locus) { ///////////////////////////// highLight ///////////////////////

        try {
            int a = Utilities.getPreviousWord(writer, locus);
            int z = Utilities.getWordEnd(writer, a);
            writer.setCaretPosition(a);
            writer.moveCaretPosition(z);
        } catch (Exception px) {
        }
    }

    void upCase() { ///////////////////////////// upCase ///////////////////////
        writer.replaceSelection(writer.getSelectedText().toUpperCase());
    }

    void downCase() { ///////////////////////////// downCase ///////////////////////
        writer.replaceSelection(writer.getSelectedText().toLowerCase());
    }

    void deleteWord() { ///////////////////////////// deleteWord ///////////////////////

        int locus = writer.getCaretPosition();
        highLight(locus);
        writer.replaceSelection("");
    }

    ///////////////////////////////////////////////////////////////////////////
    //////////////////////////// REFRESH ///////////////////////
    ///////////////////////////////////////////////////////////////////////////
    void refresh() { ///////////////////////////// refresh ///////////////////////

        this.writer.requestFocus();
        this.writer.getCaret().setVisible(true);
    }

    ///////////////////////////////////////////////////////////////////////////
    //////////////////////////// ALPHSYMBOLS ///////////////////////
    ///////////////////////////////////////////////////////////////////////////

    public static String getAlphSymbol(HashMap mapper, int code, int mods) {
        if ((mods & Event.META_MASK) == Event.META_MASK) {
            String keystring = String.valueOf(code) + "C";

            if (mapper.containsKey(keystring)) {
                return mapper.get(keystring).toString();
            }
        }

        if ((mods & Event.SHIFT_MASK) == Event.SHIFT_MASK) {
            String keystring = String.valueOf(code) + "S";

            if (mapper.containsKey(keystring)) {
                return mapper.get(keystring).toString();
            }
        }

        if (mapper.containsKey(String.valueOf(code))) {
            return mapper.get(String.valueOf(code)).toString();
        }

        return "";
    }

    ////////////////// LOCATE WINDOW  ////////////////////////////////   
              
    public static int[] locationSet(int r1, int r2) {
        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        int locx = (scrsize.width) / r1;
        int locy = (scrsize.height) / r2;

        return new int[] { locx, locy };
    }

    //////////////////// ADJUST PATHNAMES WEBSTYLE///////////////////////////

    public static String webstyle(String name) {
        name = name.replace('\\', '/');

        if (name.indexOf(":/") >= 0) {
            return name.substring(name.indexOf(":") + 1);
        }

        return name;
    }

    ///////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    //////////////// COMMANDS AND ACTIONS //////////////////////
    ////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////

    public void actionPerformed(ActionEvent ae) {
        goApp = false;

        try {
            if (helping) {
                helping = false;

                return;
            }

            writer.setEditable(true);

            cmd = ae.getActionCommand();

            if (cmd.startsWith("s@tpr@ps")) {
                cmd = cmd.substring(cmd.indexOf("-") + 1);
                propsdata = true;
            }

            shell = false;

            if (dictionary) {
                try {
                    writer.replaceSelection(cmd);
                } catch (Exception exdict) {
                } finally {
                    dictionary = false;

                    return;
                }
            }

            if (currentfile != null) {
                currentinfo.setText(currentfile);
            }

            if (cmd.startsWith("@lph@bet")) {
                alph = cmd.substring(cmd.indexOf("-") + 1);
                getAlphabet(alph);
                this.pack();

                return;
            }

            ////////////// startsWithbkmrk ///////////////////////

	if(cmd.startsWith("b@km@rk")) {
		    callPage(cmd.substring(cmd.indexOf("-")+1));
		    return;
	}

/*	For modified FileChooser

            if (cmd.startsWith("b@km@rk")) {
                ((Window) filii.getTopLevelAncestor()).dispose();
                cmd = cmd.substring(cmd.indexOf("-") + 1).trim();

                if (cmd.equals("cancel")) {
                //    cmd = currentfile;

                    return;
                }

                if (cmd.equals("open")) {
                    if (filii.getSelectedFile() == null) {
                        filii.setSelectedFile(new File(fillin.getText()));
                    }

                    cmd = webstyle(filii.getSelectedFile().getCanonicalPath());
                    dir = cmd.substring(0, cmd.lastIndexOf("/"));

                    return;
                }

                callPage(cmd);

                return;
            }

*/

            if (cmd.startsWith("n@t@")) {
try{
                replaceString = false;
                writer.requestFocus();

                lookfor = cmd.substring(cmd.indexOf("-") + 1);
                searchlist.remove(lookfor);
                searchlist.add(0, lookfor);

            Document doc = writer.getDocument();
	String buffer = doc.getText(0,doc.getLength());

             boolean wrap = false;

                int gog = buffer.indexOf(lookfor, writer.getCaretPosition()+1);

                if (gog < 0) {
                    gog = buffer.indexOf(lookfor);
                    wrap = true;
                }

                if (gog > -1) {
                    writer.setCaretPosition(gog);
                    writer.moveCaretPosition(gog + lookfor.length());
                }

                if (wrap) {
                    currentinfo.setText("Wrapping lookup.");
                }

                if (gog < 0) {
                    currentinfo.setText("NOT FOUND.");
                }
		   }catch(Exception gtex){}
                return;
            }

            if (cmd.startsWith("f@nts@ze")) {
                String fontsize = cmd.substring(cmd.indexOf("-") + 1);
                fontSize = Integer.parseInt(fontsize);

                setAttrs();

                return;
            }

            if (cmd.startsWith("f@ntf@mily")) {
                fontFamily = cmd.substring(cmd.indexOf("-") + 1);

                if (fontFamily.equals("Lucida Sans Typewriter")) {
                    fontFamily = "Lucida Typewriter";
                }

                setAttrs();

                return;
            }

            if (cmd.startsWith("f@ntst@le")) {
                int switchit = 0;
                String fontstyle = cmd.substring(cmd.indexOf("-") + 1);

                for (int i = 0; i < 4; i++) {
                    if (ZEditor.fontstyles[i].equals(fontstyle)) {
                        switchit = i;
                    }
                }

                switch (switchit) {
                case 0:
                    bold = true;
                    italic = false;

                    break;

                case 1:
                    bold = false;
                    italic = true;

                    break;

                case 2:
                    bold = true;
                    italic = true;

                    break;

                default:
                    bold = false;
                    italic = false;
                }

                setAttrs();

                return;
            }

            if (cmd.indexOf("**") > 0) {
                notmp = true;

                try {
                    currentfile = cmd.substring(0, cmd.indexOf("**"));
                    callPage(currentfile);
                } catch (Exception e) {
                } finally {
                    return;
                }
            }

	// Mail
            if (propsdata && mailinfo.containsKey(cmd)) {
                //aliases
                propsdata = false;
                Mailer(cmd);

                return;
            }

            if (propsdata && getmailinfo.containsKey(cmd)) {
                //getting email
                propsdata = false;
                GetMail();

                return;
            }

            if (modesinfo.containsKey(cmd)) {
                mode = cmd;
                mod = new Modes(mode, modesinfo);
                setMode();
                setModeMenu();

                return;
            }

            if (cmd.startsWith("Bl@@k")) {
                String _rangeplus = cmd.substring(cmd.indexOf("-") + 1);
                String _name = _rangeplus.substring(0, _rangeplus.indexOf("|"));
                String _range = cmd.substring(cmd.indexOf("|") + 1);

                Block(_name, _range);

                return;
            }

            if (cmd.startsWith("Run")) {
                Run(cmd);
            }

            if ((runapp != null) && cmd.equals(runapp.confirmString)) {
                runapp.go(runapp.which);

                return;
            }

            try {
                ((Method) harry.get(ZEditor.crunch(cmd))).invoke(this, null);

                return;
            } catch (Exception e) {
            }

            String cmdout = "";

            cmdout = mod.ktv(cmd);

            if (cmdout.length() > 0) {
                setAttrs(mod.color);
                writer.getDocument().insertString(writer.getCaretPosition(),
                    cmdout, attrs);
                writer.setCaretPosition(writer.getCaretPosition() -
                    mod.backshift);
            }
        } catch (Exception exxx) {
        } finally {
            refresh();
        }
    }

    //////////////////////////////////////////////////////////////
    void Open() { ///////////////////////////// OPEN ///////////////////////
        //////////////////////////////////////////////////////////////

        if (numson || traceon) {
            numsWarning();

            return;
        } else {
            chooseFile(dir, true);
	currentfile = filechosen;
            extension = currentfile.substring(currentfile.lastIndexOf(".") + 1);
            callPage(currentfile);
        }
    }

    //////////////////////////////////////////////////////////////         
    void SaveAs() { ///////////////////////////// SAVEAS ///////////////////////
        //////////////////////////////////////////////////////////////

        if (numson) {
            numsWarning();

            return;
        } else {
            chooseFile(dir, false);
	outname = filechosen;
            currenttmp = "TmpZefm/" + outname.replace('/', '_');
            savePage(currenttmp);

	if(outname.endsWith(".styl")) styled = true;

            savePage(outname);
            currentfile = outname;

	if(currentfile.endsWith(".styl")) {
		String localfile = currentfile.substring(0,currentfile.lastIndexOf(".styl"));
            	extension = localfile.substring(localfile.lastIndexOf(".") + 1);
	} else {
		extension = currentfile.substring(currentfile.lastIndexOf(".") + 1);
	}

            if (extinfo.containsKey(extension)) {
                mode = extinfo.getProperty(extension);
            } else {
                mode = "Text";
            }

            mod = new Modes(mode, modesinfo);
            setMode();
            setModeMenu();
        }
    }

    //////////////////////////////////////////////////////////////
    void Save() { ///////////////////////////// Save ///////////////////////
        //////////////////////////////////////////////////////////////

        if (numson) {
            numsWarning();

            return;
        } else {
            savePage(currentfile);
        }
    }

void DocSave(){ 
		styled = true;
		Save();
	           }
    //////////////////////////////////////////////////////////////
    void RevertFile() { ///////////////////////////// RevertFile ///////////////////////
        //////////////////////////////////////////////////////////////

        String tempfile = currenttmp.substring(8).replace('_', '/') + ".tmp";

        savePage(tempfile);

        try {
            FileInputStream fins = new FileInputStream(currenttmp);

            FileOutputStream fo = new FileOutputStream(currentfile);

            byte[] conts = new byte[fins.available()];
            fins.read(conts);
            fo.write(conts);
            fo.flush();
            fo.close();
        } catch (Exception eio) {
        }

        callPage(currentfile);

        currentinfo.setText(tempfile + " is the modified file and " +
            currentfile + " the original one.");
    }

    //////////////////////////////////////////////////////////////
    void FTPGetFile() { ///////////////////////////// FTPGetFile ///////////////////////
        //////////////////////////////////////////////////////////////

        hostfield = new JTextField(uphosttext, 12);
        filefield = new JTextField(upfiletext, 25);
        pwfield = new JPasswordField(pwtext, 25);
        info = new JPanel();
        info.setLayout(new GridLayout(3, 2));
        info.add(new JLabel("User@Host:Port", JLabel.CENTER));
        info.add(hostfield);
        info.add(new JLabel("Remote File Name", JLabel.CENTER));
        info.add(filefield);
        info.add(new JLabel("Password", JLabel.CENTER));
        info.add(pwfield);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "FTP Get File", info, "Get File");
    }

    //////////////////////////////////////////////////////////////
    void GetFile() { ///////////////////////////// GetFile ///////////////////////
                     //////////////////////////////////////////////////////////////

        uphosttext = hostfield.getText();
        upfiletext = filefield.getText();
        pwtext = String.valueOf(pwfield.getPassword());

        try {
            SGetFtp abc = new SGetFtp(new String[] {
                        uphosttext, upfiletext, pwtext
                    });
            System.out.println(abc.sysout.toString());
            callPage(abc.fileout);
        } catch (Exception ec) {
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void ToggleClickPad() { /////////////////////////// ToggleClickPad ///////////////////////
        //////////////////////////////////////////////////////////////

        boolean textinvisible = (textin.isVisible()) ? false : true;
        textin.setVisible(textinvisible);
    }

    //////////////////////////////////////////////////////////////
    void ToggleCharacterParagraphAttributes() { //////// ToggleCharacterParagraphAttributes ////////
        //////////////////////////////////////////////////////////////

        charset = !charset ;

        if (charset) {
            currentinfo.setText(currentinfo.getText() +
                "                         				Setting style by characters.");
        } else {
            currentinfo.setText(currentinfo.getText() +
                "                          				Setting style by paragraphs.");
        }

        setAttrs();
    }

    //////////////////////////////////////////////////////////////
    void FontColor() { ///////////////////////////// FontColor ///////////////////////
        //////////////////////////////////////////////////////////////

        jodi = JColorChooser.createDialog(new JFrame(), "Choose Font Color",
                true, chance,
                new ActionListener() {
                    public void actionPerformed(ActionEvent ev) {
                    }
                },
                new ActionListener() {
                    public void actionPerformed(ActionEvent ev) {
                    }
                });
        jodi.setVisible(true);

        Color newcolor = chance.getColor();

        if (newcolor != null) {
            setAttrs(newcolor);
        }
    }

    //////////////////////////////////////////////////////////////
    void AddPicture() { ///////////////////////////// AddPicture ///////////////////////
        //////////////////////////////////////////////////////////////

//        textfill = new JTextField(picturetext, 40);

		filii.setCurrentDirectory(new File(dir));

       		int returnVal = filii.showOpenDialog(filii.getParent());

	picturetext = "";

       	if(returnVal == JFileChooser.APPROVE_OPTION) {
	
try{
          	             picturetext = webstyle(filii.getSelectedFile().getCanonicalPath()); 
	              
	       } catch (Exception picex){}
	}

	picturetext = "file:"+picturetext;

	AddIt();

/*
        sml = new JPanel();
        sml.add(textfill);

   dialog = new QuickDialog(new ZEdit.TPEditorX(), "Add Picture", sml, Add It", "Enter filename as a URL");
*/

    }

    //////////////////////////////////////////////////////////////
    void AddIt() { ///////////////////////////// AddIt ///////////////////////
                   //////////////////////////////////////////////////////////////

//        picturetext = textfill.getText();

        try {
            Icon ike = new ImageIcon(new URL(picturetext));
            writer.insertIcon(ike);
        } catch (Exception urlex) {
            System.out.println(urlex.getMessage());
   				}
	}

    //////////////////////////////////////////////////////////////
    void GetMail() { ///////////////////////////// GETMAIL ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            new MailRun(cmd);
        } catch (Exception mailex) {
            currentinfo.setText(mailex.getMessage());
        }
    }

    //////////////////////////////////////////////////////////////
    void UnPack64() { ///////////////////////////// UnPack64 ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(packed, 30);
        textfill2 = new JTextField(unpacked, 30);
        sml = new JPanel();
        sml.add(textfill);
        sml.add(textfill2);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "UnPack Base64", sml, "UnpackIt",
                "Enter packed filename (including path) in 1st slot and name of unpacked file in 2nd slot");
    }

    //////////////////////////////////////////////////////////////
    void UnpackIt() { ///////////////////////////// UnpackIt ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            packed = textfill.getText();
            unpacked = textfill2.getText();
            new UnPackEm(packed, unpacked);
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void Pack64() { ///////////////////////////// Pack64 ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(unpacked, 30);
        textfill2 = new JTextField(packed, 30);
        sml = new JPanel();
        sml.add(textfill);
        sml.add(textfill2);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Pack to Base64", sml, "PackIt",
	         "Enter filename (including path) to pack in 1st slot and name of packed file in 2nd slot");
    }

    //////////////////////////////////////////////////////////////
    void PackIt() { ///////////////////////////// PackIt ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            unpacked = textfill.getText();
            packed = textfill2.getText();
            new PackEm(unpacked, packed);
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void SaveRemote() { ///////////////////////////// SAVE REMOTE ///////////////////////
        //////////////////////////////////////////////////////////////

        porttext = portfield.getText();

        try {
            String ooutfile = currentfile.substring(currentfile.indexOf(
                        "RemoteFiles/") + 12);
            System.out.println("OUT " + ooutfile);

            int cut = ooutfile.indexOf("_");
            String host = ooutfile.substring(0, cut);
            String remotefile = ooutfile.substring(cut).replace('_', '/');
            pwordstext = pwordsfield.getText();

            new RemoteClient(new String[] {
                    host, porttext, currentfile, remotefile, pwordstext
                });
            currentinfo.setText(RemoteClient.reply);
        } catch (Exception exc) {
            currentinfo.setText(exc.getMessage());

            return;
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void Upload() { ///////////////////////////// UPLOAD ///////////////////////
        //////////////////////////////////////////////////////////////

        hostfield = new JTextField(uphosttext, 20);
        filefield = new JTextField(upfiletext, 20);
        upfield = new JTextField(uptext, 20);
        pwordsfield = new JTextField(pwordstext, 10);

        info = new JPanel(new GridLayout(4, 2));
        info.add(new JLabel("Host:Port", JLabel.CENTER));
        info.add(hostfield);
        info.add(new JLabel("Local File Name", JLabel.CENTER));
        info.add(filefield);
        info.add(new JLabel("Remote File Name", JLabel.CENTER));
        info.add(upfield);
        info.add(new JLabel("Password", JLabel.CENTER));
        info.add(pwordsfield);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Upload", info, "Send Remote");
    }

    //////////////////////////////////////////////////////////////
    void SendRemote() { ///////////////////////////// SendRemote ///////////////////////
        //////////////////////////////////////////////////////////////

        uphosttext = hostfield.getText();
        upfiletext = filefield.getText();
        uptext = upfield.getText();
        pwordstext = String.valueOf(pwordsfield.getText());

        int cut = uphosttext.indexOf(":");
        hosttext = uphosttext.substring(0, cut);
        porttext = uphosttext.substring(cut + 1);

        try {
            new RemoteClient(new String[] {
                    hosttext, porttext, upfiletext, uptext, pwordstext
                });
            currentinfo.setText(RemoteClient.reply);
        } catch (Exception exc) {
            currentinfo.setText(exc.getMessage());

            return;
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void RemoteEdit() { ///////////////////////////// RemoteEdit ///////////////////////
        //////////////////////////////////////////////////////////////

        hostfield = new JTextField(hosttext, 20);
        filefield = new JTextField(filetext, 20);

        info = new JPanel();
        info.setLayout(new GridLayout(2, 2));
        info.add(new JLabel("Host:Port", JLabel.CENTER));
        info.add(hostfield);
        info.add(new JLabel("Remote File Name", JLabel.CENTER));
        info.add(filefield);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Remote Edit", info, "Get Remote");
    }

    //////////////////////////////////////////////////////////////
    void GetRemote() { ///////////////////////////// GetRemote ///////////////////////
        //////////////////////////////////////////////////////////////

        hosttext = hostfield.getText();
        filetext = filefield.getText();

        try {
            SFileClient abc = new SFileClient(hosttext, filetext);
            System.out.println(abc.sysout.toString());
            callPage(abc.fileout);
        } catch (Exception ec) {
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void RemoteSave() { ///////////////////////////// REMOTESAVE ///////////////////////
        //////////////////////////////////////////////////////////////

        portfield = new JTextField(porttext, 5);
        pwordsfield = new JTextField(pwordstext, 10);

        info = new JPanel();
        info.setLayout(new GridLayout(2, 2));
        info.add(new JLabel("Port:", JLabel.CENTER));
        info.add(portfield);
        info.add(new JLabel("Password:", JLabel.CENTER));
        info.add(pwordsfield);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Remote Save", info, "Save Remote");
    }

    //////////////////////////////////////////////////////////////
    void Print() { ///////////////////////////// Print ///////////////////////
        //////////////////////////////////////////////////////////////

        JPanel prtll = new JPanel();
        prtll.setLayout(new GridLayout(3, 1));
        prtll.add(new JLabel());
        prtll.add(new JLabel("Printing Buffer " + currentfile));
        prtll.add(new JLabel());
        prtll.setFont(new Font("Serif", Font.BOLD,
                (int) Math.round((1.2) * fontSize)));
        prtll.setBackground(Color.cyan);
        prtll.setForeground(Color.black);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "PRINTING", prtll, "GoPrint");

        return;
    }

    //////////////////////////////////////////////////////////////
    void GoPrint() { ///////////////////////////// GoPrint ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            writer.getCaret().setVisible(false);

            RepaintManager currentManager = RepaintManager.currentManager(writer);
            currentManager.setDoubleBufferingEnabled(false);
            new ZPrint(writer);
            currentManager.setDoubleBufferingEnabled(true);
        } catch (Exception ex) {
        } finally {
            writer.getCaret().setVisible(true);
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void QuickMail() { ///////////////////////////// QuickMail ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(30);

        sml = new JPanel();
        sml.add(textfill);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Quick Mail", sml, "Mail To", "To: ");
    }

    //////////////////////////////////////////////////////////////
    void MailTo() { ///////////////////////////// MailTo ///////////////////////
        //////////////////////////////////////////////////////////////

        mailto = textfill.getText();
        direct = 0;

        dialog.dispose();

        textfill = new JTextField(30);

        sml = new JPanel();
        sml.add(textfill);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Send e-mail", sml, "Verify Send",
                "To: " + mailto + ". Fill in subject:");
    }

    //////////////////////////////////////////////////////////////
    void VerifySend() { ///////////////////////////// VerifySend ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            subject = textfill.getText();
            dialog.dispose();

	boolean splitmailer = false;	

	if(direct==2) {
		direct = 1;
		splitmailer = true;
	}

            switch (direct) {
            case (1):

                int cut = mailto.indexOf("@");
                if(!splitmailer) mailer = mailto.substring(cut + 1);

	Thread t = new Thread(){
	
		public void run(){
		try{
            Document doc = writer.getDocument();
	String contents = doc.getText(0,doc.getLength());

	Matcher eoline = eol.matcher(contents);
	contents = eoline.replaceAll("\r\n");
		 smc = new SMailClient(mailFrom, mailer, mailto, contents, subject);
	               callPage(smc.filename);

		return;
	}catch(Exception e){
		      System.out.println("MailServer not found.");
	}
            }
   };
	 	t.start();
		t.join(25000);	

                break;

            default:
                textfill = new JTextField(fileattachment, 30);
                smlx = new JDialog(new JFrame(), "Mailer", true);
                smlx.getContentPane().add("North",
                    new JLabel("If you want to add an attachment, enter the filename (include full path) and click GO. If not, click Close."));
                smlx.getContentPane().add("Center", textfill);

                JButton closeMe = new JButton("Close");
                JButton goGO = new JButton("GO");
                goGO.setBackground(Color.green);
                closeMe.setBackground(Color.red);

                goGO.addMouseListener(new MouseAdapter() {
                        public void mousePressed(MouseEvent e) {
                            fileattachment = textfill.getText();
                            smlx.dispose();
                        }
                    });


                closeMe.addMouseListener(new MouseAdapter() {
                        public void mousePressed(MouseEvent e) {
                            smlx.dispose();
                        }
                    });


                JPanel pini = new JPanel();
                pini.add(goGO);
                pini.add(closeMe);

                smlx.getContentPane().add("South", pini);
                smlx.getContentPane().setBackground(Color.cyan);
                smlx.getContentPane().setForeground(Color.black);

                int[] loc = locationSet(5, 2);
                smlx.setLocation(loc[0], loc[1]);

                smlx.pack();
                smlx.setVisible(true);

                JMailClient jmc;
                String maillog = "";

            Document doc = writer.getDocument();
	String text = doc.getText(0,doc.getLength());

                if (fileattachment.length() > 0) {
                    jmc = new JMailClient(mailFrom, mailer, mailto, text, subject, fileattachment);
                    maillog = JMailClient.outfile;
                } else {

	      mailer = mailinfo.getProperty("~~_by");

	Thread th = new Thread(){
	
		public void run(){
	try{
            Document doc = writer.getDocument();
	String contents = doc.getText(0,doc.getLength());

	Matcher eoline = eol.matcher(contents);
	contents = eoline.replaceAll("\r\n");

             		 smc = new SMailClient(mailFrom, mailer, mailto, contents, subject);

	}catch(Exception e){
		      System.out.println("MailServer not found.");
	}
            }
   };
	 	th.start();
		th.join(25000);	
                            maillog = smc.filename;
                }

                fileattachment = "";
                callPage(maillog);
            }
        } catch (Exception ex) {
        } finally {
            if (smlx != null) {
                smlx.dispose();
            }

            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void Clear() { ///////////////////////////// Clear ///////////////////////
                   //////////////////////////////////////////////////////////////

try{
        writer.getDocument().remove(0,writer.getDocument().getLength());
}catch(Exception eclear){}

        currentfile = "cleared.txt";
        currentinfo.setText(currentfile);
    }

    //////////////////////////////////////////////////////////////   
    void RefreshBuffer() { ////////// RefreshBuffer ////////////////
        ////////////////////////////////////////////////////////////

        try {
            Document doc = writer.getDocument();
	doc.removeUndoableEditListener(this);

	ByteArrayOutputStream store = new ByteArrayOutputStream();

                ObjectOutputStream bout = new ObjectOutputStream(store);

	bout.writeObject(doc);
	bout.flush();
	bout.close();

		doc.remove(0,doc.getLength());

		ObjectInputStream xmlin = 
		new ObjectInputStream(new ByteArrayInputStream(store.toByteArray()));
		Document docin = (Document) xmlin.readObject();
            	writer.setDocument(docin);
		writer.getDocument().addUndoableEditListener(this);

            writer.setCaretPosition(0);

	if(mod.modename.equals("LaTex") && !texChecker()) mode="Tex";
	
	setMode();
            setModeMenu();
            setNotes(currentfile);
            refresh();
            currentinfo.setText("Buffer Refreshed");
        } catch (Exception ex) {
        } finally {
            cmd = "";
        }
    }

    ///////////////////////////////////////////
    void Quit() { ///////////////////////////// Quit ////////////
        /////////////////////////////////////////

        this.dispose();
    }

    ///////////////////////////////////////////
    void Close() { ///////////////////////////// Close //////////
                   /////////////////////////////////////////

        dialog.dispose();
    }

    void Cancel() {
        Close();
    }

     ///////////////////////////// Cancel ///////////////////////

    //////////////////////////////////////////////////////////////
    void LineNumbers() { ///////////////////////////// LineNumbers ///////////////////////
        //////////////////////////////////////////////////////////////

        if (numson) {
            numson = false;
        } else {
            numson = true;
        }

        lineco = writer.getCaretPosition();

       try {

            int lineno = 0;

            Document doc = writer.getDocument();

            int shift = 0;
            boolean caught = false;

	if( !currentfile.endsWith(".styl") ) {

	String text = doc.getText(0,doc.getLength());

            bin = new BufferedReader(new StringReader(text));

            StringBuilder texti = new StringBuilder(5 * text.length());

            int localposition = 0;

            if (!numson) {
                for (String v; (v = bin.readLine()) != null;) {
                    lineno++;
                    texti.append(v.substring(v.indexOf(": ") + 2) + "\n");

                    if (!caught) {
                        localposition += v.length();
                        shift += (String.valueOf(lineno).length() + 2);

                        if (localposition >= lineco) {
                            caught = true;
                        }
                    }
                }
            }

            if (numson) {
                for (String v; (v = bin.readLine()) != null;) {
                    lineno++;
                    texti.append(lineno + ": " + v + "\n");

                    if (!caught) {
                        localposition += v.length();
                        shift += (String.valueOf(lineno).length() + 2);

                        if (localposition >= lineco) {
                            caught = true;
                        }
                    }
                }
            }
		writer.getDocument().remove(0,writer.getDocument().getLength());
		writer.getDocument().insertString(0,texti.toString(),attrs);

	} else {

	int locus = 0;
	int rowstart = 0;
	int rowend = 0;
	int totalshift =0;

	int end = writer.getDocument().getLength();
	int width = 0;


            if (numson) {

	while(locus<end+totalshift){
	
		lineno++;	

			width = String.valueOf(lineno).length()+2;

		     rowstart = Utilities.getRowStart(writer, locus);
                              rowend = Utilities.getRowEnd(writer, locus);

		writer.getDocument().insertString(rowstart, lineno+": ",attrs);

			locus = rowend+width+1;

		totalshift += width;

                    if (!caught) {
		                        shift += width;
                        		if (rowend-shift >= lineco) caught = true;
                        } //localpos
                 }  
            } // numson

            if (!numson) {

	while(locus<end+totalshift){

	         	     lineno++;

			width = String.valueOf(lineno).length()+2;

		     rowstart = Utilities.getRowStart(writer, locus);
                              rowend = Utilities.getRowEnd(writer, locus);

			writer.getDocument().remove(rowstart, width);

			locus = rowend-width+1;

			totalshift += width;

	                    if (!caught) {

                        		shift +=  width;
		                        if (rowend >= lineco) caught = true;
                        } //localpos
	     }
            } // not numson

     } // styled

            int epsilon = -1;

            if (numson) {
                epsilon = 1;
            }

            writer.setCaretPosition(lineco + (epsilon * shift));
	
        } catch (Exception e) {
            return;
        }
    }

 
    //////////////////////////////////////////////////////////////
    void Trace() { ///////////////////////////// Trace ///////////////////////
        //////////////////////////////////////////////////////////////
       
 traceon = !traceon ;

        lineco = writer.getCaretPosition();

        try {
            int lineno = 0;

            Document doc = writer.getDocument();
	String text = doc.getText(0,doc.getLength());

            bin = new BufferedReader(new StringReader(text));

            StringBuilder texti = new StringBuilder(5 * text.length());

            int localposition = 0;
            int shift = 0;
            boolean caught = false;
            boolean tracerunning = false;

            for (String v; (v = bin.readLine()) != null;) {
                lineno++;

                if (v.trim().startsWith("// StartTrace")) {
                    tracerunning = true;
                }

                if (v.trim().startsWith("// StopTrace")) {
                    tracerunning = false;
                }

                if (traceon && tracerunning) {
                    texti.append(v + "\nSystem.out.println(" + lineno +
                        ");// traceon\n");
                }

                if (traceon && !tracerunning) {
                    texti.append(v + "\n");
                }

                if (!traceon) {
                    if (v.startsWith("System.out.println") &&
                            (v.indexOf("// traceon") > 0)) {
                        continue;
                    }

                    texti.append(v + "\n");
                }

                if (!caught) {
                    localposition += v.length();
                    shift += (String.valueOf(lineno).length() + 1);

                    if (localposition >= lineco) {
                        caught = true;
                    }
                }
            }

	writer.getDocument().remove(0,writer.getDocument().getLength());
            writer.getDocument().insertString(0, texti.toString().trim(), attrs);

            writer.setCaretPosition(texti.indexOf("StartTrace"));
        } catch (Exception e) {
            return;
        }
    }

    //////////////////////////////////////////////////////////////
    void Undo() { ///////////////////////////// Undo ///////////////////////
        //////////////////////////////////////////////////////////////
     
   try {
            undo.undo();
        } catch (CannotUndoException ex) {
            undo.redo();
        }
    }

    //////////////////////////////////////////////////////////////
    void Redo() { ///////////////////////////// Redo ///////////////////////
        //////////////////////////////////////////////////////////////
     
   try {
            undo.redo();
        } catch (CannotRedoException ex) {
            undo.undo();
        }
    }

    //////////////////////////////////////////////////////////////
    void CompleteWord() { ///////////////////////////// CompleteWord ///////////////////////
        //////////////////////////////////////////////////////////////

        if (!completing) {

            index = 0;

            try {
            Document doc = writer.getDocument();
	String text = doc.getText(0,doc.getLength());

                stro = new StreamTokenizer(new StringReader(text));
                stro.wordChars(48, 122);
                stro.ordinaryChars(58, 64);
                stro.ordinaryChars(91, 96);
                stro.ordinaryChars(33, 47);
                stro.wordChars(92, 92);
                tries = new Stack<String>();

                while (stro.nextToken() != StreamTokenizer.TT_EOF) {
                    if (stro.ttype != StreamTokenizer.TT_WORD) {
                        continue;
                    }

                    if (stro.sval.startsWith(scratch)) {
                        tries.push(stro.sval);
                    }
                }
            } catch (Exception et) {
                return;
            }

            completions = new String[tries.size()];

	tries.toArray(completions);	

            localword = scratch;
            position = writer.getCaretPosition() - scratch.length();

            if (completions.length > 0) {
                completing = true;
            }
        }

        if (completing) {

            int len = completions.length;
            String blanks = "";

            if (localword != null) {
                writer.setCaretPosition(position);
                writer.moveCaretPosition(position + localword.length());
                writer.replaceSelection("");
            }

            localword = completions[index];
            currentinfo.setText("Completing " + scratch + " to " + localword);

            if (localword != null) {
                try {
                    writer.setCaretPosition(position);
                    writer.getDocument().insertString(position, localword, attrs);
                } catch (Exception blx) {
                }
            }

            index++;

            if (index == len) {
                index = 0;
            }
        }
    }

    //////////////////////////////////////////////////////////////
    void Find() { ///////////////////////////// Find ///////////////////////
        //////////////////////////////////////////////////////////////
     
   writer.setEditable(false);
        replaceString = false;

        if (searchlist.size() > 12) {
            searchlist.removeElementAt(searchlist.size() - 1);
        }

        findList = new JComboBox(searchlist);
        findList.setEditable(true);

        sml = new JPanel();
        sml.add(findList);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Find String", sml, "Find String",
                "Enter string to search");

        findList.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    findString();
                }
            });
    }

    //////////////////////////////////////////////////////////////
    void Addnewquickwords() { ///////////// Addnewquickwords ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(40);
        sml = new JPanel();
        sml.add(textfill);

dialog = new QuickDialog(new ZEdit.TPEditorX(), "Adding quickwords", sml, "Confirm", "Fill in phrase:");
    }

    //////////////////////////////////////////////////////////////
    void Confirm() { ///////////////////////////// Confirm ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            String quickdatafile = "Quickwords/Quickwords.data." +
                mode.toLowerCase();
            FileOutputStream fo = new FileOutputStream(quickdatafile, true);
            PrintWriter pout = new PrintWriter(new OutputStreamWriter(fo,
                        "UTF-8"), true);
            pout.println(textfill.getText());
            pout.close();
            setQuickwords();
        } catch (IOException ioe) {
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void Deletequickwords() { ///////////////// Deletequickwords ///////////////////////
        //////////////////////////////////////////////////////////////

        sml = new JPanel();
        sml.setLayout(new GridLayout(2, 1));
        sml.add(new JLabel("Edit the Quickwords.data file"));
        sml.add(new JLabel("Save it and then Reload it from this menu."));

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Deletion info", sml);
    }

    //////////////////////////////////////////////////////////////
    void Addnewemailaddress() { ////////////// Addnewemailaddress ///////////////////////
        //////////////////////////////////////////////////////////////

        nickname = new JTextField(10);
        address = new JTextField(30);

        info = new JPanel();
        info.setLayout(new GridLayout(2, 2));
        info.add(new JLabel("Nickname", JLabel.CENTER));
        info.add(nickname);
        info.add(new JLabel("Address: id@host", JLabel.CENTER));
        info.add(address);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Adding new address", info, "Verify");

        addingaddr = true;
    }

    //////////////////////////////////////////////////////////////
    void Removeaddress() { /////////////////// Removeaddress ///////////////////////
                           //////////////////////////////////////////////////////////////

        nickname = new JTextField(10);

        info = new JPanel();
        info.setLayout(new GridLayout(2, 1));
        info.add(new JLabel("Nickname"));
        info.add(nickname);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Removing address", info, "Verify");

        addingaddr = false;
    }

    //////////////////////////////////////////////////////////////
    void Verify() { ///////////////////////////// Verify ///////////////////////
        //////////////////////////////////////////////////////////////

        if (addingaddr) {
            mailinfo.setProperty(nickname.getText(), address.getText());
        } else {
            mailinfo.remove(nickname.getText());
        }

        try {
            FileOutputStream fout = new FileOutputStream("Mail.properties");
            mailinfo.store(fout, "Aliases");
            setProps(mailinfo, emem, true);
            fout.close();
        } catch (IOException ioe) {
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void Reloadquickwords() { ///////////////// Reloadquickwords ///////////////////////
        //////////////////////////////////////////////////////////////

        setQuickwords();
    }

    //////////////////////////////////////////////////////////////
    void AddBookmarks() { //////////////////// AddBookmarks ///////////////////////
        //////////////////////////////////////////////////////////////

        address = new JTextField(currentinfo.getText());

        info = new JPanel();
        info.setLayout(new GridLayout(2, 1));
        info.add(new JLabel("Address              "));
        info.add(address);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Adding bookmark", info, "Go Bookmarks");
                

        addingaddr = true;
    }

    //////////////////////////////////////////////////////////////
    void DeleteBookmarks() { ///////////////////////////// DeleteBookmarks ///////////////////////
        //////////////////////////////////////////////////////////////

        address = new JTextField(currentinfo.getText());

        info = new JPanel();
        info.setLayout(new GridLayout(2, 1));
        info.add(new JLabel("Address              "));
        info.add(address);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Deleting bookmark", info,"Go Bookmarks");

        addingaddr = false;
    }

    //////////////////////////////////////////////////////////////
    void GoBookmarks() { ///////////////////////////// GoBookmarks ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            if (addingaddr) {
                PrintWriter prtw = new PrintWriter(new FileWriter(
                            "Data/bookmarks.data", true), true);
                prtw.println(new File(address.getText()).getCanonicalPath());
                prtw.close();
            } else {
                String newbkms = "";
                FileInputStream fins = new FileInputStream("Data/bookmarks.data");

                byte[] bbb = new byte[fins.available()];
                fins.read(bbb);

                StringTokenizer stin = new StringTokenizer(new String(bbb), "\n");

                while (stin.hasMoreTokens()) {
                    String v = stin.nextToken();

                    if (!v.equals(address.getText())) {
                        newbkms += (v + "\n");
                    }
                }

                PrintWriter prtww = new PrintWriter(new FileWriter(
                            "Data/bookmarks.data"), true);
                prtww.print(newbkms);
                prtww.close();
            }
System.out.println("A");
            bkmrx = getJMenu("Data/bookmarks.data", false);
System.out.println("AB");
            actcmds = new String[bkmrx.length];
            actcmds[0] = "Add Bookmarks";
            actcmds[1] = "Delete Bookmarks";

            for (int i = 2; i < bkmrx.length; i++) {
                actcmds[i] = "b@km@rk-" + bkmrx[i];
            }

            bookmarks.removeAll();

            setJMenu(bookmarks, bkmrx, actcmds);
        } catch (IOException ioe) {
        } finally {
            dialog.dispose();
        }
    }

    //////////////////////////////////////////////////////////////
    void START() { ///////////////////////////// START ///////////////////////
                   //////////////////////////////////////////////////////////////

        try {
            writer.getDocument().insertString(0, mod.startup, attrs);
        } catch (Exception e) {
            e.getMessage();
        }
    }

    //////////////////////////////////////////////////////////////
    void Compile() { ///////////////////////////// Compile ///////////////////////
        //////////////////////////////////////////////////////////////

        goApp = true;

        String gocmd = mod.runcommand;

        if (gocmd.equals("trax") || gocmd.equals("perl") ||
                gocmd.equals("clsv")) {
            if (gocmd.equals("trax")) {
                Run("Run XML");
            }

            if (gocmd.equals("perl")) {
                Run("Run Perl");
            }

            if (gocmd.equals("clsv")) {
                Run("Run Clsv");
            }
        } else {
            savePage(currentfile);
            runIt(gocmd, currentfile);
        }
    }

    //////////////////////////////////////////////////////////////
    void ToJava() { ///////////////////////////// ToJava ///////////////////////
        //////////////////////////////////////////////////////////////

        goApp = true;
        jxml = true;
        Run("Run XML");
    }

    //////////////////////////////////////////////////////////////
    void ToHTML() { ///////////////////////////// ToHTML ///////////////////////
        //////////////////////////////////////////////////////////////

        goApp = true;
        Run("Run XML");
    }

    //////////////////////////////////////////////////////////////
    void Run(String _cmd) { ///////////////////////////// Run ///////////////////////
        //////////////////////////////////////////////////////////////
   
   try{
            Document doc = writer.getDocument();
	String text = doc.getText(0,doc.getLength());

        runapp = new ZEdit.Commands(_cmd, text, currentfile, dir);

        if (runapp != null) {
            if (runapp.which >= 0) {
                cmd = null;
            }

            if ((runapp.which > 0) && (runapp.which < ZEdit.Commands.numapps)) {
                currentinfo.setText(runapp.confirmString);

                if (goApp) {
                    runapp.go(runapp.which);

                    return;
                }

                cmd = runapp.confirmString;
            }
        }
      }catch(Exception gtex){}
    }

    //////////////////////////////////////////////////////////////
    void RTL() { ////////////////////////// RTL ///////////////////////
        //////////////////////////////////////////////////////////////

        JFrame jff = new JFrame("RTL INFO");
        JTextArea jat = new JTextArea(5, 45);
        jff.getContentPane().add(jat);
        jff.pack();

        int[] loc = locationSet(5, 2);
        jff.setLocation(loc[0], loc[1]);

        String line = "In RTL mode use ctrl-L to move the lines to the right edge.\n";
        line += "Use F2 to refresh the buffer when switching between RTL and LTR.\n";
        line += "To get back to LTR, click English (e.g.) on the Alphabet menu, and hit F2 to refresh.";

        jat.setText(line);
        jff.setVisible(true);
    }

    //////////////////////////////////////////////////////////////
    void Shell() { ///////////////////////////// Shell ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(shellcommand, 30);
        sml = new JPanel();
        sml.add(textfill);

        textfill.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    runIt(textfill.getText());
                }
            });

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Run", sml, "Go");
        shell = true;
        dialog.requestFocus();
    }

    //////////////////////////////////////////////////////////////
    void Go() { ///////////////////////////// Go ///////////////////////
        //////////////////////////////////////////////////////////////

        runIt(textfill.getText());
    }

    //////////////////////////////////////////////////////////////
    void CloseShellWindow() { ////////////// CloseShellWindow ///////////////////////
        //////////////////////////////////////////////////////////////

        showoutput.dispose();
    }

    //////////////////////////////////////////////////////////////
    void ContinueFindorReplace() { /////////// ContinueFindorReplace ///////////////////////
        //////////////////////////////////////////////////////////////

        findString();
    }

    //////////////////////////////////////////////////////////////
    void Replace() { ///////////////////////////// Replace ///////////////////////
        //////////////////////////////////////////////////////////////

        instring = new JTextField(lookfor);
        outstring = new JTextField(20);

        info = new JPanel();
        info.setLayout(new GridLayout(2, 2));
        info.add(new JLabel("Search For", JLabel.CENTER));
        info.add(instring);
        info.add(new JLabel("Replace By", JLabel.CENTER));
        info.add(outstring);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Search and Replace", info,"Replace String");

        outstring.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    replaceString();
                }
            });

        instring.requestFocus();
    }

    ////////////////////////////////////////////////////////
    void Block(String name, String range) { ///////////// Block /////////////                                            ///////////////////////////////////////////////////////


        int cut = range.indexOf(":");
        int min = Integer.parseInt(range.substring(0, cut));
        int max = Integer.parseInt(range.substring(cut + 1));

        try {
            String getUdata = "data/UniList.data";

            bin = new BufferedReader(new InputStreamReader(ZEditor.wrapper(
                            getUdata)));

            Stack <String>stacii = new Stack<String>();
            int value = 0;

            for (String v; (v = bin.readLine()) != null;) {
                cut = v.indexOf("|");
                value = Integer.parseInt(v.substring(0, cut));

                if (max < value) {
                    break;
                }

                if (min <= value) {
                    stacii.push(v);
                }
            }

            String[] obi = new String[stacii.size()];
	stacii.toArray(obi);
            String[] wds = new String[stacii.size()];
            actcmds = new String[stacii.size()];

            for (int i = 0; i < obi.length; i++) {
                String indata = obi[i];
                cut = indata.indexOf("|");
                value = Integer.parseInt(indata.substring(0, cut));

                String symbol = String.valueOf((char) value);
                wds[i] = symbol + " " + indata.substring(cut + 1) + "|#" +
                    value;
                actcmds[i] = symbol + "*";
            }

            subusym1 = new JMenu(name);
            setJMenu(subusym1, wds, actcmds);

	char[] menuname = name.toCharArray();
	subusym1.setMnemonic(menuname[0]);

            subusym2 = new JMenu(name);
            setJMenu(subusym2, wds, actcmds);

	subusym2.setMnemonic(menuname[0]);

            if (!unimenus.containsKey(name + "1")) {
                unimenus.put(name + "1", subusym1);
                unimenus.put(name + "2", subusym2);
                unipop.add(subusym1);
                usym.add(subusym2);
            } else {
                usym.remove((JMenu) unimenus.get(name + "2"));
                unipop.remove((JMenu) unimenus.get(name + "1"));
                unimenus.remove(name + "1");
                unimenus.remove(name + "2");
            }
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }

    /////////////////////////////////////////////////////////////////////////////
    //////////////////////////// MAILER /////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    void Mailer(String _cmd) {
        String premailto = mailinfo.getProperty(_cmd);
        int cut = premailto.indexOf(",");

        if (cut < 0) {
            mailto = premailto;
            direct = 0;
        } else {
            mailto = premailto.substring(0, cut);
            direct = 1;
        }

	if(premailto.indexOf(',',cut+1)>=0) {
		mailer = premailto.substring(premailto.lastIndexOf(",")+1);
		direct = 2;
	}

        textfill = new JTextField(30);

        sml = new JPanel();
        sml.add(textfill);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Send e-mail", sml, "Verify Send",
                "To: " + _cmd + ". Fill in subject:");
    }

    /////////////////////////////////////////////////////////////////////////////
    //////////////////////////// MODS /////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    boolean modifs(InputEvent ie, String xyz) {

                   if (xyz.equals("cas")) return (ie.isControlDown() && ie.isAltDown() &&  ie.isShiftDown());
                   if (xyz.equals("caS")) return (ie.isControlDown() && ie.isAltDown() && !ie.isShiftDown());
                   if (xyz.equals("cAs")) return (ie.isControlDown() && !ie.isAltDown() && ie.isShiftDown());
                   if (xyz.equals("cAS")) return (ie.isControlDown() && !ie.isAltDown() && !ie.isShiftDown());
                   if (xyz.equals("Cas")) return (!ie.isControlDown() && ie.isAltDown() &&  ie.isShiftDown());
                   if (xyz.equals("CaS")) return (!ie.isControlDown() && ie.isAltDown() && !ie.isShiftDown());
                   if (xyz.equals("CAs")) return (!ie.isControlDown() && !ie.isAltDown() && ie.isShiftDown());
                   if (xyz.equals("CAS")) return (!ie.isControlDown() && !ie.isAltDown() && !ie.isShiftDown());

	return true;

	}	

    /////////////////////////////////////////////////////////////////////////////
    //////////////////////////// STYL CHECKING /////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

    boolean chekstyle(byte[] beti) {

	for (int q=0;q<12;q++) {
		if(beti[q] != header[q]) {
			return false;
		}
	}

	return true;

	}	

    /////////////////////////////////////////////////////////////////////////////
    //////////////////////////// PREFIXING /////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////

	public static String[] prefixed(String[] in, String prefix){	

		Stack<String> stac = new Stack<String>();
	
		for(String v : in) stac.push(prefix+v);
	
	            String[] out = new String[stac.size()];
		stac.toArray(out);

		return out;
     }


/////////////////////////////////////////////////////////////////////////////////
///////////////////////// TEXCHECKER //////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
  boolean texChecker() {

if(currentfile.endsWith(".styl")){

	return texChecker(currentfile.substring(0,currentfile.lastIndexOf(".styl")));

	}

	return texChecker(currentfile);
}

  boolean texChecker(String filename) {
	try{
	      BufferedReader fin = new BufferedReader(new FileReader(filename));
	
	        int count = 0;

	        for (String v; (v = fin.readLine()) != null;) {
	            if (v.indexOf("documentclass") > 0) {
		    return true;
	            }
	
	            count++;
	
	            if (count > 3) {
			break;	
	            }
	        }
	}catch(Exception exx){}

		mode="Tex";
		mod = new Modes(mode, modesinfo);

		return false;
     }

  //////////////////////////////////////////////////////////////
    void DiffFiles() { ///////////////////////////// Diff FILES ///////////////////////
        //////////////////////////////////////////////////////////////

        textfill = new JTextField(currentfile, 30);
        textfill2 = new JTextField(diff2, 30);
        sml = new JPanel();
        sml.add(textfill);
        sml.add(textfill2);

        dialog = new QuickDialog(new ZEdit.TPEditorX(), "Diff Files", sml, "GetDiff",
"Enter filename in 1st slot (default: current file) and name of 2nd file (default: currentfilename.bak) in 2nd slot");
    }

    //////////////////////////////////////////////////////////////
    void GetDiff() { ///////////////////////////// GetDiff ///////////////////////
        //////////////////////////////////////////////////////////////

        try {
            diff1 = textfill.getText();
            diff2 = textfill2.getText();
            DIFF.DiffPrint godiff = new DIFF.DiffPrint(diff1,diff2);

          showoutput = new JFrame("Shell Output");

        JTextArea outview = new JTextArea("", 25, 70);
        JScrollPane scrollpane = new JScrollPane(outview,
                JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

        int[] loc = locationSet(10, 7);

        showoutput.setLocation(loc[0], loc[1]);

        showoutput.getContentPane().add(scrollpane);
        showoutput.pack();
        showoutput.setVisible(true);

        showoutput.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
                    showoutput.dispose();

                    return;
                }
            });

        	outview.addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {

                    int code = e.getKeyCode();

                    if ((code == KeyEvent.VK_W) && modifs(e,"cAS"))
	                    showoutput.dispose();
                        return;
                    }
	});

           outview.setText("");
           outview.setFont(new Font(fontFamily, Font.BOLD, fontSize));
           outview.append(DIFF.DiffPrint.results);

        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        } finally {
            dialog.dispose();
        }
    }

public static void main(String[] qubits){
try{	
	new QuickEditor(qubits[0]);	
}catch(Exception ee){}
	}

///////////////// Get Connection //////////////////

       Connection getConn(){

			return DOps.goMysql;
     }

       void closeConn(Connection cc){

	System.out.println("Check DB connection");

     }
}

