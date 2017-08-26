package ZEdit;

import java.io.*;
import java.io.*;

import java.util.*;
import java.sql.*;

import javax.activation.*;

import javax.mail.*;
import javax.mail.internet.*;
import com.sun.mail.smtp.*;

import NetsManager.ZEFMServer;

public class JMailClient {
    //Class
    public static String outfile;
    SMTPMessage msg;

     Connection conn;

    public JMailClient(String from, String host, String to, String msgtext,
        String subject) {
        new JMailClient(from, host, to, msgtext, subject, "");
    }

    public JMailClient(String from, String host, String to, String msgtext,
        String subject, String filename) {
        //Constructor

        boolean debug = false;
        outfile = ZEditor.crunch(subject) + "_" + MClient.getTime();

        // create some properties and get the default Session
        Properties props = new Properties();
        props.put("mail.smtp.host", host);

        Session session = Session.getDefaultInstance(props, null);
        session.setDebug(debug);

        try {

	   conn = DOps.goMysql;

            // create a message
            msg = new SMTPMessage(session);
            msg.setFrom(new InternetAddress(from));

            InternetAddress[] address = { new InternetAddress(to) };
            msg.setRecipients(Message.RecipientType.TO, address);
            msg.setSubject(subject);
            msg.setSentDate(new java.util.Date());

	msg.setNotifyOptions(SMTPMessage.NOTIFY_SUCCESS);
	msg.setReturnOption(SMTPMessage.RETURN_HDRS);

            if (filename.length() > 0) {
                MimeBodyPart messagePart = new MimeBodyPart();
                messagePart.setText(msgtext, "UTF-8");
                msg.setContent(mimeIt(filename, messagePart));
            } else {
                msg.setText(msgtext, "UTF-8");
            }

            Transport.send(msg);

            if (!new File("SentMail").exists()) {
                new File("SentMail").mkdir();
            }

            outfile = to + "_" + outfile + ".log";

           String writemail = "Sent " + subject + " to " + to+"\n";
                     writemail += msgtext;

           String sql =     "INSERT INTO sentMail(filename,data,towhom,subject,date,time) " +
			"VALUES(?,?,?,?,?,?)"+
			" ON DUPLICATE KEY "+
			"UPDATE data=VALUES(data)";

          	            PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,outfile);
	            stmt.setString(2,writemail);
		stmt.setString(3,to);
		stmt.setString(4,subject);
		stmt.setString(5,MClient.getTime());
		stmt.setLong(6,System.currentTimeMillis());

		System.out.println("SAVING "+filename+" to db sentMail");

	            stmt.executeUpdate();
	            stmt.close();


        } catch (Exception mex) {
            System.out.println(mex.getMessage());
	new DOps();
        } finally {
		return;
	        }
    }

    static Multipart mimeIt(String _filename, BodyPart bpt)
        throws MessagingException {
        Multipart mpt = new MimeMultipart();
        mpt.addBodyPart(bpt);

        MimeBodyPart attachmentBodyPart = new MimeBodyPart();
        attachmentBodyPart.setDataHandler(new DataHandler(
                new FileDataSource(_filename)));
        attachmentBodyPart.setFileName(_filename);
        mpt.addBodyPart(attachmentBodyPart);

        return mpt;
    }

}
