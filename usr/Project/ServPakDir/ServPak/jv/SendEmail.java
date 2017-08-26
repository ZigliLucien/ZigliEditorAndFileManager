package ServPak.jv;

import ZEdit.*;
import NetsManager.ZEFMServer;

import java.io.*;
import java.util.*;

import java.sql.*;


public class SendEmail {
    static String filename;
    static String dirname;
    static boolean attachment;
     FileOutputStream ft;
    static byte[] data;
     StringBuilder buffy;
    static BufferedReader brd;
    static Properties mailinfo = new Properties();
    static String mailto;
    static String subject;
    static String mailFrom;
    static String mailer;
    static String fileattachment = "";
    static String[] aliasfile;
    public String printout;
    String textin;
    String contents;
    int direct;
    SMailClient smc;

    Connection conn;

    public SendEmail(String _textin) throws Exception {

      	     conn = ZEdit.DOps.goMysql;      

        textin = DBM.converter(_textin);

        InputStream infile = new FileInputStream("Mail.properties");

        mailinfo.load(infile);

        mailFrom = mailinfo.getProperty("~~_from");
        mailer = mailinfo.getProperty("~~_by");

        Object[] obie = mailinfo.keySet().toArray();

        Arrays.sort(obie);
        aliasfile = new String[obie.length - 2];

        for (int q = 0; q < obie.length; q++) {
            if (obie[q].toString().startsWith("~~")) {
                continue;
            }

            aliasfile[q] = obie[q].toString();
        }

        if (textin.indexOf("e@@it") >= 0) {
	String replyto = "";
	if(textin.indexOf("=")>0)
	    replyto = textin.substring(textin.indexOf("=")+1);
	
            printout = setUp(replyto);

            return;
        }

        if (textin.indexOf("s@@nd") >= 0) {
            String towhom;

            StringTokenizer stin = new StringTokenizer(textin, "&=");

            stin.nextToken();
            towhom = stin.nextToken();
            stin.nextToken();

            String vv = stin.nextToken();

            if (!vv.equals("subject")) {
                towhom = vv;
                stin.nextToken();
            }

            subject = DBM.converter(stin.nextToken()).replace('+',' ');

            String linein = textin.substring(textin.indexOf("&s@@nd=") + 7);

            int cutoff = linein.indexOf("&attachment=");

              contents = linein.substring(0, cutoff);

	for(int cut=-1;(cut=contents.indexOf("+++"))>=0;){
	contents =new StringBuilder(contents).replace(cut,cut+3,"X@@@X").toString();	
	}

	for(int cut=-1;(cut=contents.indexOf("?"))>=0;){
	contents =new StringBuilder(contents).replace(cut,cut+1,"=Z=Z").toString();	
	}

	contents = contents.replace('+',' ');

	for(int cut=-1;(cut=contents.indexOf("X@@@X"))>=0;){
	contents =new StringBuilder(contents).replace(cut,cut+5,"+").toString();	
	}

	for(int cut=-1;(cut=contents.indexOf("..."))>=0;){
	contents =new StringBuilder(contents).replace(cut,cut+3,"?").toString();	
	}

            String rem = linein.substring(cutoff + 12);

            if (new File(rem).isFile()) {
                fileattachment = rem;
                System.out.println("Sending attachment " + fileattachment);
            }

            setMailTo(towhom);
            printout = VerifySend();

            return;
        }
    }

    void setMailTo(String premailto) {
        if (mailinfo.containsKey(premailto)) {
            premailto = mailinfo.getProperty(premailto);
        }

        int cut = premailto.indexOf(",");

        if (cut < 0) {
            mailto = premailto;
            direct = 0;
        } else {
            mailto = premailto.substring(0, cut);
            direct = 1;
        }

	if(premailto.indexOf(',',cut+1)>=0) {
		mailer = premailto.substring(premailto.lastIndexOf(",")+1);
		direct = 2;
	}

    }

