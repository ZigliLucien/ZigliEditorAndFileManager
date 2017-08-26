package ZEdit;
import NetsManager.ZEFMServer;

import java.io.*;
import java.text.*;
import java.util.*;
import java.sql.*;

public class MailFiles {
    static final java.util.Date dte = new java.util.Date();
    static final SimpleDateFormat stf = new SimpleDateFormat("kk_mm");
    static final String[] titles = { "Subject:", "Date:", "From:" };
    static final String[] days = {
        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
    };
    static final String[] longdays = {
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday"
    };
    PrintWriter prt;
    static HashMap <String,String> duti = new HashMap<String,String>();
    PrintWriter pout;
    int cc = 0;
    int lines = 0;
    String t;
    String prefix;
    String prereq;

    boolean mime64_0;
    boolean mime64_1;

   Connection conn;

    public MailFiles(String filename, String user) throws Exception {

try{
	   conn = DOps.goMysql;
	}catch(Exception ee){
		new DOps();
	}

        String cal = new java.util.Date().toString();

        String[] stin = cal.split("\\s+");

        String month = stin[1];
        String day = stin[2];
        String yr = stin[5];

        t = month + day + "_"+ yr + "_" + getTime() + "_" + user;
        prefix = "INBOXES/" + user;

        try {
            FileInputStream fin = new FileInputStream(filename);
            BufferedReader bin = new BufferedReader(new InputStreamReader(fin, "UTF-8"));

            duti.clear();

            for (String v; (v = bin.readLine()) != null;) {
                if (v.startsWith(">From")) {
                    continue;
                }

	if(!mime64_0 && !mime64_1 ) {

                if (((v.indexOf("+OK") >= 0) && (lines < 1)) ||
                        ((v.indexOf("POPmail") >= 0) && (lines < 1)) ||
                        ((v.startsWith("From ") && (v.indexOf("@") >= 0)) &&
                        (lines < 1)) || v.equals("===!_/ NEXT MESSAGE /|!===")) {
                    if (prereq != null) {
                        doNotes(prereq);
                    }

                    cc++;

                    String fileit = prefix + "/" + t + "_" + cc + ".mail";
                    String prefixdir = System.getProperty("user.dir")
                                             .replace('\\', '/').replace('/', '_');

                    if (prefixdir.indexOf(":") >= 0) {
                        prefixdir = prefixdir.substring(prefixdir.indexOf(":") + 1);
                    }

                    prereq = prefixdir + "_" +
                        prefix.replace('/', '_') + "." + t + "_" + cc +
                        ".mail";

                    FileOutputStream fileout = new FileOutputStream(fileit, true);
                    pout = new PrintWriter(new OutputStreamWriter(fileout,
                                "UTF-8"), true);

                    if (v.equals("===!_/ NEXT MESSAGE /|!===")) {
                        lines = 1;

                        continue;
                    }
                }

                if (((v.indexOf("POPmail") >= 0) && (lines == 1)) ||
                        ((v.indexOf("Return-Path") >= 0) && (lines == 1)) ||
                        ((v.indexOf("Received:") >= 0) && (lines == 1))) {
                    lines = 0;
                }

                if ((v.indexOf("Message-Id") >= 0) ||
                        (v.indexOf("Message-ID") >= 0)) {
                    continue;
                }

                String x = "";
                String y = "";

                for (String title : titles) {
                    if (v.indexOf(title) >= 0) {
                        int cut = v.indexOf(":");

                        x = v.substring(0, cut);
                        y = v.substring(cut + 2);

                        if (x.equals("From")) {
                            if (y.indexOf("<") >= 0) {
                                y = y.substring(0, y.indexOf("<"));
                            }
                        }

                        duti.put(x, y);
                    }
                }

     }

	if(!mime64_0 && v.indexOf("Content-")>=0 && v.toLowerCase().indexOf("ase64")>=0) mime64_0 = true;

	if( mime64_0 && !mime64_1 && v.trim().length()==0 ) mime64_1 = true;

	if(mime64_0 && mime64_1){
		if(v.startsWith("--")) {
			mime64_0 = false;
			mime64_1 = false;
		}
	}

	if(!mime64_0 && !mime64_1 ) {

                if (v.indexOf('=') >= 0) {
                    v = converter(v, "=");
                }

                if (v.indexOf('%') >= 0) {
                    v = converter(v, "%");
                }

                v = ampcheck(v);
     }
                pout.println(v);
            }
        } catch (Exception eee) {
        }

        doNotes(prereq);
    }

