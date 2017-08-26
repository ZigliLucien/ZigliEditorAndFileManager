package ServPak.jv;

import NetsManager.*;

import java.io.*;

import java.math.*;


public class Logging {
    static String filename;
    static String dirname;
     StringBuilder buffy;
     PrintWriter pt;
    static BufferedReader brd;
    static String outf;
    public static String user;
    public String printout;
    boolean registered;

    public Logging(String textin) throws Exception {
        System.out.println(textin);

        if (textin.endsWith("GOGO")) {
            return;
        }

        registered = false;

        if (textin.equals("lgout")) {
            String logout = "http://" + NetsManager.ZEFMServer.localhost + ":" +
                NetsManager.ZEFMServer.port + NetsManager.ZEFMServer.userdir;

            buffy = new StringBuilder(
                    "<html><head><title>ZEFM Logged Out</title></head><body>\n");
            buffy.append(
                "<h2> Bye-Bye from Zigli's File Manager</h2>\n<blockquote><blockquote>");
            buffy.append("<a href=" + logout + "> See you next time. </a>");
            buffy.append("</blockquote></blockquote></body></html>");

            NetsManager.ZConnection.logging = 0;
            NetsManager.ZConnection.currentclient = "y";
            user = "??";

            printout = buffy.toString();

            return;
        }

        outf = "http://" + NetsManager.ZEFMServer.localhost + ":" +
            NetsManager.ZEFMServer.port + NetsManager.ZEFMServer.userdir +
            "/?home";

        if (!new File("users").exists()) {
            new File("users").createNewFile();
        }

        FileInputStream fins = new FileInputStream("users");
        byte[] data = new byte[fins.available()];

        fins.read(data);

        if ((textin.indexOf("new=Register") >= 0) || (data.length < 2)) {
            NetsManager.ZConnection.logging = 0;

            Registering reggie = new Registering("new");

            printout = reggie.printout;

            return;
        }

        BigInteger f = new BigInteger(data);
        byte[] filedata = f.shiftRight(3).toByteArray();

        int cut = textin.indexOf("&");
        String info = textin.substring(cut + 1);

        user = textin.substring(textin.indexOf("=") + 1, cut);

        String password = info.substring(1 + info.indexOf("="),
                info.indexOf("&"));

        if (user.length() == 0) {
            user = "??";
        }

        if (password.length() == 0) {
            password = "??";
        }

        password = NetsManager.ZEFMServer.converter(password);
        brd = new BufferedReader(new InputStreamReader(
                    new ByteArrayInputStream(filedata)));

        for (String v; (v = brd.readLine()) != null;) {
            if (ZEFMServer.word.length() > 0) {
                v += ZEFMServer.word;
            }

            if (!v.equals("@@@@@@" + user + "==" + password)) {
                continue;
            }

            registered = true;

            // System.out.println("Checking "+v);
        }

        if (!registered) {
            NetsManager.ZConnection.logging = 0;

            Registering reggie = new Registering("new");

            printout = reggie.printout;

            return;
        }

        buffy = new StringBuilder(
                "<html><head><title>ZEFM Logged In</title></head><body>\n");
        buffy.append(
            "<h2> Welcome to Zigli's File Manager</h2>\n<blockquote><blockquote>");
        buffy.append("<a href=" + outf + "> To Home Page </a>");
        buffy.append("</blockquote></blockquote></body></html>");

        NetsManager.ZConnection.currentclient = textin.substring(0,
                textin.indexOf("="));
        printout = buffy.toString();
    }
}
