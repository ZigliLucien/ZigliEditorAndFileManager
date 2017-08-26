package ServPak.jv;

import NetsManager.Traxit;
import NetsManager.XCommands;
import NetsManager.ZEFMServer;

import java.io.*;
import java.util.*;
import java.net.*;


public class DBM {

    static BufferedReader buff;
    public static final String zefmhome = "zefm@" + ZEFMServer.localhostname;
    public String printout;
    HashMap<String,String> data = new HashMap<String,String>();
    HashSet keyfields = new HashSet();
    int numlines = 0;
    String dbasename;

    /////////////////////// DBM /////////////////////////////////
    public DBM(String query) throws Exception {
        if (query.indexOf("savetable") >= 0) {
            savetable(query);

            StringBuilder prtout = new StringBuilder("<html>\n<head><title>" +
                    dbasename + "</title></head>\n<body>\n");

            prtout.append(
                "<p>&nbsp;<p>&nbsp;<p>&nbsp;<p>&nbsp;&nbsp;&nbsp;&nbsp;\n");
            prtout.append("<u>" + dbasename +
                ".sdb.xml</u>&nbsp; <i>has been copied to</i>&nbsp;<u>" +
                dbasename + ".xml</u>\n");
            prtout.append("<p>&nbsp;<p><a href=" + dbasename + ".sdb>");
            prtout.append("Return to Search/Sort</a><p>\n");
            prtout.append("<a href=\"DBgo.jav?tablename=" + dbasename);
            prtout.append("&newtable=\">Return to Table Edit </a><p>\n</body></html>");
            printout = prtout.toString();

            return;
        }

        boolean bool = false;

        if (query.endsWith("=GO")) {
            query = query.substring(0, query.indexOf("=GO"));

            String subquery = query.substring(0, query.indexOf("&sortdefault"));
            String[] tok = subquery.split("&|=");
            String cats = "";

	for(int q=0;q<tok.length;q=q+2) cats += tok[q] + ",";

            cats = cats.substring(0, cats.length() - 1);
            data.put("categories", cats);
            bool = true;
        }

        query = converter(query);

        String[] toks = query.split("&");

	for (String mark : toks) {

            String kee = mark.substring(0, mark.indexOf("="));
            String valu = mark.substring(mark.indexOf("=") + 1);

            data.put(kee, valu);
        }

        dbasename = data.get("dbase");

	try{
	new NetsManager.Query(
		new FileInputStream("DB/" + dbasename + ".xml"), "for $i in /*/* return $i");
	}catch (Exception ee){ }

	BufferedReader buff = new BufferedReader(
		new StringReader(NetsManager.Query.qtabby.toString()));

        PrintWriter pw = new PrintWriter(new FileWriter("DB/" + dbasename + ".xml"), true);

        String sortdef = data.get("sortdefault");
        String[] catz = data.get("categories").split(",");

        for(String v : catz) keyfields.add(v);

        String rootname;

        if (bool) {
            rootname = dbasename.substring(dbasename.lastIndexOf("/")+1);
        } else {
            rootname = data.get("root");
        }

        StringBuilder sbuild = new StringBuilder();

        sbuild.append("<?xml version=\"1.0\"?>\n");
        sbuild.append("<" + rootname + ">\n");

        String[] elements = data.get("fields").split(",");

            String v;
	String f = "";

	int numfields = elements.length+1;

	int cc =  0;
	int ccc = 0;

            String entryname = data.get("entry");

            while ((v = buff.readLine()) != null) {

	ccc = (cc % numfields);
	cc++;

if(ccc>0){

   	   if(ccc==1) {
			sbuild.append("\n<" + entryname + ">\n");
	           		numlines++;
		}
             	        f = elements[ccc-1];
    
	    String ky = v;
                String kyref = XCommands.hexml(ky);

                ky = ZEdit.MailFiles.ampcheck(ky);

                if (keyfields.contains(f)) {
                    sbuild.append(
			       "<" + f + " key=\"" + f + kyref + "\">" + ky + "</" + f + ">\n");
                } else {
                    sbuild.append("<" + f + ">" + ky + "</" + f + ">\n");
                }
      } else {
	if(cc>1) {
		            sbuild.append("</" + entryname + ">\n");
		}
	}
        }

        sbuild.append("</" + entryname + ">\n");
        sbuild.append("\n</" + rootname + ">");
        pw.print(sbuild.toString());
        pw.close();

        new Traxit("DB/" + dbasename + ".xml", "ServPak/xsl/dbmrun.xsl");

        String currentTable = new String(Traxit.tabby);

        currentTable = currentTable.substring(currentTable.indexOf("?>") + 3);

        PrintWriter prtw = new PrintWriter(new FileWriter("DB/" + dbasename + ".sdb"), true);

        StringBuilder dbmbufr = new StringBuilder();
        String locdirec = ZEFMServer.localdir;

        if (locdirec.indexOf(":") > 0) {
            int q = locdirec.indexOf(":");

            locdirec = locdirec.substring(q + 1);
            locdirec = locdirec.replace('\\', '/');
        }

        dbmbufr.append("<html>\n");
        dbmbufr.append("<head><title> Search " + dbasename + " </title>\n");
        dbmbufr.append("<style type=\"text/css\">\n");
        dbmbufr.append("input { color: green; background-color: white}\n");
        dbmbufr.append("input.res { color: darkblue; background-color: white}\n");
        dbmbufr.append("option { color: white; background-color: blue}\n");
        dbmbufr.append("</style>\n");
        dbmbufr.append("</head>\n");
        dbmbufr.append("<body>\n");
        dbmbufr.append("<h1> Search</h1>\n");
        dbmbufr.append(
            "Click on the field you wish to search on. Select from the available choices.\n");
        dbmbufr.append("<p>\n");
        dbmbufr.append("<form method=\"get\">\n");

        Arrays.sort(catz);

        LineNumberReader linenumberreader = 
		new LineNumberReader(new StringReader(currentTable));

        for (String w : catz) {

            dbmbufr.append(
"<span style=\"background-color:white\"> &#160;" + DBgo.dataCheck(w) + " &#160; </span> \n");
            dbmbufr.append("<select name=\"" + w + "\">\n");
            dbmbufr.append("<option> ALL </option>\n");

            HashSet hashset = new HashSet();

            while (linenumberreader.getLineNumber() < numlines) {
                String countLine = linenumberreader.readLine();

                if (hashset.add(countLine)) {
                    dbmbufr.append(countLine + "\n");
                }
            }

            linenumberreader.setLineNumber(0);
            dbmbufr.append("</select>&nbsp;&nbsp;&nbsp;&nbsp;\n");
        }

        dbmbufr.append("<p>&nbsp;<br>\n");
        dbmbufr.append("Primary Sort: <select name=\"Sort\">\n");
        dbmbufr.append("<option value=" + sortdef + "> " + DBgo.dataCheck(sortdef) + " </option>\n");

        for (String w : catz) {
            if (!w.equals(sortdef)) {
                dbmbufr.append("<option value=" + w + "> " + DBgo.dataCheck(w) + " </option>\n");
            }
        }

        dbmbufr.append("</select>&nbsp;&nbsp;&nbsp;&nbsp;\n");
        dbmbufr.append("Secondary Sort: <select name=\"Sort\">\n");
        dbmbufr.append("<option value=" + sortdef + ">" + DBgo.dataCheck(sortdef) + "</option>\n");

        for (String w : catz) {
            if (!w.equals(sortdef)) {
                dbmbufr.append("<option value=" + w + "> " + DBgo.dataCheck(w) + " </option>\n");
            }
        }

        dbmbufr.append("</select>\n");
        dbmbufr.append("<p>&nbsp;<br>\n");
        dbmbufr.append(
            "<center><input type=submit value=\"SEARCH/VIEW\"></center><p><input type=reset class=res>\n");
        dbmbufr.append("</form>\n");

        if (bool) {
            dbmbufr.append(
		"<p/>&nbsp;<p><a href=DBM.jav?savetable=" + dbasename + ">");
            dbmbufr.append(
                "\\/\\/\\/\\ <b>Save</b> Sorted Table to Original File (<i> overwrites original table </i>) /\\/\\/\\/ ");
            dbmbufr.append("</a><p/>");

dbmbufr.append("<a href=\"DBgo.jav?tablename=" + dbasename 
		   + "&newtable=\">Back to Edit Table</a><p>\n");
            dbmbufr.append("<a href=\"" + locdirec +
                "/HTML/zserve.html\"> Back to " + zefmhome + "</a><p>\n");
        }


        dbmbufr.append("</body>\n");
        dbmbufr.append("</html>\n");
        prtw.print(dbmbufr.toString());
        prtw.close();
  
        String fileref = locdirec + "/DB/" + dbasename;

	sbuild = 
	new StringBuilder(
"<html><head><meta http-equiv=\"refresh\" content=\"url=0;"+fileref+".sdb\"></head>\n");
        sbuild.append("<html><body><p>&nbsp;<p>&nbsp;<p>&nbsp;<p><center> <a href=");
        sbuild.append(fileref + ".sdb> <font size=+2>Go To <b>");
        sbuild.append(dbasename.toUpperCase() + "</b></font></a></center></body></html>");
	printout = sbuild.toString();
    }

