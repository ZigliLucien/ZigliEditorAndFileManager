package ServPak.jv;

import NetsManager.*;

import java.io.*;

import java.math.BigInteger;

import java.util.Random;


public class Registering {
    static String buffertext;
     StringBuilder buffy;
     PrintWriter pt;
    static BufferedReader brd;
    static String outf;
    static int numtries;
    public String printout;
    byte[] filedata;

    public Registering(String textin) throws Exception {
        ///////////////////// REGISTER NEW USER ///////////////////////
        if (textin.equals("new")) {
            buffy = new StringBuilder(
                    "<html><head><title>Register </title></head><body>\n");
            buffy.append("<h2> Register </h2>\n<blockquote><blockquote>");
            buffy.append("<form action=Registering.jav method=GET>");
            buffy.append("Name <input name=\"user\"/>\n<p/>");
            buffy.append(
                "Password <input type=\"password\" name=\"password\"/>\n<p/>");
            buffy.append(
                "<input type=submit name=register value=\"GO\">\n<p/><input type=reset></form>");
            buffy.append("</blockquote></blockquote></body></html>");

            printout = buffy.toString();

            return;
        }

        /////////////////// PROCESS REGISTRATION /////////////////	
        if (textin.indexOf("user") >= 0) {
            int cut = textin.indexOf("&");

            String part = textin.substring(cut + 1);
            String user = textin.substring(textin.indexOf("=") + 1, cut);
            String password = part.substring(part.indexOf("=") + 1,
                    part.indexOf("&"));

            password = NetsManager.ZEFMServer.converter(password);

            if (!new File("users").exists() || (password.length() < 6) ||
                    (user.length() < 4)) {
                printout = "Please choose a username of 4 to 20 characters and a password of 6 to 10 characters. Please re-register.";

                return;
            }

            FileInputStream fins = new FileInputStream("users");
            byte[] data = new byte[fins.available()];

            fins.read(data);

            buffertext = "";

            if (data.length > 0) {
                BigInteger f = new BigInteger(data);

                filedata = f.shiftRight(3).toByteArray();
                buffertext = new String(filedata);
            }

            if (buffertext.indexOf("@@@@@@" + user + "==") >= 0) {
                printout = "This username is taken. Please choose another.";

                return;
            }

            buffertext += ("\n@@@@@@" + user + "==" + password);
            filedata = buffertext.getBytes();

            FileOutputStream fout = new FileOutputStream("users");

            BigInteger f = new BigInteger(filedata);

            f = f.shiftLeft(3).add(new BigInteger(3, new Random()));
            fout.write(f.toByteArray());
            fout.flush();
            fout.close();

            outf = "http://" + NetsManager.ZEFMServer.localhost + ":" +
                NetsManager.ZEFMServer.port + NetsManager.ZEFMServer.userdir +
                "/?home";

            buffy = new StringBuilder(
                    "<html><head><title>ZEFM Registered</title></head><body>\n");
            buffy.append(
                "<h2> Welcome to Zigli's File Manager</h2>\n<blockquote><blockquote>");
            buffy.append("You are successfully registered.<p/>");
            buffy.append("<a href=" + outf +
                "> -&gt; Continue here &lt;- </a>\n");
            buffy.append("</blockquote></blockquote></body></html>");

            printout = buffy.toString();
        }
    }
}
