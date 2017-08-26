package ZEdit;

import java.io.*;

import java.net.*;

import java.text.*;

import java.util.*;

public class MClient {
    static String host;
    static String fileout;
    static String user;
    static String pass;
    static String logfile;
    static int nummessages;
    static final Date dte = new Date();
    static final SimpleDateFormat sdf = new SimpleDateFormat("MM_dd_yy");
    static final SimpleDateFormat stf = new SimpleDateFormat("kk_mm");
    String directory;

    public MClient(String[] args) throws IOException, ClassNotFoundException {
        user = args[0];
        host = args[1];
        pass = args[2];

        String fileuser = user;

        if (user.indexOf("@") >= 0) {
            fileuser = user.substring(0, user.indexOf("@"));
        }

        directory = "INBOXES/" + fileuser;
        fileout = directory + "/" + fileuser + ".mail";
        logfile = directory + "/" + fileuser + ".log";

        if (host.equals("local")) {
            String getMailDirectory = "/var/spool/mail/";
            boolean varmail = false;

            if (new File("/var/mail/" + fileuser).exists()) {
                varmail = true;
            }

            if (varmail) {
                getMailDirectory = "/var/mail/";
            }

            FileInputStream fin = new FileInputStream(getMailDirectory + fileuser);
            FileOutputStream fout = new FileOutputStream(fileout);
            byte[] data = new byte[fin.available()];
            fin.read(data);
            fout.write(data);
            fout.flush();
            fout.close();

            File mailout = new File(fileout);
            File mailin = new File(getMailDirectory + fileuser);

            if (mailout.length() == mailin.length()) {
                mailin.delete();
            }

            return;
        }

        Socket server = new Socket(host, 110);
        server.setSoTimeout(8000);

        InputStream in = server.getInputStream();
        BufferedReader bin = new BufferedReader(new InputStreamReader(in, "UTF-8"));

        OutputStream out = server.getOutputStream();
        PrintWriter pout = new PrintWriter(out, true);
        FileOutputStream fout = new FileOutputStream(fileout);
        PrintWriter pdout = new PrintWriter(new OutputStreamWriter(fout, "UTF-8"), true);
        FileWriter folog = new FileWriter(logfile);
        PrintWriter foutlog = new PrintWriter(folog, true);
        pout.println("user " + user+"\r");
        foutlog.println(bin.readLine());
        pout.println("pass " + pass+"\r");
        foutlog.println(bin.readLine());
        pout.println("stat\r");

        foutlog.println(bin.readLine());

        String reply = bin.readLine();

        String[] parsed = reply.split("\\s+");

        foutlog.println(reply);
        nummessages = Integer.parseInt(parsed[1]);

        if (nummessages > 0) {

            for (int i = 1; i < (nummessages + 1); i++) {
                pout.println("list " + i+"\r");
                reply = bin.readLine();
                foutlog.println(reply);
 
                pout.println("retr " + i+"\r");

                StringBuilder sabi = new StringBuilder();

                for (String v;((v = bin.readLine()) != null) && (!v.equals("."));) {
                    sabi.append(v + "\n");
                }

                pdout.print(sabi.toString().trim());

                if (i < nummessages) {
                    pdout.println("\n\n===!_/ NEXT MESSAGE /|!===\n");
                }

                pout.println("dele " + i+"\r");
                foutlog.println(bin.readLine());
            }
        }

        pout.println("quit\r");
        foutlog.println(bin.readLine());
        foutlog.close();
        pdout.close();
        pout.close();
        server.close();
    }

     public static String getTime() {
        dte.setTime(System.currentTimeMillis());
        return sdf.format(dte) + "." + stf.format(dte);
    }
}
