package NetsManager;

import ZEdit.*;

import java.awt.*;
import java.awt.event.*;

import java.io.*;
import java.sql.*;

import java.util.*;
import java.util.regex.*;

import javax.swing.*;


public class XmlMail {
    static final String[] titles = {
        "Subject:", "Date:", "From:", "Reply-To:", "Reply-to:"
    };
    static final String[] days = {
        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
    };
    static final String[] longdays = {
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday"
    };
    	 BufferedReader bin;
    	 PrintWriter prt;
    static HashMap harry = new HashMap();
             StringBuilder pout;
    int cc = 0;
    boolean firstflag;
    boolean flag;
    boolean f1;
    boolean flag0;
    boolean flag1;
    boolean flag64_0;
    boolean flag64_1;
    boolean hasHTML = false;

    Properties mimexts = new Properties();
    String mimxt;

    HashMap duti = new HashMap();
    String replyto;
    public String viewmail;

   Connection conn;

    public XmlMail(String filename, String user) throws Exception {

         new ContentSplitter(filename, user);
try{
	         conn = ZEdit.DOps.goMysql;
	}catch(Exception ee){
		new DOps();
	}
	final String rqfile = XCommands.reqfile;

 	InputStream infile = new FileInputStream("MimeExtensions.properties"); 
	mimexts.load(infile);

        for (int q = 0; q < longdays.length; q++) {
            harry.put(days[q], longdays[q]);
        }

	StringBuilder sbuf = new StringBuilder(4097);

	replyto = "";

        String cal = new java.util.Date().toString();

        StringTokenizer stin = new StringTokenizer(cal);

        stin.nextToken();

        String month = stin.nextToken();
        String day = stin.nextToken();

        pout = new StringBuilder(4097);

        pout.append("<?xml version=\"1.0\"?>\n");
        pout.append(
            "<?xml-stylesheet type=\"text/xsl\"  href=\"ServPak/xsl/mailxml.xsl\"?>\n");
        pout.append(
            "<!DOCTYPE tpwm [<!ENTITY % tpwsymbols SYSTEM \"file:ServPak/xsl/TPW\"> %tpwsymbols;]>\n");
        pout.append("<mail>\n");

        try {
            FileInputStream fin = new FileInputStream(filename);
            bin = new BufferedReader(new InputStreamReader(fin, "UTF-8"));

            for (String v; (v = bin.readLine()) != null;) {
                if (v.startsWith(">From")) {
                    continue;
                }

                if (((v.indexOf("+OK") >= 0) && (cc < 1)) ||
                        ((v.indexOf("POPmail") >= 0) && (cc < 1)) ||
                        ((v.startsWith("From ") && (v.indexOf("@") >= 0)) &&
                        (cc < 1)) || v.equals("===!_/ NEXT MESSAGE /|!===")) {

                    duti.clear();
                    cc++;

                    if (firstflag) {
                        pout.append("</message>\n");
                    }

                    continue;
                }

                if (((v.indexOf("POPmail") >= 0) && (cc == 1)) ||
                        ((v.indexOf("Return-Path") >= 0) && (cc == 1)) ||
                        ((v.indexOf("Received:") >= 0) && (cc == 1))) {
                    cc = 0;
                    flag = true;
                    f1 = false;
                }

                if ((v.indexOf("Message-Id") >= 0) ||
                        (v.indexOf("Message-ID") >= 0)) {
                    continue;
                }

                String x = "";
                String y = "";

                for (int q = 0; q < titles.length; q++) {
                    if (v.indexOf(titles[q]) >= 0) {
                        int cut = v.indexOf(":");

                        x = v.substring(0, cut);
                        y = v.substring(cut + 2);

                        if (x.equals("From")) {
	if(y.indexOf("&lt;")>=0) {
		replyto = y.substring(y.indexOf("&lt;")+4,y.indexOf("&gt;"));	
	} else {
		replyto = y;	
	}
                        }

                        duti.put(x, ZEdit.MailFiles.ampcheck(y));
                    }
                }


                String w = ZEditor.crunch(v);

                if (!flag64_0 && w.length() == 0) {
                    flag = false;

                    continue;
                }

                if (flag) {
                    continue;
                }

                if (!f1) {
                    f1 = true;

                    longday();

                    pout.append("<headers>\n");

                    for (int q = 0; q < titles.length; q++) {
                        String key = titles[q].substring(0,
                                titles[q].indexOf(":"));

                        String ii = (key.equals("Reply-To") ||
                            key.equals("Reply-to")) ? "ReplyTo" : key;

                        if (duti.containsKey(key)) {
                            pout.append("<" + ii + ">" +
                                duti.get(key).toString() + " </" + ii + ">\n");
                        }
                    }

                    pout.append("</headers>\n");
                    pout.append("\n<message>\n");
                }

	////////////////////// Content Handlers //////////////////////////

	if(v.toLowerCase().startsWith("content-type")) {

		for(Enumeration enume=mimexts.keys();enume.hasMoreElements();){
		String testext = enume.nextElement().toString();
		if(v.toLowerCase().indexOf(testext)>=0) {
				mimxt = mimexts.getProperty(testext);
				System.out.println("Mime-type "+mimxt);
				break;
			}
		}
	}


	//////////////////////////////// Base64 Content /////////////////////////////
	if(!flag64_0 && v.indexOf("Content-")>=0 && v.toLowerCase().indexOf("ase64")>=0) {
		flag64_0 = true;
	}

	     if(flag64_0) break; 

	////////////////////////// HTML Content ////////////////////////////

     if(!flag0 && v.indexOf("Content-")>=0 && v.indexOf("text/html")>=0) flag0 = true;

     if(!flag0 && (v.toLowerCase().indexOf("doctype html public")>=0 
	       || v.toLowerCase().indexOf("<html")>=0)) flag0 = true;

     if(!flag0 && v.toLowerCase().indexOf("&lt;html")>=0) flag0 = true;

     if(new File(filename+".html").exists() && flag0) break;

	if(flag0) hasHTML = true;

     if(!new File(filename+".html").exists()){
	if(flag0 && !flag1 && (v.length()==0 || 
			v.toLowerCase().indexOf("quoted-printable")>=0 || 
			v.toLowerCase().indexOf("<html")>=0 || 
			v.toLowerCase().indexOf("&lt;html")>=0) ) {

				System.out.println("Parsing HTML attachment.");
				sbuf.append(fixAmps(v)+"\n");
				flag1 = true;
				continue;
	}
	
	if(flag0 && flag1){
	if(v.toLowerCase().indexOf("&lt;/html&gt;")>=0 || v.toLowerCase().indexOf("</html>")>=0) {
			flag0 = false;
			flag1 = false;

		     String htmlString =
		 "<p/><a href=\"http://"+
		     ZEFMServer.localhost + ":" +ZEFMServer.port +
		    "/SSS?" + filename+"\"> Delete Mail Message </a><p/>\n" +
		     "<a href=\"javascript: history.back()\"> Back </a>\n</html>";

		     String delString = getDeleteString(replyto,filename+".html").concat(htmlString);

			sbuf.append(delString+"\n");
			prt = new PrintWriter(new FileWriter(filename+".html"),true);
			prt.print(sbuf.toString());
			prt.close();

		String prefix = "INBOXES/"+user;
		String postfix = filename.substring(filename.lastIndexOf("/")+1);
              	String prefixdir = System.getProperty("user.dir").replace('\\', '/').replace('/','_');

	              if (prefixdir.indexOf(":") >= 0) {
	                          prefixdir = prefixdir.substring(prefixdir.indexOf(":") +1);
              					       }

		 String prereq0 = prefixdir + "_" +prefix.replace('/', '_') +"."+postfix;
		 String prereq = prereq0+".html";

		byte[] data = ZEFMServer.getFile(conn, prereq0,"annotations");
		ZEFMServer.goSave(conn, prereq, new String(data), "annotations");

		XCommands.reqfile = rqfile;
		XCommands.pushListing(System.getProperty("user.dir")+"/"+prefix);		
			continue;
		}
	  		sbuf.append(fixAmps(v)+"\n");
			continue;
	} 

	  if(flag0) continue;	

     }

                if (v.indexOf('=') >= 0) {
                    v = ZEdit.MailFiles.converter(v, "=");
                }

                if (v.indexOf('%') >= 0) {
                    v = ZEdit.MailFiles.converter(v, "%");
                }

                v = ZEdit.MailFiles.ampcheck(v);

                pout.append(v + "<br/>\n");

                firstflag = true;
            }
        } catch (Exception ee) {
		System.out.println(ee.getMessage());
        }

        pout.append("</message>\n</mail>\n");

        new Traxit(pout, "ServPak/xsl/mailxml.xsl", null);

	    StringBuilder buffy = new StringBuilder(4097);

	    String reply = new String(Traxit.tabby,"UTF-8");

        if (reply.equals("Check the xml file.")) {
            buffy.append("<html>\n<body>\n");
            buffy.append("<pre>\n");

            bin = new BufferedReader(new FileReader(filename));

            for (String v; (v = bin.readLine()) != null;) {
                if (v.indexOf('=') >= 0) {
                    v = ZEdit.MailFiles.converter(v, "=");
                }

                if (v.indexOf('%') >= 0) {
                    v = ZEdit.MailFiles.converter(v, "%");
                }

                v = ZEdit.MailFiles.ampcheck(v);

                buffy.append(v + "\n");
            }

            buffy.append("</pre>\n");
            buffy.append(getDeleteString(replyto,filename)+"\n");	
            buffy.append("</body>\n</html>\n");	

                   } else {

	   BufferedReader bread = new BufferedReader(new StringReader(reply));

 	    for (String v; (v = bread.readLine()) != null;) {
	    if (v.indexOf("</body>")>=0)  buffy.append(getDeleteString(replyto,filename)+"\n");
                  buffy.append(v + "\n");
		}   	
               }
		viewmail = buffy.toString();

	if(hasHTML){
		 StringBuilder buffi = new StringBuilder(4097);

	           buffi.append("<html>\n");
	           buffi.append("<meta http-equiv=\"refresh\" content=\"0;"+filename+".html>\n");
                         buffi.append("\n</html>\n");		            
	           viewmail = buffi.toString();
	}
    }

