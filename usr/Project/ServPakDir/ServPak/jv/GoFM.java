package ServPak.jv;

import NetsManager.XCommands;
import NetsManager.Xlster;
import NetsManager.ZEFMServer;
import NetsManager.ZConnection;
import NetsManager.Traxit;

import java.io.*;
import java.util.*;
import java.util.zip.*;

import java.sql.*;
import java.net.URLDecoder;

public class GoFM {

    static BufferedReader buffr;
    static final String vvv = "<input type=\"radio\" name=\"fileops\" value=\"VVV\"";
    static final String ccc = "<input type=\"radio\" name=\"fileops\" value=\"CCC\"";
    static final String mmm = "<input type=\"radio\" name=\"fileops\" value=\"MMM\"";
    static final String xxx = "<input type=\"radio\" name=\"fileops\" value=\"XXX\"";
    static final String eee = "<input type=\"radio\" name=\"fileops\" value=\"EEE\"";
    static final String qqq = "<input type=\"radio\" name=\"fileops\" value=\"QQQ\"";
    static final String aaa = "<input type=\"radio\" name=\"fileops\" value=\"AAA\"";

    String reqreq;
    public static String dirname;
    public static String dirnum;

      ResultSet rs;
      Connection conn;

	public String printout="";

    public GoFM(String linein) throws Exception {

try{
		conn = ZEdit.DOps.goMysql;
	}catch(Exception ee){
		new ZEdit.DOps();
	}

         if(linein !=null) dirname = linein.substring(0, linein.indexOf("^"));

        dirname = URLDecoder.decode(dirname, "UTF-8");

        if(linein != null) dirnum = linein.substring(linein.indexOf("^") + 1);

        String lstfile = dirname.replace('/', '_') + ".listing.html";

        String localprocess = ServPak.jv.FileOps.processcall;

        if (localprocess == null) {
            localprocess = "VVV";
        }

        if (dirnum.equals("0")) {
            StringBuilder bufi = new StringBuilder(6145);

	buffr = new BufferedReader(getStream(lstfile, "listings"));

            for (String v; (v = buffr.readLine()) != null;) {
                if (v.indexOf("form action=\"FileOps.jav") >= 0) {
                    fillChecked(bufi, localprocess, dirname);

                    continue;
                }

                bufi.append(v + "\n");
            }
	          ZConnection.out.write(bufi.toString().trim().getBytes());
	          ZConnection.out.flush();

	           	return;
        }

        reqreq = XCommands.reqfile;
        String listfile = dirname.replace('/', '_') + ".xml"; 

        try {
                                  int i = Xlster.counters.get(dirname);

             StringBuilder bufi = new StringBuilder(6145);

bufi.append("<html>\n");
bufi.append("<head>\n");
bufi.append("<link rel=\"stylesheet\" type=\"text/css\""); 
bufi.append(" href=\""+ZEFMServer.userdir+"/ServPak/css/listing.css\"/>\n");
bufi.append("<script type=\"text/javascript\""); 
bufi.append(" src=\""+ZEFMServer.userdir+"/ServPak/js/listing.js\"></script>");
bufi.append("</head>\n");
bufi.append("<body bgcolor=\"#ffffff\" oncontextmenu=\"return false\" onload=\"setup()\">");


                    bufi.append(
                        "<p align=right><a class=\"w\" href=\"GoFM.jav?" +
                        dirname + "^0\"> Top </a></p>\n");
                    bufi.append("<p align=right><a class=\"w\" href=GoFM.jav?" +
                        dirname + "^" + i + "> Bottom </a><br/><div id='time' style='float:right'></div></p>\n");
                    bufi.append("<h2>" + dirname + " : Listing " + dirnum + "</h2>\n");

                    fillChecked(bufi, localprocess, dirname);

		String main = "";

	String qry = new String(
"<html>\n<body>\n { let $part := \"HEADER"+dirnum+"\"\n for $i in //*[name()=$part]\n return $i/node()}\n</body>\n</html>");

		new NetsManager.Query(getBits(listfile,"xml"),qry,null,false);

		main = NetsManager.Query.qtabby.toString();

		int dirnumplus = Math.min(Integer.parseInt(dirnum)+1,i);

		String refstrip = Xlster.reffout(dirname, XCommands.keyvalue, dirnumplus);

		main = main.replace("<main>","");
		main = main.replace("<body>","");
		main = main.replace("<html>","");
		main = main.replace("</main>","</form>");
		main = main.replace("<reference>","<reference>\n"+refstrip+"\n");

		bufi.append(main);

		String buffout = bufi.toString().trim();

   	            ZConnection.out.write(buffout.getBytes());
   	            ZConnection.out.flush();
   	            ZConnection.out.close();

        } catch (Exception exception) {

            XCommands.pushListing(dirname);
            XCommands.reqfile = reqreq;

		String resume = 
"<html>\n<head><script>function go(){ location.reload(true);}</script></head>\n"
+"<body onload=\"go()\">\n\n";

		ZConnection.out.write(resume.getBytes());
   	            ZConnection.out.flush();
        }
    }

	///////////// FILL CHECKED //////////////////

    public static void fillChecked(StringBuilder _buf, String _localprocess, String dirctry) {
_buf.append("<form action=\"FileOps.jav\" method=\"GET\" name=\"overall\"");
_buf.append(" id=\""+dirctry+"\">");
        
       
	 _buf.append(vvv);

        if (_localprocess.startsWith("V")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"v\">view</span> ");

        _buf.append(ccc);

        if (_localprocess.startsWith("C")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"c\">copy</span> ");
        _buf.append(mmm);

        if (_localprocess.startsWith("M")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"m\">move</span> ");
        _buf.append(xxx);

        if (_localprocess.startsWith("X")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"d\">dele</span> ");
        _buf.append(eee);

        if (_localprocess.startsWith("E")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"e\">edit</span> ");
        _buf.append(qqq);

        if (_localprocess.startsWith("Q")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"q\">quik</span> ");
        _buf.append(aaa);

        if (_localprocess.startsWith("A")) {
            _buf.append("  checked=\"yes\"");
        }

        _buf.append("/> <span class=\"a\">note</span><p/>\n");
    }

///////////// GET CLOB AS STREAM ////////////

	 Reader getStream(String filename, String db) throws Exception{

   try{
	String sql = 
		"SELECT data " + "FROM "+db+" WHERE filename=?";

		PreparedStatement stmt = conn.prepareStatement(sql); 
			          stmt.setString(1, filename);
			          rs = stmt.executeQuery();            
			          rs.next();
    }catch( Exception e ) {
	            System.out.println(e.getMessage());
		new ZEdit.DOps();
    }
	return rs.getCharacterStream("data");
   }


	///////////// GET CLOB AS BYTE STREAM ////////////

	 InputStream getBits(String filename, String db) throws Exception{

   try{
   	String sql = 
		"SELECT data " + "FROM "+db+" WHERE filename=?";

		PreparedStatement stmt = conn.prepareStatement(sql); 
			          stmt.setString(1, filename);
			          rs = stmt.executeQuery();            
			          rs.next();
    }catch( Exception e ) {
	            System.out.println(e.getMessage());
		new ZEdit.DOps();
    }
	return new GZIPInputStream(rs.getBinaryStream("data"));
  }

}