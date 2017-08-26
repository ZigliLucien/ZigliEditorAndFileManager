package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.util.*;
import java.sql.*;

import javax.swing.*;
import javax.swing.event.*;


public class Alphabet {
    static JTextField jot;
	public    static String fontFamily;
	public    static int fontSize;
    static String filename;
    static String inword;
    static String wordout;
    static String langname;

    static JMenuItem jimi;

    static int locx;
    static int locy;

    public static HashMap alphmap;

 	public   int[] strokes;
	public   int[] modifiers;
	public   String[] outstrokes;
	public   String wordkey;

	static ResultSet rs;

    public Alphabet(String _languageName) {

        Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

        locx = (scrsize.width) / 5;
        locy = (scrsize.height) / 2;

        String[] strkes;

        try {

            filename = _languageName + ".keymap";

            Properties keymap = new Properties();

            ZEditor.putFile("keymap/" + filename, "Keymaps/" + filename);

            InputStream inkeys = new FileInputStream("Keymaps/" + filename);
            keymap.load(inkeys);

            strkes = new String[keymap.size()];
            strokes = new int[keymap.size()];
            modifiers = new int[keymap.size()];
            outstrokes = new String[keymap.size()];

            alphmap = new HashMap();

            int q = 0;

            for (Enumeration e = keymap.propertyNames(); e.hasMoreElements();) {
                strkes[q] = e.nextElement().toString();
                q++;
            }

            Arrays.sort(strkes);

            for (int qq = 0; qq < strokes.length; qq++) {
                modifiers[qq] = Event.ALT_MASK;

                String localstroke = keymap.getProperty(strkes[qq]);
                String locstroke = strkes[qq];

                if (locstroke.endsWith("S")) {
                    modifiers[qq] = Event.ALT_MASK | Event.SHIFT_MASK;
                    locstroke = locstroke.substring(0, locstroke.indexOf("S"));
                }

                if (locstroke.endsWith("C")) {
                    modifiers[qq] = Event.ALT_MASK | Event.META_MASK;
                    locstroke = locstroke.substring(0, locstroke.indexOf("C"));
                }

                if (localstroke.length() < 7) {
                    outstrokes[qq] = String.valueOf((char) Integer.parseInt(localstroke)) + "*";
                } else {
                    int firstpart = Integer.parseInt(localstroke.substring(0, 4));
                    int secondpart = Integer.parseInt(localstroke.substring(4, 8));

                    outstrokes[qq] = String.valueOf((char) firstpart) +
                        String.valueOf((char) secondpart) + "*";
                }

                alphmap.put(strkes[qq],
                    outstrokes[qq].substring(0, outstrokes[qq].indexOf("*")));

                int zstrkes = Integer.parseInt(locstroke);

                strokes[qq] = zstrkes;
            }
        } catch (Exception ioe) {
	System.out.println(ioe.getMessage());
            System.out.println("Keymap missing!");
        }
    }

	//////////////// DICTIONARYIN ///////////////////

    public static void dictionaryin(String langName, String _inword, Connection _conn) {
        // DictIn

		 rs = null;

        try {

	langname = langName;

            boolean isInDictionary = false;

try{
		     inword = _inword.trim();

    String sql = 
         "SELECT data FROM dictionaries WHERE lang='"+langname+"' AND word like ?";

		PreparedStatement stmt = _conn.prepareStatement(sql); 
			       stmt.setString(1, inword);	
			rs = stmt.executeQuery();

}catch(Exception dbex){ System.out.println(dbex.getMessage()); }

	 isInDictionary = rs.next();

            JPanel pl = new JPanel();
            pl.setLayout(new GridLayout(3, 1));
            pl.add(new JLabel(
                    "Separate translations by commas. Enter to keep or add to current entry."));

            jot = new JTextField(20);

            jot.setFont(new Font(fontFamily, Font.BOLD, fontSize));
            pl.add(jot);

	JButton jub = new JButton(
		"<html><center>Click Here to Delete Entry <p>"+
		"<i>Also, closing the window will delete the entry</i></center></html> ");
	jub.setBackground(Color.lightGray);
	
	pl.add(jub);

            final JFrame jff = new JFrame(langname + " adding " + inword);
            jff.add(pl);

            jot.addKeyListener(new KeyAdapter() {
                    public void keyPressed(KeyEvent e) {
                        if ((e.getKeyCode() == KeyEvent.VK_Q) &&
                                e.isControlDown()) {
                            jff.dispose();
                        }
                    }
                });
            jot.requestFocus();
            jff.setLocation(locx, locy);
            jff.pack();
            jff.setVisible(true);

            jub.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent e) {     
                        jff.dispose();
                    }
                });

            if (!isInDictionary) {
	                wordout = "";
            } else {    

	String sql = 
	         "DELETE FROM dictionaries WHERE lang='"+langname+"' AND word like ?";
	PreparedStatement stmt = _conn.prepareStatement(sql); 
			           stmt.setString(1, inword);	
		           int n = stmt.executeUpdate();
			stmt.close();

	          System.out.println("Deleting "+inword+" from "+langname+" dictionary with result "+n);

            	    wordout = new String(rs.getBytes("data"),"UTF-8") + ",";
            }

	jot.setText(wordout);

	final Connection cnn = _conn;

            jot.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent e) {

	   	     wordout = jot.getText();
		     if(wordout.endsWith(",")) wordout = wordout.substring(0,wordout.length()-1);	
		     wordout = wordout.trim();

     try{

	 String sql =   "INSERT INTO dictionaries(lang,word,data) " +
		          "VALUES('"+langname+"',?,?)"+
		          " ON DUPLICATE KEY UPDATE data=VALUES(data)";

 	              PreparedStatement stmt = cnn.prepareStatement(sql); 

		  stmt.setString(1, inword);
	              stmt.setBytes(2,  wordout.getBytes("UTF-8"));

		System.out.println("SAVING "+new String(inword.getBytes("UTF-8"))+" to dictionary");

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){}
      
                        jff.dispose();
		
                    }
                });
        } catch (Exception alphex) {
            System.out.println(alphex.getMessage());
        }
    }

	//////////////// DICTIONARYOUT ///////////////////

    public String[] dictionaryout(String langName, String searchword, Connection _conn) {
        // DictOut
        Stack <String>stac = new Stack<String>();
         searchword = searchword.trim();

        try {

          String result = "";
 

	String sql = 
			"SELECT word,data FROM dictionaries "+
			" WHERE lang='"+langName+"' AND word like ?";

		PreparedStatement stmt = _conn.prepareStatement(sql); 
			       stmt.setString(1, searchword);	
			rs = stmt.executeQuery();
			rs.next();	

	result = new String(rs.getBytes("data"),"UTF-8");
	this.wordkey =  rs.getString("word");

            String[] stin = result.split(",");
            for(String v : stin) stac.push(v);

        } catch (Exception alphoutex) {}

	String[] out = new String[stac.size()];
	stac.toArray(out);

        return out;
    }
}
