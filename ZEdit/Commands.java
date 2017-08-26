package ZEdit;

import NetsManager.*;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import javax.swing.*;
import java.sql.*;


public class Commands extends TPEditorX {
    public static String xmldoc;
    static String args;
    static final String[] programs = {
        "Perl", "PDFTeX", "PDFLaTeX", "Clsv", "XML", "Jxml", "HTML", "PS",
        "JavaDoc", "Java"
    };
 	public   static final int numapps = programs.length - 1;

    //Class
    String cmd;
    String buffr;
    String title;
	public    String confirmString;
    String textlabel;
    String currentfile;
    String direc;
 	public   int which = -1;

	public    Commands(String _cmd) {
        this(_cmd, null, null, null);
    }

 	public   Commands(String _cmd, String _buffr, String _currentfile, String _direc) {
        this.cmd = _cmd;
        this.buffr = _buffr;

	if(_currentfile.endsWith(".styl")) {
		       this.currentfile = _currentfile.substring(0,_currentfile.lastIndexOf(".styl"));
	} else {
		        this.currentfile = _currentfile;
	}

        this.direc = _direc;

        textfill = new JTextField(40);

        readCmd();

        if ((which == 0) || (which == numapps)) {
            sml = new JPanel();
            sml.add(textfill);
            textfill.setText(args);
            dialog = new QuickDialog(this, title, sml, confirmString, textlabel);

            textfill.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent e) {
                        go(which);
                    }
                });
        }
    }

    void readCmd() {
        String apprun;

        apprun = cmd.substring(cmd.indexOf(" ") + 1);

        title = apprun + " Command Line";
        confirmString = "Go " + apprun;
        textlabel = "Enter command line arguments";

        for (int q = 0; q < programs.length; q++) {
            if (programs[q].equals(apprun)) {
                this.which = q;

                break;
            }
        }
    }

	public    void go(int whch) {
        switch (whch) {
        case (0):
            goPerl();

            break;

        case (1):
            goPDFTeX();

            break;

        case (2):
            goPDFLaTeX();

            break;

        case (3):
            goClsv();

            break;

        case (4):
            goXML();

            break;

        case (5):
            goJxml();

            break;

        case (6):
            goHTML();

            break;

        case (7):
            goPS();

            break;

        case (8):
            goJavaDoc();           

            break;

        case (9):
            goJava();          

            break;

        default:
            return;
        }
    }

    // Application runs
    void goPerl() {
        args = textfill.getText();

        try {
            runIt("perl " + this.currentfile + " " + args);

            this.savePage(this.currentfile);
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }
    }

    void goJava() {
        args = textfill.getText();

        String javarun = this.currentfile.substring(this.currentfile.lastIndexOf(
                    "/") + 1, this.currentfile.indexOf("."));

        try {
            runIt("java -classpath " + this.direc + " " + javarun + " " + args);
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }

        this.savePage(this.currentfile);
    }

//////////////// GO PDFTEX //////////////

    void goPDFTeX() {
        String name = this.currentfile.substring(1 +
                this.currentfile.lastIndexOf("/"), this.currentfile.indexOf("."));

        runIt("pdftex -interaction=nonstopmode " + this.currentfile);

        try {
            File out = new File(name + ".pdf");
            System.out.println("PDFTeX: " + this.direc);

            copy(out, this.direc + "/" + name + ".pdf", true);
            copy(out, this.direc + "/" + name + ".aux", true);

            String[] erasem = { ".log", ".dvi", ".toc" };

            for (String v : erasem) {
                String filestogo = name + v;
                new File(filestogo).delete();
            }
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }

        System.out.println("PDF file available");

        this.savePage(this.currentfile);
    }

    void goPDFLaTeX() {
        String name = this.currentfile.substring(1 +
                this.currentfile.lastIndexOf("/"), this.currentfile.indexOf("."));

        runIt("latex -interaction=nonstopmode " + this.currentfile);
        runIt("pdflatex -interaction=nonstopmode " + this.currentfile);

        try {
            File out = new File(name + ".pdf");
            System.out.println("PDFLaTeX: " + this.direc);

            copy(out, this.direc + "/" + name + ".pdf", true);
            copy(out, this.direc + "/" + name + ".aux", true);

            String[] erasem = { ".log", ".dvi", ".toc" };

            for (String v : erasem) {
                String filestogo = name + v;
                new File(filestogo).delete();
            }
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }

        System.out.println("PDF file available");

        this.savePage(this.currentfile);
    }

/////////////// GO PS ///////////////

    void goPS() {
        String name = 
	this.currentfile.substring(1 + this.currentfile.lastIndexOf("/"), this.currentfile.indexOf("."));
        String inname = this.currentfile.substring(0, this.currentfile.lastIndexOf("."));
        String outfile = name + ".ps";

        try {
            runIt("dvips " + inname + ".dvi");

            System.out.println("DVIPS: " + this.direc);

            copy(outfile, this.direc + "/" + name + ".ps", true);
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }

        System.out.println("PS file available");

        this.savePage(this.currentfile);
    }

////////// Go CLSV /////////////

    void goClsv() {
        try {
            String prename = this.currentfile.substring(0,
                    this.currentfile.lastIndexOf("."));

            outname = prename + ".xml";

            Clsv pretable = new Clsv(this.buffr, outname);

            new Traxit(pretable.xmltext, "ServPak/xsl/generic.xsl", prename + ".html");
        } catch (Exception e) {
        } finally {
            dialog.dispose();
        }

        this.savePage(this.currentfile);
    }