    void savetable(String in) {
        dbasename = in.substring(in.indexOf("=") + 1);

        try {
            FileInputStream fins = new FileInputStream("DB/" + dbasename + ".sdb.xml");
            byte[] conts = new byte[fins.available()];

            fins.read(conts);

            FileOutputStream fl = new FileOutputStream("DB/" + dbasename + ".xml");

            fl.write(conts);
            fl.flush();
            fl.close();
        } catch (Exception ioex) {
        }
    }

    //////////////// CONVERTER /////////////////////
    public static String converter(String string) {

        String x;
        String y;
        String z;

        for (/**/; string.indexOf("%") >= 0;
                string = x + y + z) {
            int i = string.indexOf("%");

            x = string.substring(0, i);
            y = string.substring(i + 1, i + 3);
            z = string.substring(i + 3);

            int q = ((16 * Byte.parseByte(y.substring(0, 1), 16)) +
                Byte.parseByte(y.substring(1, 2), 16));

            y = String.valueOf((char) q);
        }

        return string;

    }

    /////////////////////// FIXGTLT //////////////////////
    public static String fixgtlt(String string) {
        char[] cs = string.toCharArray();
        String y = "";

        for (int i = 0; i < cs.length; i++) {
            if (cs[i] == '<') {
                y += "&lt;";
            } else if (cs[i] == '>') {
                y += "&gt;";
            } else if (cs[i] == '\"') {
                y += "&quot;";
            } else {
                y += String.valueOf(cs[i]);
            }
        }

        return y;
    }
}