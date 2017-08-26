package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;

import java.sql.*;


class QuickEditor extends JFrame implements ActionListener {
    // Class 
    static JTextPane writer = new JTextPane();
    static JMenu usym = new JMenu("UniSyms");
    static JPopupMenu unipop = new JPopupMenu();
    static JMenu subusym1;
    static JMenu subusym2;
    static HashMap unimenus = new HashMap();
    final static Modes mod = new Modes("Xml", TPEditorX.modesinfo);
    static SimpleAttributeSet attrs = new SimpleAttributeSet();
    static final String[] edits = { "Clear", "Save", "Quit" };
    static final String[] refs = { "reference|S" };
    static final String[] del = { "Verify Delete" };

    	 BufferedReader buf;

    JMenu links = new JMenu("DoLink");
    JMenu ldsym = new JMenu("UniBlox");
    JMenu erase = new JMenu("DeleteThisNote");
    JMenuItem menuItem;
    final JMenu eded = new JMenu("Edit");
    final JMenuBar jiji = new JMenuBar();
    String title;
    String basename;
    String key;
    String link;
    boolean ifold;
    int locx;
    int locy;

    ResultSet rs;
    Connection conn;

    public QuickEditor(String _basename, String ttl, boolean _ifold, String _key, String _link) {
        //Constructor	


 	   conn = DOps.goMysql;


        Dimension dsize = this.getSize();
        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        locx = (scrsize.width - dsize.width) / 3;
        locy = (scrsize.height - dsize.height) / 3;

        this.basename = _basename;
        this.title = ttl;
        this.ifold = _ifold;
        this.key = _key;
        this.link = _link;

        this.setTitle(title);

        int[] strokes = new int[] { 0x77, 0x70, KeyEvent.VK_Q };
        int[] modifiers = new int[] { 0, 0, Event.CTRL_MASK };

        setMenu(eded, edits, strokes, modifiers);

        jiji.add(eded);

        /// Unicode Blocks
        String[] uniblx = TPEditorX.getJMenu("data/UniBlox.data");
        int size = 0;

        String[] actcmds = TPEditorX.prefixed(uniblx,"Bl@@k-");

        setJMenu(ldsym, uniblx, actcmds);

        /// Unicode Symbols Menus usym is added to hold unicode block menus as requested
        jiji.add(usym);
        jiji.add(ldsym);

        setJMenu(links, new String[] { "reference" }, refs);
        jiji.add(links);

        setJMenu(erase, del, null);
        jiji.add(erase);

        System.out.println("Menus added");

        JScrollPane jazz = new JScrollPane(writer,
                JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
                JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS);

        int localwdth = (int) Math.round(0.65 * ZEditor.wdth);
        int localhght = (int) Math.round(0.45 * ZEditor.hght);

        jazz.setPreferredSize(new Dimension(localwdth, localhght));

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add("Center", jazz);

        getContentPane().add("North", jiji);

        writer.setFont(new Font("SansSerif", Font.BOLD, 18));
        writer.setBackground(Color.white);
        writer.setForeground(Color.black);

        writer.setText("");

        writer.addMouseListener(new MouseAdapter() {
                public void mousePressed(MouseEvent e) {
                    if (e.getClickCount() > 1) {
                        refresh();
                        System.out.println("Refreshing");

                        return;
                    }

                    if (SwingUtilities.isRightMouseButton(e)) {
                        unipop.show(e.getComponent(), e.getX(), e.getY());
                    }
                }
            });

        this.addWindowListener(new WindowAdapter() {
                public void windowClosing(WindowEvent e) {
                    dispose();
                }
            });

	String txt = "";

        if (ifold) {
try{
	txt = new String(getFile(basename,key),"UTF-8");
 }catch(Exception se){}
            }

            this.writer.setText(txt);

        setLocation(scrsize.width / 3, scrsize.height / 3);

        this.writer.requestFocus();

        this.pack();
        this.setVisible(true);
    }

    public void setMenu(JMenu mimi, String[] words, int[] strokes,
        int[] modifiers) {
        setJMenu(mimi, words, strokes, modifiers, null);
    }