///////////// GO XML //////////

    void goXML() {
        String prename = this.currentfile.substring(0, this.currentfile.lastIndexOf("."));

        String ext = ".html";

        if (TPEditorX.jxml) {
            ext = ".java";
            TPEditorX.stylefile = "ServPak/xsl/javajava.xsl";
        }

        TPEditorX.outfile = prename + ext;

        setGoJMenu(TPEditorX.outfile);

        try {

			StringBuilder bfr = new StringBuilder();
	if(TPMLCheck(currentfile)) {
			bfr = Plugins.GoXML.goTPML(currentfile);
			TPEditorX.stylefile = "ServPak/xsl/tpw.xsl";

		            new NetsManager.Traxit(bfr, TPEditorX.stylefile, currentfile);
	} else {
		            new NetsManager.Traxit(currentfile);
	}

	FileOutputStream fout = new FileOutputStream(TPEditorX.outfile);
	fout.write(NetsManager.Traxit.tabby);
	fout.flush();
	fout.close();

        } catch (Exception e) {
        } finally {
            dialog.dispose();
        }

        this.savePage(this.currentfile);

        TPEditorX.jxml = false;
        TPEditorX.stylefile = null;
    }

/////////////// GO JXML ////////////

    void goJxml() {
        String prename = this.currentfile.substring(0,
                this.currentfile.lastIndexOf("."));

        String ext = ".jxml";

        String processfile = this.currentfile;

        String localout = prename + ext;

        runIt("perl ServPak/pl/jv2jxml.pl " + processfile);

        String name = localout.substring(1 + localout.lastIndexOf("/"),
                localout.indexOf("."));

        try {
            copy(name + ".jxml", this.direc + "/" + name + ".jxml", false);
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }

        setGoJMenu(localout);

        TPEditorX.outfile = processfile;

        this.savePage(this.currentfile);
    }

    void goHTML() {
        try {
            runIt("netscape -remote 'openURL(" + this.currentfile + ")' ");
        } catch (Exception ex) {
        } finally {
            dialog.dispose();
        }
    }

    void goJavaDoc() {
        try {
            String preoutfile = 
		currentfile.substring(currentfile.lastIndexOf("/") + 1, currentfile.lastIndexOf("."));

            BufferedReader buff = new BufferedReader(new FileReader(currentfile));
            String v = "";

            while ((v = buff.readLine()) != null) {
                if (v.trim().length() == 0) {
                    continue;
                }

                break;
            }

            if (v.indexOf("package") >= 0) {
                v = v.substring(v.indexOf("package") + 7, v.indexOf(";")).trim();
                preoutfile = v + "." + preoutfile;
            }

            outfile = preoutfile + ".xml";

            if (new File("DOX/UnCommented/" + outfile).exists()) {
                System.out.println(
                    "Use your browser to continue at DOX/UnCommented/ " +
                    outfile);

                return;
            }

            com.sun.tools.javadoc.Main.execute(new String[] {
                    "-package", "-breakiterator", "-sourcepath", ".", "-doclet",
                    "Jvmaker", this.currentfile
                });
            copy(outfile, "DOX/UnCommented/" + outfile, true);
        } catch (Exception ex) {
        } finally {
            dialog.dispose();

            return;
        }
    }

    /////////////////////// SAVE PAGE ////////////////////		 
    public void savePage(String filename) {
        if (filename.indexOf("*") > 0) {
            if (filename.endsWith(".tmp.tmp*")) {
                filename = filename.substring(0, filename.indexOf("*"));
            } else {
                filename = filename.substring(0, filename.indexOf("*"));
                filename += ".tmp";
            }
        }

        try {
            FileOutputStream fo = new FileOutputStream(filename);

            fo.write(this.buffr.getBytes("UTF-8"));
            fo.flush();
            fo.close();

            setGoJMenu(filename);
        } catch (IOException ioe) {
            return;
        }
    }

    public static void copy(String infile, String tofile, boolean move) {
        copy(new File(infile), tofile, move);
    }

    /////////////////////// COPY //////////////////
    public static void copy(File infile, String tofile, boolean move) {
        try {
            FileInputStream fins = new FileInputStream(infile);
            byte[] conts = new byte[fins.available()];
            FileOutputStream fout = new FileOutputStream(tofile);
            fins.read(conts);
            fout.write(conts);
            fout.flush();
            fout.close();

            String outword = (move) ? "Moving" : "Copying";

            System.out.println(outword + " " + infile + " to " + tofile);

	if(move) {
try{
		Connection conn = DOps.goMysql;
		String inf = infile.toString();
             	String dirc = inf.substring(0, inf.lastIndexOf("/"));
		String prereq = dirc.replace('/', '_') + "." + inf.substring(inf.lastIndexOf("/") + 1);

		if(DOps.testKey(conn,prereq,"annotations")){
		String note = DOps.res.getString("data");

		ZEFMServer.removeKey(conn, prereq,"annotations");

	            String filename = tofile.substring(tofile.lastIndexOf("/") + 1);
             	     dirc = tofile.substring(0, tofile.lastIndexOf("/"));
            	     prereq = dirc.replace('/', '_') + "." + filename;

		DOps.goSaveText(conn, prereq,note,"annotations");
	}

	}catch(Exception eee){ 	
			new DOps(); 
	}
   		}

            if (move && !infile.delete()) {
                System.out.println(infile + " not removed.");
            }
        } catch (Exception eio) {
            return;
        }
    }
	///////////// TPML Check ////////////////
	boolean TPMLCheck(String filename) throws Exception{
	
	boolean result = false;
	String v = "";

		BufferedReader buf = new BufferedReader(new FileReader(filename));
		for(int q=0;q<5 && v !=null;q++) {
			v = buf.readLine();
			if(v.contains("tpw.xsl") || v.contains("<tpwm>")) result = true;		
		}

	return result;
	}
}