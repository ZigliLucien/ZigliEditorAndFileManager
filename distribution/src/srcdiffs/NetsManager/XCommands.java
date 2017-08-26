package NetsManager;

import ServPak.jv.*;

import ZEdit.*;

import com.ice.tar.*;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.lang.reflect.*;

import java.net.*;

import java.text.*;

import java.util.*;
import java.util.zip.*;

import javax.swing.*;

import java.sql.*;


public class XCommands implements Comparator {
    static String direc;
    static String dirxml;
    public static String keyvalue;
    static String prekeyvalue;
    static String listfile;
    static String actfile;
    public static String reqfile;
    public static String filepath;
    static String reqx;
    static final String[] values = {
        "filename", "timekey", "filetype", "key1", "key2", "keys", "invkeys","standard"
    };
    static final String[] keys = {
        "Name", "Date", "FileType", "Key1", "Key2", "Keys12", "Keys21","RecentName"
    };
     static StringBuilder bufi;
     static StringBuilder buffy;
     static StringBuilder newxxs;
    static final java.util.Date d = new java.util.Date();
    static final SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yy");
    static final SimpleDateFormat stf = new SimpleDateFormat("kk:mm");
    static long timet = 0;
    static File current;
    static String[] hello = new String[6];
    static String notes;
    static final String baseURL = "file://" + ZEFMServer.localhost + ZEFMServer.userdir;
    static String workingdir;
    static String queryvalue;
    static String localprocesscall = "VVV?";

    static String listcontrol0 = "locxsorter.xsl";
    static String listcontrol1 = "lister.xsl";

    public String returns;
    String whichmethod;

    static Connection conn;

