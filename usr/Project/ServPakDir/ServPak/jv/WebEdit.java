package ServPak.jv;

import NetsManager.Traxit;
import NetsManager.ZEFMServer;

import ZEdit.MailFiles;

import java.io.*;
import java.sql.*;

import java.lang.Character.UnicodeBlock;


public class WebEdit {
    static String filename;

     PrintWriter pout;
    static BufferedReader bin;
    public String printout;

    Connection conn;

    public WebEdit(String _textin) throws Exception {

      	   conn = ZEdit.DOps.goMysql;

        String textin = DBM.converter(_textin);

        printout = textin;

        if (textin.indexOf("e@@it") >= 0) {

            String filein = textin.substring(textin.indexOf("=") + 1);

            printout = editFile(filein);
        }

        if (textin.indexOf("s@@ve") >= 0) {
            String contents = DBM.converter(textin.substring(textin.indexOf("=") + 1));

            contents = contents.replace('+', ' ');

	ZEFMServer.goSave(conn, filename,contents,"annotations");
            printout = goString();
        }
    }

    String editFile(String _filename) throws Exception {

        filename = _filename;

          bin = new BufferedReader(ZEFMServer.getStream(conn, filename,"annotations"));

        StringBuilder buffy = new StringBuilder();

        buffy.append("<html>\n");
        buffy.append("<head><title>" + filename + "</title>\n");
        buffy.append("</head>\n");
        buffy.append("<body>\n");
        buffy.append("<h2> Editing " + filename + "</h2>");
        buffy.append(
            "<form action=\"WebEdit.jav\" method=\"post\"><table width=\"100%\">");
        buffy.append("<p><TEXTAREA name=\"s@@ve\" rows=\"25\" cols=\"80\">\n");

        for (String v; (v = bin.readLine()) != null;) {
            buffy.append(checkUTF(v) + "\n");
        }

        buffy.append("</TEXTAREA>\n");
        buffy.append(
            "<INPUT type=\"submit\" value=\"Save\"><INPUT type=\"reset\">\n");
        buffy.append("<p></form>");
        buffy.append("</body>\n");
        buffy.append("</html>\n");

        return buffy.toString();
    }

    public static  String goString() {
        StringBuilder buffy = new StringBuilder();

        buffy.append("<html>\n<body>\n");
        buffy.append("<pre>\n\nAnnotating " + NetsManager.XCommands.filepath +
            "\n</pre>\n");
        buffy.append("<form method=get>\n");
        buffy.append("Push GO to continue <p>\n");
        buffy.append("<input type=submit name=AAA?A  value=GO>\n");
        buffy.append("</form><p>\n");
        buffy.append("</body>\n</html>\n");

        return buffy.toString();
    }

    public static String checkUTF(String vv) {
        char[] z = vv.toCharArray();
        String word = "";

        for (int q = 0; q < z.length; q++) {
            int val = (int) z[q];

            if (val <= 127) {
                word += String.valueOf(z[q]);
            } else {
                word += ("&#" + val + ";");
            }
        }

        return word;
    }
}