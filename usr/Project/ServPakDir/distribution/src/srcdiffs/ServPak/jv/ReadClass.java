package ServPak.jv;

import NetsManager.*;

import sun.tools.java.*;

import sun.tools.javac.*;

import sun.tools.javap.*;

import sun.tools.tree.*;

import sun.tools.util.*;

import java.io.*;

import java.util.*;


public class ReadClass {
    public String printout;
    Process dojavap;

    public ReadClass(String _filename) throws Exception {
        String effectiveFile = _filename;
        String classpath = "";

        String htmlstart = "<html><head><style>";
        StringBuilder bufi = new StringBuilder(htmlstart);

        if (_filename.indexOf("!") > 0) {
            int cut = _filename.indexOf("!");

            classpath = _filename.substring(0, cut);

            String classname = _filename.substring(cut + 1).replace('/', '.');
            int lastcut = classname.lastIndexOf(".");

            effectiveFile = classname.substring(0, lastcut);
        } else {
            int firstcut = effectiveFile.lastIndexOf("/");

            classpath = effectiveFile.substring(0, firstcut);
            effectiveFile = effectiveFile.substring(firstcut + 1);

            int cut = effectiveFile.lastIndexOf(".");

            effectiveFile = effectiveFile.substring(0, cut);
        }

        String v = "";

	Runtime ronny = Runtime.getRuntime();

        try {
            dojavap = ronny.exec("java sun.tools.javap.Main -classpath "+classpath+" "+effectiveFile);
        } catch (Exception jpex) {
            bufi.append(
                "Check your java installation for the Sun Tools package with the javap command.\n");
            bufi.append("\n</body>\n</html>");

            printout = bufi.toString();

            return;
        }

	BufferedReader err = new BufferedReader(new InputStreamReader(dojavap.getErrorStream()));

        for (String vv; (vv = err.readLine()) != null;) {
            System.out.println(vv);

            if (vv.startsWith("Error")) {
                bufi.append(
                    "Path not found. If this is part of a package, try a jar archive to see class information.\n");
                bufi.append("\n</body>\n</html>");

                printout = bufi.toString();

                return;
            }
        }

	BufferedReader buf = new BufferedReader(new InputStreamReader(dojavap.getInputStream()));

        bufi.append(
            "span.a{background-color: #ffddff;} td.b{background-color: #99ff99;}\n");
        bufi.append(
            "span.c{background-color: #ffffff;}span.d{background-color: #99ffff;}\n");
        bufi.append(
            "span.e{background-color: #ffffcc;}span.b{background-color: #99ff99;}\n");
        bufi.append("</style>\n</head>\n");

        String cd = "";

        v = buf.readLine();

        String title = "";

        if (v.indexOf("Compiled from") >= 0) {
            title = v.substring(v.indexOf("Compiled from") + 15, v.indexOf(".", v.indexOf("Compiled from")));
        }

        v = buf.readLine();
        cd = v.substring(0, v.indexOf("{"));
        bufi.append("<body bgcolor=#dddddf><h2>" + title + "</h2>\n");

        bufi.append("\n<h3><span class=c>Class</span></h3>\n");

        bufi.append("<span class=c>" + cd + "</span>\n<p>\n");
        bufi.append("\n<h3><span class=b>Fields</span></h3>\n");
        bufi.append("<table>\n");

        while ((v = buf.readLine()).indexOf("(") < 0) {
            bufi.append("<tr><td>");

            String[] vv = doString(v, false);

            bufi.append("<span class=e>" + vv[0] + "</span></td>");
            bufi.append("<td align=left class=b><tt>" + vv[1] +
                "</tt></td></tr>\n");
        }

        bufi.append("</table><p>");

        bufi.append("&nbsp;<p>\n<h3><span class=d>Methods</span></h3>\n");

        String[] vvv = doString(v, true);

        bufi.append("<span class=e>" + vvv[0] + "</span>");
        bufi.append(" <span class=d><tt>" + vvv[1] + "</tt></span>\n<p>");

        while ((v = buf.readLine()).indexOf('}') < 0) {
            String[] vv = doString(v, true);

            bufi.append("<span class=e>" + vv[0] + "</span>");
            bufi.append(" <span class=d><tt>" + vv[1] + "</tt></span>\n<p>");
        }

        bufi.append("\n</body>\n</html>");

        printout = bufi.toString();
    }

    String[] doString(String str, boolean ismethod) {
        String[] strout = new String[2];

        String methd = "";

        strout[0] = "";

        StringTokenizer stin = new StringTokenizer(str);
        int numtokens = stin.countTokens();

        String qq = "";

        if (ismethod) {
            while (qq.indexOf('(') < 0) {
                qq = stin.nextToken();
            }

            strout[0] = str.substring(0, str.indexOf(qq));
            methd = str.substring(strout[0].length());

            int cut = methd.indexOf('(');

            methd = "<b>" + methd.substring(0, cut) + "</b>" +
                methd.substring(cut);
        } else {
            for (int q = 0; q < (numtokens - 1); q++) {
                strout[0] += (stin.nextToken() + " ");
            }

            methd = stin.nextToken();
        }

        strout[1] = methd.substring(0, methd.length() - 1);

        return strout;
    }
}