    //////////////////////////////////////////////////////////////////////
    /////////////////////// COMMANDS AND ACTIONS /////////////////////               				/////////////////////////////////////////////////////////////////////
    public void actionPerformed(ActionEvent ae) {
        String cmd = ae.getActionCommand();

        if (cmd.startsWith("Bl@@k")) {
            String _rangeplus = cmd.substring(cmd.indexOf("-") + 1);
            String _name = _rangeplus.substring(0, _rangeplus.indexOf("|"));
            String _range = cmd.substring(cmd.indexOf("|") + 1);

            Block(_rangeplus, _name, _range);

            return;
        }

        if (cmd.equals("Clear")) {
            this.writer.setText(" ");

            return;
        }

        if (cmd.equals("Quit")) {
            this.dispose();
        }

        /////////////////// SAVE //////////////////////
        if (cmd.equals("Save")) {
            try {

	if(ifold) removeKey(basename, key.trim().replaceAll("'","\\\\'"));

		saveIt(basename, 
			key.trim().replaceAll("'","\\\\'"), link, writer.getText().getBytes("UTF-8"));

                final JFrame smlx = new JFrame("SAVING FILE");
                smlx.getContentPane().setLayout(new BorderLayout());
                smlx.getContentPane().add("Center", new JLabel(" " + title + " "));
                smlx.getContentPane().setBackground(Color.cyan);
                smlx.getContentPane().setForeground(Color.black);
                smlx.setLocation(locx, locy);
                smlx.pack();
                smlx.setVisible(true);

                smlx.addMouseListener(new MouseAdapter() {
                        public void mouseEntered(MouseEvent e) {
                            smlx.dispose();
                        }
                    });
            } catch (Exception e) {
                System.out.println(e.getMessage());

                return;
            }

            return;
        }

        /////////////// Verify DELETE ////////////////////////////
        if (cmd.equals("Verify Delete")) {
            try {                   

   	    removeKey(basename, key.trim().replaceAll("'","\\\\'"));

                final JFrame smlx = new JFrame("NOTES");
                smlx.getContentPane().setLayout(new BorderLayout());
                smlx.getContentPane().add("Center", new JLabel("Deleting Note"));
                smlx.getContentPane().setBackground(Color.yellow);
                smlx.getContentPane().setForeground(Color.black);
                smlx.setLocation(locx, locy);
                smlx.pack();
                smlx.setVisible(true);

                smlx.addMouseListener(new MouseAdapter() {
                        public void mouseEntered(MouseEvent e) {
                            smlx.dispose();
                            dispose();
                        }
                    });
            } catch (Exception e) {
                System.out.println(e.getMessage());

                return;
            }

            return;
        }

        String cmdout = "";

        cmdout = mod.ktv(cmd);

        try {
            if (cmdout.length() > 0) {
                writer.getDocument().insertString(writer.getCaretPosition(), cmdout, attrs);
                writer.setCaretPosition(writer.getCaretPosition() - mod.backshift);
            }
        } catch (Exception ex) {
        }
    }

    ////////////////////////// SETJMENU //////////////////////////////
    public void setJMenu(JMenu mimi, String[] words, String[] actioncmds) {
        setJMenu(mimi, words, null, null, actioncmds);
    }

    public void setJMenu(JMenu mimi, String[] words, int[] strokes,
        int[] modifiers, String[] actioncmds) {
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

                    if (strokes != null) {
	     menuItem.setAccelerator(KeyStroke.getKeyStroke(strokes[localindex], modifiers[localindex]));
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

                if (strokes != null) {
                    menuItem.setAccelerator(KeyStroke.getKeyStroke(strokes[i], modifiers[i]));
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

        return mItem;
    }

    ////////////////////////////////////////////////////////
    void Block(String rangeplus, String name, String range) { ///////////// Block /////////////

        ///////////////////////////////////////////////////////
        int cut = range.indexOf(":");
        int min = Integer.parseInt(range.substring(0, cut));
        int max = Integer.parseInt(range.substring(cut + 1));

        try {
            String getUdata = "data/UniList.data";

            buf = new BufferedReader(new InputStreamReader(ZEditor.wrapper(getUdata)));

            Stack <String>stacii = new Stack<String>();
            int value = 0;

            for (String v; (v = buf.readLine()) != null;) {
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
            String[] wds = new String[obi.length];
            String[] actcmds = new String[obi.length];

            for (int i = 0; i < obi.length; i++) {
                String indata = obi[i];
                cut = indata.indexOf("|");
                value = Integer.parseInt(indata.substring(0, cut));

                String symbol = String.valueOf((char) value);
                wds[i] = symbol + " " + indata.substring(cut + 1) + "|x" + value;
                actcmds[i] = symbol + "*";
            }

            subusym1 = new JMenu(name);
            setJMenu(subusym1, wds, actcmds);

            subusym2 = new JMenu(name);
            setJMenu(subusym2, wds, actcmds);

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

    ///////////////////////////////////////////////////////////////////////////
    //////////////////////////// REFRESH ///////////////////////
    ///////////////////////////////////////////////////////////////////////////
    void refresh() { ///////////////////////////// refresh ///////////////////////
        this.writer.requestFocus();
        this.writer.getCaret().setVisible(true);
    }


      ////////////////// DB OPS //////////////////


	//////////// SAVE in DB //////////

	 void saveIt(String name, String _word, String _link, byte[] _data) {

   try{

	 String sql =   "INSERT INTO notes (filename,word,link,data) " +
		"VALUES('"+name+"',?,?,?)"+
		" ON DUPLICATE KEY UPDATE data=VALUES(data)";

 	              PreparedStatement stmt = conn.prepareStatement(sql); 

		  stmt.setString(1, _word);
	              stmt.setString(2, _link);
	              stmt.setBytes(3, _data);

		  System.out.println("SAVING "+new String(_word.getBytes("UTF-8"))+" to notes");

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){System.out.println(esave.getMessage());}
     }



/////////////// REMOVE KEY /////////////////////
	 boolean removeKey(String name, String _word){
   
   try{

           int n = conn.createStatement().executeUpdate(
		"DELETE FROM notes WHERE filename='"+name+"' AND word like '"+_word+"'");

	System.out.println("Deleting "+_word+" in "+name+" with result "+n);

	if(n==0) return false;

    }catch( Exception e ) {return false; }

	return true;
	}

///////////////// GET DB FILE /////////////////////

	 byte[] getFile(String filename, String _word) throws Exception{

try{           
             rs = conn.createStatement().executeQuery(
		"SELECT data FROM notes WHERE filename='"+filename+"' and word like '"+_word+"'");

	                                   rs.next();
    }catch( Exception e ) {            
	System.out.println(e.getMessage()); 
    }
	return rs.getBytes("data");
    }
	//
}//	

