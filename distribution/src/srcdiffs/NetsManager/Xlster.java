package NetsManager;

import ServPak.jv.FileOps;

import java.io.*;

import java.util.*;
import java.util.zip.*;

import java.sql.*;


public class Xlster {
    static boolean test;
    static boolean test3;
    static String currentfiletype;
    static String ftype = "";
    static String filedescriptor = "";

     PrintWriter pout;
     StringBuilder buffout;
     StringBuilder pari;
     StringBuilder buffy;
     StringBuilder bufi;
    static Stack <String>stacy;
    static HashMap harry = new HashMap();

             Stack<String>refstrip = new Stack<String>();

    public static HashMap<String,Stack> dirrefs = new HashMap<String,Stack>();
    public static final HashMap<String, Integer> counters = new HashMap<String, Integer>(1);
    static Properties fileinfo = ZConnection.fileinfo;

    static String firstdir="";

             BufferedReader listin;

    int filecounter;
    int linecounter;

	String header;

    boolean firstflag;
    boolean nameindex;
    boolean end;

    Connection conn;

    public Xlster(byte[] stanly, String _direc, String _keyvalue, String _prekeyvalue) throws Exception {

	         conn = ZEdit.DOps.goMysql;

        buffout = new StringBuilder(8193);
        buffy = new StringBuilder(4097);
        bufi = new StringBuilder(4097);
        pari = new StringBuilder(16385);

        stacy = new Stack<String>();

        listin = new BufferedReader(new StringReader(new String(stanly)));

        String dirname = _direc.replace('/', '_');

        for (int q = 0; q < XCommands.values.length; q++)
            harry.put(XCommands.values[q], XCommands.keys[q]);

        firstflag = false;

        String pwd = ZEFMServer.hexi(_direc);
        String keyval = _keyvalue;
        String prekeyval = _prekeyvalue;
        StringTokenizer scale = new StringTokenizer(pwd, "/");

        int len = scale.countTokens();

        String dirscale = "";

        StringBuilder outpt = new StringBuilder(65);

        String tok = "";
        String viewtok = "";

        for (int qq = 1; qq < len; qq++) {
            tok = scale.nextToken();

            dirscale = dirscale + "/" + tok;

            viewtok = ZEFMServer.converter(tok);

            outpt.append(
		"<a href=" + dirscale + ">" + viewtok + "</a> / ");
        }

        tok = scale.nextToken();
        viewtok = ZEFMServer.converter(tok);

        outpt.append(
	"<a href=" + dirscale + "/" + tok + "><b>" + viewtok + "</b></a>\n");

        String ghost = fileinfo.getProperty("HOSTNAME");

        buffy.append("<html>\n");

        String lstfile = dirname + ".listing.html";

        for (String v; (v = listin.readLine()) != null;) {
            // READING LISTING
            test = false;
            test3 = false;

            if (keyval.equals("filetype")) {
                if (((v.indexOf("type=\"image\"") >= 0) ||
                        (v.indexOf("type=\"button\"") >= 0)) &&
                        (v.indexOf("td") >= 0) && (v.indexOf("input") >= 0)) {

                    String mainpart = v.substring(v.indexOf("value=\"") + 7);

                    int cut = mainpart.indexOf("\"");
                    mainpart = mainpart.substring(0, cut);

                    if (mainpart.indexOf(".") > 0) {
                        currentfiletype = mainpart.substring(mainpart.lastIndexOf(".") + 1);
                    } else {
                        currentfiletype = "none";
                    }

                    test3 = (!ftype.equals(currentfiletype));
                    ftype = currentfiletype;                                  
                }
            }

            if (v.indexOf("<tr") >= 0) {
                linecounter++;
            }

            if (v.indexOf("<html") >= 0) {
                continue;
            }

            if (v.indexOf("<body") >= 0) {
                buffy.append(v + "\n");

                ///////////////////// SET TOP LINE /////////////////////////////////
                buffy.append("\n<div>\n <div id=\"top\">\n");
	    buffy.append("<b>" + ghost + ": / " + outpt.toString() + "</b>");
                buffy.append("\n</div>\n");
                buffy.append("\n<div id=\"local\"><a href=home?home>");
	    buffy.append("<f>zefm@"+ZEFMServer.localhostname + "</f></a>\n");

            buffy.append("\n<div>\n<ul>\n");
	    buffy.append("<li><input type=\"button\"\n");
	    buffy.append("id=\"W\" class=\"x\" value=\"New File\"/></li>\n");

	    buffy.append("<li><input type=\"button\"\n");
	    buffy.append("id=\"S\" class=\"x\" value=\"Search String\"/></li>\n");

	    buffy.append("<li><input type=\"button\"\n");
	    buffy.append("id=\"F\" class=\"x\"  value=\"Find File\"/></li>\n");

	    buffy.append("<li><input type=\"button\"\n");
	    buffy.append("id=\"DB\" class=\"x\"  value=\"Text Search\"/></li>\n");

                buffy.append("</ul>\n</div>\n");
                buffy.append("\n</div>\n</div>\n &nbsp;<p/>");

                ///////////////////// SET SORT /////////////////////////////////
                buffy.append("\n<div id=\"global\">\n");
                buffy.append("\n<div id=\"options\">\n");
                buffy.append("<form action=get>\n");
                buffy.append(
                    "<input type=submit value=\"Sort by\" style=\"background-color: #ffffe0\"><br/>\n");
                buffy.append("<select name=\"" + pwd + "\">\n");

                Object[] iti = harry.keySet().toArray();

                Arrays.sort(iti);

                for (int q = 0; q < iti.length; q++) {
                    String sortkey = harry.get(iti[q]).toString();

                    buffy.append("<option>" + sortkey + "</option>\n");
                }

                buffy.append("</select>\n");
                buffy.append("</form>");
                buffy.append("<a class=\"u\" href=\"" + pwd +
                    "?update\"><f class=\"t\"> <b>Update</b>");
                buffy.append("<br/>(" + harry.get(keyval) + "/" + harry.get(prekeyval) + ") </f></a>");
                buffy.append("\n<div id='time'></div>\n</div>");

                ///////////////////////////// end Set Sort ////////////////////////////
                ////////////////////////// SET DIRECTORIES ////////////////////////
                File dirr = new File(_direc);

                String[] listdir = dirr.list();

                for (String w : listdir) {

                    if (w.startsWith(".")) {
                        continue;
                    }

                    File testit = new File(_direc + "/" + w);

                    if (testit.isDirectory()) {
                        stacy.push(w);
                    }
                }

                String[] dirlist = new String[stacy.size()];
		stacy.toArray(dirlist);

                Arrays.sort(dirlist);

                int numrows = (int) Math.round(dirlist.length / 4);
                int          tail = dirlist.length % 4;
	
	    buffy.append("\n\n<div id=\"table\">\n");
                buffy.append(
            "\n<table  cellspacing=\"2\" cellpadding=\"1\" align=\"center\" style=\"background-color: #ffffff\">\n");

                int cc = 0;

                String bcolor = "#ffffff";
                String color1 = "#f2f2f2";
                String color2 = "#ffffff";
                String aclass = "class=\"y\"";

                if (numrows > 0) {
                    for (int q = 1; q <= numrows; q++) {
                        buffy.append("<tr>\n");

                        for (int q0 = 1; q0 < 5; q0++) {

                            bcolor = (bcolor.equals(color2)) ? color1 : color2;
                            aclass = (bcolor.equals(color1)) ? "class=\"x\""
                                                                               : "class=\"y\"";

                            String dirltemp = dirlist[cc];
                            String href = pwd + "/" +
                                ZEFMServer.hexi(dirltemp);
                            buffy.append("<td "+ aclass +
		        "><a href=\"" + href +
                                "\">" + dirltemp + "</a></td>\n");
                            cc++;
                        }

                        buffy.append("</tr>\n");
                    }
                }

                if (tail > 0) {
                    buffy.append("<tr>\n");

                    for (int q = 1; q <= tail; q++) {

                        bcolor = (bcolor.equals(color2)) ? color1 : color2;
                        aclass = (bcolor.equals(color1)) ? "class=\"x\""
                                                                           : "class=\"y\"";
                        String dirltemp =  dirlist[cc];
                        String href = pwd + "/" + ZEFMServer.hexi(dirltemp);

                        buffy.append("<td "+ aclass + 
                            "><a href=\"" + href + "\">" +
                            dirltemp + "</a></td>\n");
    
                        cc++;
                    }

                    if (numrows > 0) {
                        for (int q = 1; q <= (4 - tail); q++) {
                            buffy.append("<td align=\"center\" bgcolor=" +
                                bcolor + "><br/></td>\n");
                            bcolor = (bcolor.equals(color2)) ? color1 : color2;
                            aclass = (bcolor.equals(color1)) ? "class=\"x\""
                                                                               : "class=\"y\"";
                        }
                    }
	                    buffy.append("</tr>\n");
                }

                buffy.append("</table>\n </div>\n");

                ///////////////////////////// end Set Directories ///////////////////////
                buffy.append("</div>\n\n");

                // closes topmatter
                filecounter = 0;

                continue;
            }

 //xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


	if(v.contains("<input type=\"button\"")) {

		int cut = v.indexOf("<input type=\"button\"");
		String xx = v.substring(cut+20);
		xx = xx.replaceFirst(">","/>");
		v = v.substring(0,cut)+"<input type=\"button\""+xx;
	}


	            v = v.replace("<br>","<br/>");

nameindex = ( ( linecounter == 15 ) 
			      ||   ( linecounter >15 && (linecounter % 25) == 24) );


	if(nameindex) {
	boolean valref = (v.indexOf("value")>-1 || v.indexOf("href")>-1) ;	          	

         	if( keyval.equals("filename") && valref ){
		String tst = "value";
		if(v.indexOf("href")>-1) tst = "href";
		int cut = v.indexOf(tst);
		String mark = v.substring(cut+tst.length()+2);
		mark = mark.substring(0, mark.indexOf('"')); 
		if(tst.equals("href")) mark = mark.substring(mark.lastIndexOf("/"));
		if(mark.length()>3) mark = mark.substring(0,4);
		filedescriptor = mark;		
	}

     }

	test = ( ( linecounter == 15 && v.indexOf("<tr") > -1 ) 
	      ||   ( linecounter >15 && (linecounter % 25) == 0 && v.indexOf("<tr") > -1 ) );

            if (keyval.equals("filetype")) test = test3;

            if (test) {

                filecounter++;

                String xmlrefweb = ZEFMServer.hexi(_direc + "^" + filecounter);

                String xxref = "GoFM.jav?" + xmlrefweb;

                if (keyval.equals("filetype")) {
                    filedescriptor = ftype;
                } else {
                if(!keyval.equals("filename")) filedescriptor = String.valueOf(filecounter);
                }

	    refstrip.push(filedescriptor);

                ////////////////
                if (!firstflag) {
                    buffy.append("</table>\n</form>\n");
                    buffy.append("<reference>\n\n</reference>\n");
                    buffout.append(buffy.toString());
                }

                if (firstflag) {
	      if(keyval.equals("filetype")) bufi.append("</tr>\n");
                    bufi.append(" </table>\n</main>");
                    bufi.append("<reference>\n\n</reference>\n");

                    pari.append(bufi.toString());
                }

                if (!firstflag) {
                    firstflag = true;
                }

                bufi = new StringBuilder();

	   

	if(filecounter==1) {

                  header = "<?xml version=\"1.0\"?>\n"
+"<?xml-stylesheet type=\"text/xsl\" href=\"ServPak/xsl/tpw.xsl\"?>\n"
+"<!DOCTYPE zefmdir [<!ENTITY % tpwsymbols SYSTEM \"file:ServPak/xsl/TPW\"> %tpwsymbols;]>"
+"\n<zefmdir>\n<HEADER1>\n<main>\n";
	
	} else {

	     int prev = filecounter-1 ;

	     header = "\n</HEADER"+prev+">\n<HEADER"+filecounter+">\n<main>\n";

	}

                pari.append(header);

                ///////////////////////////////////////////////////////////////////////////////////
                bufi.append(
                    "<table align=\"center\" width=\"98%\" cellpadding=\"0\" cellspacing=\"0\">\n");
                bufi.append("<tr><th width=\"30%\">Filename</th>");
                bufi.append("<th width=\"25%\">Size &#160;  &#160;  Date &#160; &#160;  Time</th>");
                bufi.append("<th width=\"35%\">Notes</th>\n");
                bufi.append("</tr>\n");

	    if(keyval.equals("filetype")) bufi.append("<tr class=\"a\">\n");

                bufi.append(v + "\n");

                continue;
            }

            // xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

	if(v.trim().equals("</form>") || v.trim().equals("</html>") || v.trim().equals("</body>") ) continue;

           if (firstflag) {	    
                bufi.append(v + "\n");
            }

            if (!firstflag) {
                buffy.append(v + "\n");
            }
        }

        if (firstflag) {  
               pari.append(bufi.toString());
        }

        if (pari.length() != 0) {
            pari.append(("\n</main>\n<reference>\n</reference>\n"));
            pari.append("</HEADER"+filecounter+">\n</zefmdir>");
	
	ZEFMServer.Zipper(conn, dirname + ".xml", pari.toString().getBytes(), "xml");

        }

        if (!firstflag) {
                    buffout.append(buffy.toString());
        }

        if (keyval.equals("filetype")) {
            buffout.append("<p><hr><p><center><b>File Types</b></center><p>\n");
        }

        counters.put(_direc, filecounter); 

        if(firstdir.length()==0) firstdir = _direc;

        if(dirrefs.size()>10) {
		dirrefs.remove(firstdir);
		String[] kys = new String[dirrefs.size()];
		dirrefs.keySet().toArray(kys);
		firstdir = kys[0]; 
	}

        dirrefs.put(_direc,refstrip);

        buffout.append(reffout(_direc,keyval));
        buffout.append("\n</body>\n</html>\n");

        ZEFMServer.goSave(conn, lstfile, buffout.toString(), "listings");
	if(!ZConnection.bgupdate){
			       ZConnection.out.write(buffout.toString().getBytes());
			       ZConnection.out.flush();
	}
    }

///////////////////////////////////////////////////////
//////////////////////// REFFOUT /////////////////////
//////////////////////////////////////////////////////

	public String reffout(String dirc, String mode){
		return reffout(dirc,mode,filecounter);
	}

	public static String reffout(String dirc, String mode, int cutoff){
	
	List stky = dirrefs.get(dirc).subList(0,cutoff);

	int local = stky.size();

	String[] descrips = new String[local];
	stky.toArray(descrips);

	StringBuilder sb = new StringBuilder("<table align=\"center\" class=\"ww\"><tr>");
	String xxref = "";
	String filedescriptor = "";

	for (int q=0;q<local;q++){

		filedescriptor = descrips[q];

		int qplus =q+1;

	                xxref = "GoFM.jav?" + ZEFMServer.hexi(dirc + "^" + qplus);
	
                String aref = (mode.equals("filetype") || mode.equals("filename")) ? filedescriptor
                                                          : (filedescriptor + " | ");

                sb.append("<td><a href=\"");
	    sb.append(xxref);
                sb.append("\" class=\"pgref\">" + aref + "</a></td>");

                if (q>0 && (q % 10) == 0) {
                    sb.append("</tr><tr>");
                }
  		}
            sb.append("</tr></table>");
		return sb.toString();
	}
}
