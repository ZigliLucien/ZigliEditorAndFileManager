package ZEdit;

import java.io.*;
import java.text.*;

import java.sql.*;

import java.net.*;
import NetsManager.ZEFMServer;

public class SMailClient {
    String host;
    String to;
    String from;
    String msg;
    public String filename;
    Socket server;

	Connection conn;

    public SMailClient(String _from, String _host, String _to, String _message,
        String _subject) {
        this.to = _to;
        this.filename = ZEditor.crunch(_subject) + "_" + MClient.getTime();
        this.from = _from;
        this.msg = "Subject: " + _subject + "\r\n\r\n" + _message+"\r\n";
        this.host = _host;

        if (!new File("SentMail").exists()) {
            new File("SentMail").mkdir();
        }

        filename = to + "_" + filename + ".log";

       StringBuilder writemail = new StringBuilder();

        try {


 	   conn = DOps.goMysql;


            this.server = new Socket(host, 25);

            InputStream in = server.getInputStream();
            OutputStream out = server.getOutputStream();
            BufferedReader bin = new BufferedReader(new InputStreamReader(in));
            PrintWriter pout = new PrintWriter(new OutputStreamWriter(out, "UTF-8"), true);

            server.setSoTimeout(8000);

            pout.println("helo " + this.host);

            writemail.append(bin.readLine()+"\n");

            pout.println("mail from: <" + this.from+">");

            writemail.append(bin.readLine()+"\n");

            pout.println("rcpt to: <" + this.to+">");

            writemail.append(bin.readLine()+"\n");

            pout.println("data");
            writemail.append(bin.readLine()+"\n");

            pout.print(this.msg);
            pout.print("\r\n" + "." + "\r\n");

            writemail.append(bin.readLine()+"\n");
            pout.println("quit");
            writemail.append(bin.readLine()+"\n");

            System.out.println("DONE!");

            pout.close();

            writemail.append(this.msg+"\n");

	String sql =     "INSERT INTO sentMail(filename,data,towhom,subject,date,time) " +
			"VALUES(?,?,?,?,?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data)";

          	            PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,filename);
	            stmt.setString(2,writemail.toString());
		stmt.setString(3,to);
		stmt.setString(4,_subject);
		stmt.setString(5,MClient.getTime());
		stmt.setLong(6,System.currentTimeMillis());

		System.out.println("SAVING "+filename+" to db SentMail");

	            stmt.executeUpdate();
	            stmt.close();


                        server.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
	new DOps();
	return;
        }
    }
}
