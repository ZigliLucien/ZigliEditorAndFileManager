package Plugins;

import com.ice.tar.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;


public class GoTar {

	public String printout;

      public GoTar(String rfile) throws Exception {

               	rfile = rfile;

        StringBuilder names = new StringBuilder(16385);
        names.append("<html><body bgcolor=\"#ffffff\">");

      String filext = rfile.substring(rfile.lastIndexOf(".") + 1);

        int cc = 0;

        if (filext.equals("gz") && !rfile.endsWith("tar.gz")) {
	FileInputStream fins = new FileInputStream(rfile);
            InputStream zipin = new GZIPInputStream(fins, fins.available());
            ByteArrayOutputStream bout = new ByteArrayOutputStream();

            for (int qq = 0; (qq = zipin.read()) != -1;) {
                bout.write(qq);
            }

            names.append("\n<pre>\n");
            names.append(bout.toString() + "\n</pre>");
        }

        if (filext.equals("tgz") || rfile.endsWith("tar.gz")) {
	FileInputStream fins = new FileInputStream(rfile);
            InputStream zipin = new GZIPInputStream(fins, fins.available());
            TarInputStream tin = new TarInputStream(zipin);

            for (TarEntry te = null; (te = tin.getNextEntry()) != null;) {
                cc++;

                if ((cc % 10) == 0) {
                    names.append("<p>");
                }

                String entry = te.getName();
                StringBuilder out = new StringBuilder(8193);
                out.append("<a href=TTT?GZ-" + rfile + "!" + entry + "> View </a> &nbsp;&nbsp;");
                out.append(
		"<a href=TTT?XGZ-" + rfile + "!" + entry +"> Extract </a>&nbsp;&nbsp;&nbsp;&nbsp;");

                if (entry.indexOf("/") > 0) {
                    StringTokenizer stin = new StringTokenizer(entry, "/");
                    int N = stin.countTokens();
                    out.append(stin.nextToken());

                    if (N > 2) {
                        for (int q = 0; q < (N - 2); q++)
                            out.append("/" + stin.nextToken());
                    }

                    if (N == 1) {
                        out.append("<p>" + out + "/");
                    }

                    if (N >= 2) {
                        out.append("<tt>/" + stin.nextToken());
                        out.append("</tt>");
                    }
                } else {
                    out.append("<tt>" + entry + "</tt>");
                }

                names.append("\n<br>" + out.toString());
            }
        }

        if (filext.equals("jar") || filext.equals("zip")) {
            ZipFile zf = new ZipFile(rfile);

            for (Enumeration enu = zf.entries(); enu.hasMoreElements();) {
                cc++;

                if ((cc % 10) == 0) {
                    names.append("<p>");
                }

                String entry = ((ZipEntry) enu.nextElement()).getName();
                StringBuilder out = new StringBuilder(8193);

                if (entry.endsWith(".class")) {
                    out.append("<a href=ReadClass.jav?" + rfile + "!" + entry +"> View </a>&nbsp;&nbsp;");
                } else {
                    out.append("<a href=TTT?ZI-" + rfile + "!" + entry + "> View </a>&nbsp;&nbsp;");
                }

                out.append(
		"<a href=TTT?XZI-" + rfile + "!" + entry + "> Extract </a>&nbsp;&nbsp;&nbsp;&nbsp;");

                if (entry.indexOf("/") > 0) {
                    StringTokenizer stin = new StringTokenizer(entry, "/");
                    int N = stin.countTokens();
                    out.append(stin.nextToken());

                    if (N > 2) {
                        for (int q = 0; q < (N - 2); q++)
                            out.append("/" + stin.nextToken());
                    }

                    if (N == 1) {
                        out.append("<p>" + out + "/");
                    }

                    if (N >= 2) {
                        out.append("<tt>/" + stin.nextToken());
                        out.append("</tt>");
                    }
                } else {
                    out.append("<tt>" + entry + "</tt>");
                }

                names.append("\n<br>" + out.toString());
            }
        }

        names.append("</body></html>");

	String where = System.getProperty("user.dir");

	PrintWriter pout = new PrintWriter(new FileWriter(where+"/TarList.html"),true);
	pout.print(names.toString());
	pout.close();

	printout = 
"<html><head><script> window.location=\""+where+"/TarList.html\"</script></head>\n"
+"<body><p/>&nbsp;<p/><p/>&nbsp;<p/><center><h2>--&gt;&gt; <a href=\""
+where+"/TarList.html\"> See List </a>&lt;&lt;--</h2></center></body></html>" ;

    }

 }