	/////////////// GET DELETESTRING ////////////

	String getDeleteString(String _replyto, String _filename) {

	     String replyString = "<p/>&#160;<br/><a href=\"http://" 
	+ ZEFMServer.localhost + ":" +ZEFMServer.port 
	+ "/SendEmail.jav?e@@it=" + _replyto+"\"> Reply To Message </a>\n";

	     String deleteString = "<p/><a href=\"http://"+
		     ZEFMServer.localhost + ":" +ZEFMServer.port +
		    "/XXX?" + _filename+"\"> Delete Message </a>\n";

	     String noteString = "<p/><a href=\"http://"+
		 ZEFMServer.localhost + ":" +ZEFMServer.port +
		 "/AAA?" + _filename+"\"> Annotate Message </a>";

	    return replyString+deleteString+noteString;
	}

	//////////// LONGDAY //////////

  void longday() {
        String predate = duti.get("Date").toString();

        for (int q = 0; q < days.length; q++) {
            if (predate.indexOf(days[q]) < 0) {
                continue;
            }

            int cut = predate.indexOf(days[q]);
            predate = predate.substring(0, cut) + longdays[q] +
                predate.substring(cut + 3);
        }

        duti.put("Date", predate);

        if (firstflag) {
            pout.append("\n\n");
        }
    }

/////////////// FIXAMPS ///////////////////

	static String fixAmps(String x){

		x = x.replace("&lt;","<");
		x = x.replace("&gt;",">");
		x = x.replace("&quot;","\"");
		x = x.replace("?>","?>\n");
		x = x.replace("&amp;","&");

		return x;
	}
}