    ///////////////////////////////////////////////////////////
    String setUp(String reply2) { // //////////////////////// setUp //////////////////////////

        //////////////////////////////////////////////////////////
        buffy = new StringBuilder();

        buffy.append("<html>\n");
        buffy.append("<head><title>  Send EMail </title>\n");
        buffy.append("</head>\n");
        buffy.append("<body>\n");
        buffy.append("<h2> Send EMail </h2>");
        buffy.append("<form action=\"SendEmail.jav\" method=\"get\">");
        buffy.append(
            " Correspondent (or fill in address below):  <select name=\"toWhom\">\n");
        buffy.append(
            "<option> Select from this list or enter address below </option>\n");

        for (int q = 0; q < aliasfile.length; q++) {
            buffy.append("<option value=" + aliasfile[q].toString() + ">" +
                aliasfile[q].toString() + "</option>\n");
        }

        buffy.append("</select><br/>\n");
        buffy.append(
  "Enter e-mail address here:  <INPUT type=\"text\" name=\"toWhom\" size=\"30\" value=\""+reply2+"\"><p/>\n");
        buffy.append("Subject: <INPUT type=\"text\" name=\"subject\"><p/>\n");
        buffy.append("<p><TEXTAREA name=\"s@@nd\" rows=\"25\" cols=\"80\">");
        buffy.append("</TEXTAREA>\n");
        buffy.append("<INPUT type=\"submit\" value=\"Send\"><p/>\n");
        buffy.append(
            "To send an attachment. Insert the filename (full pathname) here: <INPUT type=\"text\" size=\"40\" name=\"attachment\"> <p/>");
        buffy.append("<INPUT type=\"reset\">\n");
        buffy.append("<p></form>");
        buffy.append("</body>\n");
        buffy.append("</html>\n");

        return buffy.toString();
    }

    //////////////////////////////////////////////////////////////
    String VerifySend() { ///////////////////////////// VerifySend ///////////////////////

        //////////////////////////////////////////////////////////////
        try {

	boolean splitmailer = false;	

	if(direct==2) {
		direct = 1;
		splitmailer = true;
	}

            switch (direct) {
            case (1):

                int cut = mailto.indexOf("@");
               if(!splitmailer) mailer = mailto.substring(cut + 1);

	Thread t = new Thread(){
	
		public void run(){
	try{
             		 smc = new SMailClient(mailFrom, mailer, mailto, contents, subject);
	}catch(Exception e){
		      System.out.println("MailServer not found.");
	}
            }
   };
	 	t.start();
		t.join(25000);	
		return callPage(smc.filename);
                default:

                JMailClient jmc;
                String maillog = "";

                if (fileattachment.length() > 0) {
                    jmc = new JMailClient(mailFrom, mailer, mailto, contents, subject, fileattachment);
                    maillog = JMailClient.outfile;
                } else {      	
	      mailer = mailinfo.getProperty("~~_by");

	Thread th = new Thread(){
	
		public void run(){
	try{
             		 smc = new SMailClient(mailFrom, mailer, mailto, contents, subject);
	}catch(Exception e){
		      System.out.println("MailServer not found.");
	}
            }
   };
	 	th.start();
		th.join(25000);	
                            maillog = smc.filename;
                }

                fileattachment = "";

                return callPage(maillog);
            }
        } catch (Exception ex) {
		System.out.println(ex.getMessage());
        }

        return "Please check your address.";
    }


	/////////////////// callPage //////////////////

    String callPage(String _filename) throws Exception {

        String home = "http://" + NetsManager.ZEFMServer.localhost + ":" +
            NetsManager.ZEFMServer.port + NetsManager.ZEFMServer.userdir +
            "/?home";

        buffy = new StringBuilder("<html><body><pre>\n");
        brd = new BufferedReader(ZEFMServer.getStream(conn, _filename,"sentMail"));

        for (String v; (v = brd.readLine()) != null;) {

            if (v.toCharArray().length > 0) {
                v = ServPak.jv.DBM.fixgtlt(v);
            }

            buffy.append(v + "\n");
        }

        buffy.append("<p/>&nbsp;<p/><hr/><p/><a href=" + home +"> Return To Home Page </a>");
        buffy.append("</pre></body></html>");

        return buffy.toString();
    }
}