    public XCommands(String cmd) throws Exception {
        //Constructor

try{
	         conn = ZEdit.DOps.goMysql;
	}catch(Exception ee){
		new DOps();
	}

        if (ZEFMServer.ServerRoot != null) {
            Commands serverCheck = new Commands(cmd);
            serverCheck.goJJ();
            returns = serverCheck.result;

            return;
        }

        if (ServPak.jv.FileOps.processcall != null) {
            localprocesscall = ServPak.jv.FileOps.processcall;
        } else {
            localprocesscall = "VVV?";
        }

         Class cappi = Class.forName("NetsManager.XCommands");

        String directry = "";
        String xmlfile = "";

        if (filepath == null) {
            filepath = cmd.substring(cmd.indexOf("?") + 1);
        }

        if (reqfile == null) {
            reqfile = getListingFile();
        }

        try {
            whichmethod = ZConnection.whichproc;
            returns = cappi.getDeclaredMethod(whichmethod,
                    new Class[] { String.class }).invoke(this, new String[] { cmd }).toString();

            return;
        } catch (Exception e) {
        }

        /////////////////////////////////////////////////////////////
        /////////////////////// SORTING and LISTING ////////////////////////////
        ////////////////////////////////////////////////////////////
        if (cmd.indexOf("GO") < 0) {
           returns = 
	"<html><body>&nbsp;<p/>&nbsp;<p/> &nbsp;&nbsp; &nbsp; File or Resource Not Found: "+
	"<a style=\"color:blue;font-size:120%\" onclick='history.go(-2)'>"+
	"Return </a></body></html>";

	boolean both = true;

            if (cmd.indexOf("=") > 0) {
                if (keyvalue != null) {
                    prekeyvalue = keyvalue;
	        both = false;
                } else {
                    keyvalue = "timekey";
                    prekeyvalue = "filename";
                }

                workingdir = cmd.substring(cmd.indexOf("?") + 1, cmd.indexOf("="));
                queryvalue = cmd.substring(cmd.indexOf("=") + 1);

                directry = "";
                xmlfile = "";

                directry = ZEFMServer.converter(workingdir);

                if (directry.endsWith("/")) {
                    directry = directry.substring(0, directry.length() - 1);
                }

                for (int i = 0; i < values.length; i++) {
                    if (queryvalue.equals(keys[i])) {
                        XCommands.keyvalue = values[i];
                    }
                }

                if (keyvalue.equals("keys")) {
	        both = true;
                    keyvalue = "key1";
                    prekeyvalue = "key2";
                }

                if (keyvalue.equals("invkeys")) {
	        both = true;
                    keyvalue = "key2";
                    prekeyvalue = "key1";
                }

	    if (keyvalue.equals("standard")) {
	        keyvalue = "timekey";
                    prekeyvalue = "filename";
                }

                pushListing(directry, both);

            }
        }
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN C COPY/MOVE ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
 static String runM(String req) throws Exception {
        return runC(req, true);
    }

    static String runC(String req) throws Exception {
        return runC(req, false);
    }

     static String runC(String req, boolean move) throws Exception {
        filepath = (req.indexOf("M?") > -1)
            ? req.substring(req.indexOf("M?") + 2)
            : req.substring(req.indexOf("C?") + 2);

        if ((filepath.indexOf("C=GO") > -1) || (filepath.indexOf("M=GO") > -1)) {
            String target = filepath.substring(filepath.indexOf("=") + 1,
                    filepath.indexOf("&"));

            String targfile = ZEFMServer.converter(target);

            direc = ZEFMServer.converter(direc);

            if (!(targfile.indexOf("/") > -1)) {
                targfile = direc + "/" + targfile;
            }

	if(new File(targfile).isDirectory()) {
	String ffile = actfile.substring(actfile.lastIndexOf("/")+1);
	 	targfile = targfile+"/"+ffile;	
	}	

            targfile = targfile.replace('+', ' ');
	if(targfile.indexOf("//")>-1) targfile = targfile.replaceAll("//","/");

/*
            if (ZEFMServer.testKey(conn, XCommands.actfile,"annotations")) {
		byte[] data = ZEFMServer.getFile(conn, XCommands.actfile,"annotations");
		ZEFMServer.goSave(conn, targfile, new String(data), "annotations");
	}
*/

            ZEdit.Commands.copy(XCommands.actfile, targfile, move);

            XCommands.keyvalue = "timekey";
            XCommands.prekeyvalue = "filename";

	pushListing(direc, false);
	return null;

        } else {

            direc = filepath.substring(0, filepath.lastIndexOf("/"));
            actfile = filepath;
            reqfile = ZEFMServer.hexi(reqfile);

            buffy = new StringBuilder();
            buffy.append("<html>\n<body>\n");

            if (move) {
                buffy.append("<h1> Move File </h1>\n");
                buffy.append("<pre>\n\n<b>Move</b> " + filepath + "\n</pre>\n");
                buffy.append("<pre><b>to</b> [fill in filename]</pre>\n\n");
                buffy.append("<form method=get>\n");
                buffy.append("<input size=45 name=whereto>\n");
                buffy.append("<input type=submit name=M value=GO>\n");
                buffy.append(
                    "<p>Push GO to move (the directory will be updated).<p>\n");
                buffy.append(
                    "<p>Enter filename to move to. <br>Moves to the same directory by default.<br>\n");
	  buffy.append("Only the new filename is needed.<p/>\n");
	    buffy.append("To move to another directory, type in the path with /'s. \n");
	    buffy.append("<br>You may omit the filename if not changing it.<br/>\n");
            } else {
                buffy.append("<h1> Copy File </h1>\n");
                buffy.append("<pre>\n\n<b>Copy</b> " + filepath + "\n</pre>\n");
                buffy.append("<pre><b>to</b> [fill in filename]</pre>\n\n");
                buffy.append("<form method=get>\n");
                buffy.append("<input size=45 name=whereto>\n");
                buffy.append("<input type=submit name=C value=GO>\n");
                buffy.append(
                    "<p>Push GO to copy (the directory will be updated).<p>\n");
                buffy.append(
                    "<p>Enter filename to copy to. <br>Copies to the same directory by default. <br/>\n");
	  buffy.append("Only the new filename is needed.<p/>\n");
	    buffy.append("To copy to another directory, type in the path with /'s. \n");
	    buffy.append("<br>You may omit the filename if not changing it.<br/>\n");
            }

            buffy.append("</form><p>\n");
            buffy.append("<a href=" + reqfile +
                "> Back to Listing (cancel file operation)</a>\n");
            buffy.append("</body>\n</html>\n");

            return buffy.toString();
        }
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN X DELETE ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
     static String runX(String req) throws Exception {
        filepath = req.substring(req.indexOf("X?") + 2);

        if (filepath.indexOf("X=GO") > -1) {
            reqfile = ZEFMServer.converter(reqfile);
            direc = ZEFMServer.converter(direc);

            String listfileout = direc.replace('/', '_') + ".listing.html";

            String replyout = "<html>\n<body><a href=" +
                ZEFMServer.hexi(reqfile) +
                "> Please Refresh Here </a></body></html>";

            String prereq = direc.replace('/', '_') + "." + actfile.substring(actfile.lastIndexOf("/") + 1);

            if (ZEFMServer.removeKey(conn, prereq,"annotations")) {
                System.out.println("Notes deleted.");
            }

            if ((new File(XCommands.actfile)).delete()) {
replyout = 
"<html><body><a href=" + ZEFMServer.hexi(reqfile) + ">File has been deleted.</a></body></html>";
            }

            newxxs = new StringBuilder(8193);

	BufferedReader buff = null;

            boolean reqtype = (reqfile.indexOf("^") > 0);
             int scale = -1;
             if (reqtype) scale = Integer.parseInt(reqfile.substring(reqfile.lastIndexOf("^")+1));

            if ( scale > 0) {
                buff = ZEFMServer.getZipFile(conn, direc.replace('/', '_') + ".xml", "xml");
            } else {
                 buff = new BufferedReader(ZEFMServer.getStream(conn, listfileout, "listings"));
            }

            boolean line = false;

            actfile = ZEFMServer.hexi(actfile);

	String tester = actfile.substring(actfile.lastIndexOf("/")+1);

            for (String v; (v = buff.readLine()) != null;) {
                if (v.indexOf("form action=\"FileOps.jav\"") >= 0) {
                    ServPak.jv.GoFM.fillChecked(newxxs, localprocesscall, direc);

                     continue;
                }

                if (v.indexOf("value=\""+tester+"\"") > 0) {
                    line = true;
                }

                if (line && (v.indexOf("</tr>") >= 0)) {
                    line = false;
                }

                if (!line) {
                    newxxs.append(v + "\n");
                }
            }

            if (scale > 0) {

             ZEFMServer.Zipper(conn, direc.replace('/', '_') + ".xml",newxxs.toString().getBytes(),"xml");
	                return listOut(reqfile, replyout);
            } else {
                ZEFMServer.goSave(conn, listfileout, newxxs.toString(), "listings");
            	    return newxxs.toString();
            }

        } else {
            direc = filepath.substring(0, filepath.lastIndexOf("/"));
            actfile = filepath;
            reqfile = ZEFMServer.hexi(reqfile);
            buffy = new StringBuilder();

            buffy.append("<html>\n<head>\n");
	buffy.append(
"<script type=\"text/javascript\" src=\""+ZEFMServer.localdir+"/ServPak/js/quickdel.js\"></script>\n");
	buffy.append("</head>\n<body>\n");
            buffy.append("<h1> Delete File </h1>\n");
            buffy.append("<pre>\n\n<b>Delete</b> " + filepath + "\n</pre>\n");
            buffy.append("<form action=\"FileOps.jav\" method=\"get\">\n");
            buffy.append("Click GO or push spacebar to delete <p>\n");
            buffy.append("<input name=X value=GO type=hidden>\n");
            buffy.append("<input type=submit value=GO>\n");
            buffy.append("</form><p>\n");
            buffy.append("<a href=" + reqfile + "> Cancel Delete </a>\n");
            buffy.append("</body>\n</html>\n");

            return buffy.toString();
        }
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN E EDIT ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
   static String runE(String req) throws Exception {
        return runE(req, false);
    }

    static String runQ(String req) throws Exception {
        return runE(req, true);
    }

     static String runE(String req, boolean _qked) throws Exception {
  
      if (!ZConnection.local) {

            return listOut(reqfile,
                "<html><body><a href=" + ZEFMServer.hexi(reqfile) +
                "> Check your Zigli's Editor for Remote Edit.</a></body></html>");

        }

        final boolean qked = _qked;
        reqx = req;

        Thread t = new Thread() {
                public void run() {
                    try {
                        if (!qked) {
                            filepath = reqx.substring(reqx.indexOf("E?") + 2);
                        }

                        if (qked) {
                            filepath = reqx.substring(reqx.indexOf("Q?") + 2);
                        }

                        if (!ZEFMServer.nozedit && !qked) {

                            TPEditorX newBuffer = new TPEditorX(filepath, filepath);
                            ZEdit.ZEditor.initializing = false;

                            (ZEFMServer.zigli).daki.add(newBuffer);
                            (ZEFMServer.zigli).tiling();
                            (ZEFMServer.zigli).daki.setSelectedFrame(newBuffer);

                            return;
                        }
                        new QuickEditor(filepath);
                    } catch (Exception e) {
                    }
                }
            };

        t.start();
        t.join();

        direc = filepath.substring(0, filepath.lastIndexOf("/"));

            boolean reqtype = (reqfile.indexOf("^") > 0);
             int scale = -1;
             if (reqtype) scale = Integer.parseInt(reqfile.substring(reqfile.lastIndexOf("^")+1));

        if (scale <= 0) {
            checkListing(direc.replace('/', '_') +".listing.html", localprocesscall);
        }

        return listOut(reqfile,
           "<meta http-equiv=\"refresh\" content=\"0;"+ZEFMServer.hexi(reqfile)
	+">\n<a href="+ ZEFMServer.hexi(reqfile) + "> Done with Edit </a>");
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN N  NEWFILE///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
        static String  runN(String req) throws Exception {
        boolean trydirec = false;

        String predirec = req.substring(0, req.indexOf("NNN?"));

        for (int q = 0; q < ZConnection.processes.length; q++) {
            String test = ZConnection.processes[q];
            test = test.substring(0, test.length() - 1);

            if (predirec.indexOf(test) > 0) {
                trydirec = true;
            }
        }

        if (!new File(predirec).isDirectory()) {
            trydirec = true;
        }

        if (!trydirec) {
            direc = predirec;
        }

        if (trydirec) {
            return "<html><body><p>&nbsp;<p>&nbsp;&nbsp;&nbsp;<a href=" +
            ZEFMServer.hexi(reqfile) +
            ">Please update or click on the directory in the upper left first.</a></body></html>";
        }

        String prereq = "";

        prereq = req.substring(req.indexOf("=") + 1);

        direc = ZEFMServer.converter(direc);
        prereq = prereq.replace('+', ' ');

        new File(direc + "/" + prereq).createNewFile();

        XCommands.keyvalue = "timekey";

        pushListing(direc, false);        
        return null;
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN A Annotate ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
      static String runA(String req) throws Exception {
        //Annotate
        filepath = req.substring(req.indexOf("A?") + 2);

        if (filepath.indexOf("A=GO") > -1) {
            notes = "";

	String dataname = direc.replace('/', '_') + "." + reqx;

            BufferedReader binn = new BufferedReader(
			ZEFMServer.getStream(conn, dataname,"annotations"));

            for (String v; (v = binn.readLine()) != null;) {
                if (v.startsWith("Notes:")) {
                    notes = v.substring(v.indexOf(":") + 1);

                    break;
                }
            }

            newxxs = new StringBuilder(8193);

            boolean reqtype = (reqfile.indexOf("^") > 0);
             int scale = -1;
	BufferedReader buff = null;

             if (reqtype) scale = Integer.parseInt(reqfile.substring(reqfile.lastIndexOf("^")+1));

            if (scale > 0) {
                buff = ZEFMServer.getZipFile(conn, direc.replace('/', '_') + ".xml", "xml");
            } else {
             String  filein1 = direc.replace('/', '_') + ".listing.html";
                 buff = new BufferedReader(ZEFMServer.getStream(conn, filein1, "listings"));
           }


            boolean line = false;
	boolean mid = false;

            actfile = ZEFMServer.hexi(actfile);                     

	String tester = actfile.substring(actfile.lastIndexOf("/")+1);

            for (String v; (v = buff.readLine()) != null;) {		

                if (v.indexOf("form action=\"FileOps.jav\"") >= 0) {
                    ServPak.jv.GoFM.fillChecked(newxxs, localprocesscall, direc);

                    continue;
                }

                if (v.indexOf("value=\""+tester+"\"") > 0) {
                    line = true;
                }

                if (line && (v.indexOf("</tr>") >= 0)) {
                    line = false;
	        mid = false;
                }

                if (line && (v.indexOf("class=\"w\"") < 0) && (v.indexOf("value=") < 0)) {

                    String addit = "<td>" + notes + "</td>";
                    newxxs.append(addit + "\n");
	        mid = true;
                }
		if(!line || !mid) newxxs.append(v + "\n");
            }


            if (scale > 0) {

             ZEFMServer.Zipper(conn, direc.replace('/', '_') + ".xml",newxxs.toString().getBytes(),"xml");

                return listOut(reqfile,
           "<meta http-equiv=\"refresh\" content=\"0;"+ZEFMServer.hexi(reqfile)
	+">\n<a href="+ ZEFMServer.hexi(reqfile) + "> Done with Annotate </a>");

            } else {

            ZEFMServer.goSave(conn, direc.replace('/', '_') + ".listing.html", newxxs.toString(), "listings");

	pushListing(direc, false);
	return null;
            }
        } else {
            String filename = filepath.substring(filepath.lastIndexOf("/") + 1);

            actfile = filepath;
            reqx = filename;
            reqfile = ZEFMServer.hexi(reqfile);

            direc = filepath.substring(0, filepath.lastIndexOf("/"));

            final String prereq = direc.replace('/', '_') + "." + filename;

	if(!ZEFMServer.testKey(conn, prereq,"annotations")){

                StringBuilder babs = new StringBuilder();
                babs.append("Key1: " + "\n\n");
                babs.append("Key2: " + "\n\n");
                babs.append("Notes: ");

	   ZEFMServer.goSave(conn, prereq, babs.toString(),"annotations");
	}

            if (ZEFMServer.webed) {
                return new WebEdit("e@@it=" + prereq).printout;
            } else {
                Thread t = new Thread() {
                        public void run() {
                            try {
                                QuickEditor quid = new QuickEditor(prereq);
                                quid.writer.setCaretPosition(23);
                            } catch (Exception e) {
                            }
                        }
                    };

                t.start();
                t.join();

                return WebEdit.goString();
            }
        }
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN V VIEW ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
     static String runV(String req) throws Exception {
        filepath = req.substring(req.indexOf("V?") + 2);
        direc = filepath.substring(0, filepath.lastIndexOf("/"));

            boolean reqtype = (reqfile.indexOf("^") > 0);
             int scale = -1;
             if (reqtype) scale = Integer.parseInt(reqfile.substring(reqfile.lastIndexOf("^")+1));

        if (scale <= 0) {
            checkListing(direc.replace('/', '_') + ".listing.html", localprocesscall);
        }

        buffy = new StringBuilder(6145);

        buffy.append("<html>\n<body>\n");
        buffy.append("<pre>\n");

        if (new File(filepath).isDirectory()) {
            return ("To view files in this directory, first click on it to see a listing.");
        }

        BufferedReader binn = new BufferedReader(new InputStreamReader(
                    new FileInputStream(filepath), "UTF-8"));

        for (String v; (v = binn.readLine()) != null;) {
            if (v.toCharArray().length > 0) {
                v = ServPak.jv.DBM.fixgtlt(v);
            }

            buffy.append(v + "\n");
        }

        buffy.append("</pre>\n");
        buffy.append("</body>\n</html>\n");

        return buffy.toString();
    }

    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN T TARVIEW ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
    public  static String runT(String req) throws Exception {
        boolean extract = false;

        filepath = req.substring(req.indexOf("T?") + 2);

        int cut = filepath.indexOf("-");
        int cut2 = filepath.indexOf("!");

        String ext = filepath.substring(0, cut);
        String entryname = filepath.substring(cut2 + 1);
        filepath = filepath.substring(cut + 1, cut2);

        String locdir = filepath.substring(0, filepath.lastIndexOf("/"));
        String localdirec = locdir;
        int qcut = 0;

        if ((qcut = entryname.lastIndexOf("/")) > 0) {
            localdirec += ("/" + entryname.substring(0, qcut));
        }

        byte[] data = null;

        if (ext.startsWith("X")) {
            extract = true;
            ext = ext.substring(1);

            if (!new File("Xtrax").isDirectory()) {
                new File("Xtrax").mkdir();
            }

            if (!new File("Xtrax" + localdirec).exists()) {
                new File("Xtrax" + localdirec).mkdirs();
            }
        }

        if (ext.equals("GZ")) {
	FileInputStream fin = new FileInputStream(filepath);
            InputStream zipin = new GZIPInputStream(fin, fin.available());
            TarInputStream tin = new TarInputStream(zipin);

            for (TarEntry te = null; (te = tin.getNextEntry()) != null;) {
                if (!te.getName().equals(entryname)) {
                    continue;
                }

                data = new byte[tin.available()];
                tin.read(data);

                break;
            }
        } else {
            ZipFile zf = new ZipFile(filepath);
	DataInputStream zipin = new DataInputStream(zf.getInputStream(zf.getEntry(entryname)));
            data = new byte[zipin.available()];
            zipin.readFully(data);
        }

        if (extract) {

	String xtrloc = "Xtrax" + locdir + "/" + entryname;

            FileOutputStream prtw = new FileOutputStream(xtrloc);
            prtw.write(data);
            prtw.flush();
            prtw.close();

	            buffy = new StringBuilder("<html>\n<head>");
		buffy.append("<script> function go(){window.location=\""+xtrloc+"\";}</script>");
		buffy.append("</head>");
		buffy.append("<body onload=\"go()\">\n<pre>\n");
	            buffy.append("File extracted to "+xtrloc+" .");
        } else {
		buffy = new StringBuilder("<html>");
		buffy.append("<body>\n<pre>\n");
	            buffy.append(new String(data) + "\n");
        }

        buffy.append("</pre>\n");
        buffy.append("</body>\n</html>\n");

	        return buffy.toString();
    }



    /////////////////////////////////////////////////////////////////////////
    /////////////////////// RUN S QUIKDELETE ///////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////
     static String runS(String req) throws Exception {
        filepath = req.substring(req.indexOf("S?") + 2);
       
      		boolean ff = new File(filepath).delete();
		System.out.println("File "+filepath+" deleted: "+ff);
	               buffy = new StringBuilder("<html>\n<head>");
		buffy.append("<script> function go(){history.back();}</script>");
		buffy.append("</head>");
		buffy.append("<body onload=\"go()\">\n File Deleted\n");		
		buffy.append("</body>\n</html>\n");

        return buffy.toString();
    }

    /////////////////// GET LISTING FILE ////////////////////////////////
     String getListingFile() {
        try {
            XCommands.direc = filepath.substring(0, filepath.lastIndexOf("/"));

            String fpath = ZEFMServer.hexi(filepath);

            String lstfile = direc.replace('/', '_') + ".listing.html";

            BufferedReader binn = new BufferedReader(ZEFMServer.getStream(conn, lstfile, "listings"));

            String outf = lstfile;

            for (String v; (v = binn.readLine()) != null;) {
                if (v.indexOf(fpath + "\"") > 0) {
		ZConnection.out.write(ZEFMServer.getFile(conn, outf, "listings"));
		ZConnection.out.flush();
		ZConnection.out.close();
                }
            }

            BufferedReader buff = 	ZEFMServer.getZipFile(conn, direc.replace('/', '_') + ".xml", "xml");

            int count = 0;

            for (String v; (v = buff.readLine()) != null;) {
                if (v.indexOf("HEADER") > 0) {
	        int cut = v.indexOf(">");
                    count = Integer.parseInt(v.substring(cut-1,cut));
                }

                if (v.indexOf(fpath + "\"") > 0) {
                    return "GoFM.jav?" + direc + "^" + count;
                }
            }
        } catch (Exception e) {
            return "NOT FOUND";
        }
try{
 		return listOut(reqfile, direc);
	}catch(Exception eon){
		return direc;
	}
    }

    //////////////////// PUSHLIST //////////////////////


    public  static void pushListing(String _dir) throws Exception {
		pushListing(_dir, true);
	}

    public  static void pushListing(String _dir, boolean both) throws Exception {

        final String _directry = _dir;

        if (keyvalue == null) {
            keyvalue = "timekey";
        }

        if (prekeyvalue == null) {
            prekeyvalue = "filename";
        }

        listfile = _directry.replace('/', '_')+".listing.html";

        if (reqfile == null) {
            reqfile = listfile;
        }

        Thread t = new Thread() {
                public void run() {
                    try {
                        bufi = updateList(_directry);
                    } catch (Exception e) {
                    }
                }

                //run
            };

        //thread
        t.start();
        t.join();

        if (ZEFMServer.hexi(_directry) != null ) dirxml = ZEFMServer.hexi(_directry);

        String lpcall = localprocesscall.substring(0, localprocesscall.indexOf("?"));

        boolean keykey = 
	((XCommands.prekeyvalue.equals("key1") && XCommands.keyvalue.equals("key2")) ||
               (XCommands.prekeyvalue.equals("key2") && XCommands.keyvalue.equals("key1")));

	String diry = hexml(_directry);

	String queryString = 
            ZEFMServer.userdir+"!"+XCommands.keyvalue + "!" + _directry + "!" + dirxml + "!" + 
	lpcall;

if( !keyvalue.equals("timekey") || ! prekeyvalue.equals("filename") ) {

if(both){

        if (keykey) {

        new Query(bufi.toString(), "ServPak/xql/sorter.xql", "timekey", true, true);
        new Query(Query.qtabby.toString(), "ServPak/xql/sorter.xql", XCommands.prekeyvalue, true, true);
  
        } else {
            new Query(bufi.toString(), "ServPak/xql/sorter.xql", XCommands.prekeyvalue, true, true);
         }
     }

if(both){
	        new Traxit(Query.qtabby.toByteArray(), "ServPak/xsl/"+listcontrol0, queryString);
	} else {	 
       	        new Traxit(bufi, "ServPak/xsl/"+listcontrol0, queryString);
	}

     }else {

		new Traxit(bufi,"ServPak/xsl/"+listcontrol1, queryString);

	}
	        new Xlster(Traxit.tabby, _directry, XCommands.keyvalue, XCommands.prekeyvalue);
    }

    /////////////// LISTOUT ////////////////////
    public  static String listOut(String _outname, String _reply)
        throws Exception {

        final String xoutname = _outname;
        final String reply = _reply;

        Thread t = new Thread() {
                public void run() {
                    String outname = xoutname;

                    try {
                        if (outname.indexOf("?") > 0) {
                           	    outname = outname.substring(outname.indexOf("?") + 1);
                                        new GoFM(outname);
                        } else {

		    if(new File(outname).isDirectory()) {
	if(outname.endsWith("/")) outname = outname.substring(0,outname.lastIndexOf("/"));
			outname = outname.replace("/","_")+".listing.html";
		}

                            ZConnection.out.write(ZEFMServer.getFile(conn, outname, "listings"));
                            ZConnection.out.flush();
		    ZConnection.out.close();
                        }
                    } catch (Exception e) {
                    }
                }
            };

        t.start();
        t.join();

        return reply;
    }

    ///////////////////////////////////////////////////
    ///////////// UPDATELIST ////////////////////////
    /////////////////////////////////////////////////
     static StringBuilder updateList(String _direc) throws Exception {

	direc = _direc;

        int parity = 0;

        	            StringBuilder bufy = new StringBuilder(16385);

        String xmlname = hexml(_direc);

        bufy.append("<?xml version=\"1.0\"?>\n");
        bufy.append(
            "<!DOCTYPE notes [<!ENTITY % tpwsymbols SYSTEM \"file:ServPak/xsl/TPW\"> %tpwsymbols;]>\n");
        bufy.append("<" + xmlname + ">\n");

        String[] dirlist = new File(_direc).list();

	String kk = keyvalue;
	String pk = prekeyvalue;

	Arrays.sort(dirlist, new XCommands("null"));

	keyvalue = kk;
	prekeyvalue =pk;

        String dirkey = _direc.replace('/', '_');

        String filetype = "";

        for (String direntry : dirlist) {
      
            parity = 1 - parity;

            int dot = direntry.lastIndexOf(".");

            filetype = "none";

            if (dot > 0) {
                filetype = direntry.substring(dot + 1);
            }

            if (direntry.indexOf(".") == 0) {
                continue;
            }

            String keyname = dirkey + "." + direntry;
                         current = new File(_direc + "/" + direntry);

 if (current.isDirectory()) {
              continue;
            }

            timet = current.lastModified();
            d.setTime(timet);

            String filelement = "filename";

            bufy.append("<filedata parity=\""+parity+"\">\n");
            bufy.append("<sdt size=\"" + String.valueOf(current.length()) + "\" ");
            bufy.append("time=\"" + stf.format(d) + "\">" + sdf.format(d) + "</sdt>");
            bufy.append("<" + filelement + ">" + direntry + "</filename>");
            bufy.append("<timekey>" + String.valueOf(timet) + "</timekey>");
            bufy.append("<filetype>" + filetype + "</filetype>");

            if (ZEFMServer.testKey(conn, keyname,"annotations")) {
                notes = "";

           BufferedReader binn = 
		new BufferedReader(ZEFMServer.rs.getCharacterStream("data"));

                String keywords1 = "";
                String keywords2 = "";

                for (String v; (v = binn.readLine()) != null;) {
                    if (v.indexOf("Key1:") >= 0) {
                        keywords1 = v.substring(v.indexOf(":") + 1).trim();
                    }

                    if (v.indexOf("Key2:") >= 0) {
                        keywords2 = v.substring(v.indexOf(":") + 1).trim();
                    }

                    if (v.indexOf("Notes:") >= 0) {
                        notes = v.substring(v.indexOf(":") + 1);

                        break;
                    }
                }

                if (hexml(keywords1).length() == 0) {
                    keywords1 = "~~";
                }

                if (hexml(keywords2).length() == 0) {
                    keywords2 = "~~";
                }

                boolean kk1 = (keyvalue.equals("key1") ||
                    prekeyvalue.equals("key1"));
                boolean kk2 = (keyvalue.equals("key2") ||
                    prekeyvalue.equals("key2"));

                if (kk1 && !kk2) {
                    notes += (" &#160;<tt>[" + keywords1 + "]</tt>");
                }

                if (!kk1 && kk2) {
                    notes += (" &#160;<tt>[" + keywords2 + "]</tt>");
                }

                if (kk1 && kk2) {
                    notes += (" &#160;<tt>[" + keywords1 + "/" + keywords2 +
                    "]</tt>");
                }

                bufy.append("<key1> " + keywords1 + " </key1>\n");
                bufy.append("<key2> " + keywords2 + " </key2>\n");
                bufy.append("<annotation> " + notes + " </annotation>\n");
            } else {
                bufy.append("<key1>~~</key1>\n");
                bufy.append("<key2>~~</key2>\n");
                bufy.append("<annotation> - </annotation>\n");
            }

            bufy.append("</filedata>\n\n");
        }

        bufy.append(
            "<comment>EOF<filename>~~</filename><filetype>~~</filetype><key1>~~</key1><key2>~~</key2><timekey/></comment>\n");
        bufy.append("</" + xmlname + ">");

        return bufy;
    }

    /////////////////// HEXML NON-ALPHANUMERIC SQUASH ////////////////////////
    public static String hexml(String in) {
        char[] z = in.toCharArray();

        String y = "";

        for (int q = 0; q < z.length; q++) {
            if (!Character.isLetterOrDigit(z[q])) {
                continue;
            } else {
                y += String.valueOf(z[q]);
            }
        }

        return y;
    }

    ///////////////////// CheckListing //////////////////
    static void checkListing(String _lstfile, String _localprocesscall)
        throws Exception {

        StringBuilder bufy = new StringBuilder(8193);
        BufferedReader buff = new BufferedReader(ZEFMServer.getStream(conn, _lstfile,"listings"));

        for (String v; (v = buff.readLine()) != null;) {
            if (v.indexOf("form action=\"FileOps.jav\"") >= 0) {
                ServPak.jv.GoFM.fillChecked(bufy, _localprocesscall, direc);

                continue;
            }

            bufy.append(v + "\n");
        }
	ZEFMServer.goSave(conn, _lstfile,bufy.toString(), "listings");
    }

	/////////////////////// Compare Two //////////////////////////

	public int compare(Object i, Object j){

	File x = new File(direc+"/"+(String) j);
	File y = new File(direc+"/"+(String) i);

	int out = -1;

	if( x.lastModified() > y.lastModified()) out = 1;

	return out;

	}
}