    public static String getTime() {
        dte.setTime(System.currentTimeMillis());

        return stf.format(dte);
    }

    public  void doNotes(String _prereq) throws Exception {
        if (duti.isEmpty()) {
            return;
        }

	Properties mailprops = new Properties();

	  InputStream infile = new FileInputStream("GetMail.properties");
	  mailprops.load(infile);

	  boolean keyit = mailprops.containsKey("~~keyfrom");
	  boolean keyit2 = mailprops.containsKey("~~keysubject");

            StringBuilder babs = new StringBuilder();

            String from = "";
            String subject = "";

            if (duti.containsKey("From")) {
                from = ampcheck(duti.get("From"));
            }

            if (duti.containsKey("Subject")) {
                subject = ampcheck(duti.get("Subject"));
            }

	if (keyit) {
	            babs.append("Key1: " + from +  "\n\n");
	} else {
	            babs.append("Key1: " + "\n\n");
	}
	if (keyit2) {
	            babs.append("Key2: " + subject +  "\n\n");
	} else {
	            babs.append("Key2: " + "\n\n");
	}
	  
	            babs.append("Notes: ");
	            babs.append(from + "<br/><em>" + subject + "</em>");

		DOps.goSaveText(conn, _prereq, babs.toString(),"annotations");

              duti.clear();
    }

    ////////////////// HEX CONVERTER ////////////////////////
    public static String converter(String y, String cutter) {
        StringTokenizer stin = new StringTokenizer(y, cutter);

        String v = "";
        String out = "";

        if (!y.startsWith(cutter)) {
            out = stin.nextToken();
        }

        while (stin.hasMoreTokens()) {
            v = stin.nextToken();

            if (v.length() < 2) {
                out += (cutter + v);

                continue;
            }

            char[] z = v.substring(0, 2).toCharArray();

            if ((Character.digit(z[0], 16) == -1) ||
                    (Character.digit(z[1], 16) == -1)) {
                out += (cutter + v);

                continue;
            }

            int checkit = (16 * Byte.parseByte(v.substring(0, 1), 16)) +
                Byte.parseByte(v.substring(1, 2), 16);

            out += String.valueOf((char) checkit);

            if (v.length() > 2) {
                out += v.substring(2);
            }
        }

        return out;
    }

    /////////////////////// controlChecker ////////////////////////////////////
    public static String controlChecker(String y) {
        char[] z = y.toCharArray();

        String yy = "";

        for (char v : z) {
            if (!Character.isISOControl(v)) {
                yy += String.valueOf(v);
            }
        }

        return yy;
    }

    /////////////////////// AMPCHECK ///////////////////////////
    public static String ampcheck(String chekit) {
        if (chekit == null) {
            return "null";
        }

        if (chekit.length() == 0) {
            return "";
        }

        chekit = ServPak.jv.DBM.fixgtlt(chekit);
        chekit = controlChecker(chekit);

        int ampcheck = chekit.indexOf('&');

        if (ampcheck < 0) {
            return chekit;
        }

        StringTokenizer stin = new StringTokenizer(chekit, "&");
        String v = "";
        String out = "";

        if (!chekit.startsWith("&")) {
            out = stin.nextToken();
        }

        while (stin.hasMoreTokens()) {
            v = stin.nextToken();

            if (v.indexOf(';') < 0) {
                out += ("&amp;" + v);
            } else {
                out += ("&" + v);
            }
        }

        return out;
    }
}
