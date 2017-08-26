package NetsManager;

import ServPak.jv.*;

import java.io.*;

import java.net.*;

import java.util.*;
import java.util.zip.*;

import java.sql.*;

public class ZConnection extends Thread {
  
    static String[] domains = getStringData("data/domains.data");
    static String[] addresses = getStringData("data/addresses.data");
    static String[] passwords;
    public static final String header = "HTTP/1.1 200 OK\nContent-Type: text/html\r\n";
    public static final String[] processes = {
       "SSS?", "VVV?", "CCC?", "XXX?", "EEE?", "QQQ?", "AAA?", "NNN?", "TTT?", "MMM?"
    };
    public static final String[] processrun = {
        "runS", "runV", "runC", "runX", "runE", "runQ", "runA", "runN", "runT", "runM"
    };

	static final String csss =  "/ServPak/css/listing.css";  
	static final String jsss =  "/ServPak/js/listing.js";  

    	  Socket client;
              PrintWriter pout;

    static char[] bst;
    static String request = "";
    public static OutputStream out;
    	 BufferedReader in;
             StringBuilder buffy;
    static boolean local;
    static boolean loggedin;
    public static int logging;
    public static String currentclient = "x";

    static boolean skip;
    static boolean bgupdate;

    public static String whichproc;
    public static final String propertiesFile = "ZServer.properties";
    public static Properties fileinfo = new Properties();
    static Properties mimeinfo = new Properties();
    static Commands runapp;
    static Thread tt;
    static ServerSocket uplds;
    public static String localaddr;
    static XCommands cary;
    static StringTokenizer st;
    static String prequest;
    boolean uploading;
    boolean withmime;
    boolean allowlogin;
    String incoming;
    String ext;

    static Vector dirsvisited = new Vector(16);

    Connection conn;

   public ZConnection(Socket _client) throws Exception {

	         conn = ZEdit.DOps.goMysql;

        client = _client;
        setPriority(NORM_PRIORITY - 1);

        ServPak.jv.Logging.user = (ServPak.jv.Logging.user != null)
            ? ServPak.jv.Logging.user : "User??";

        try {
            ZEFMServer.port = client.getLocalPort();

            localaddr = InetAddress.getLocalHost().getHostAddress();
            incoming = client.getInetAddress().getHostAddress();
            local = (client.getInetAddress().getHostName().equals("localhost") ||
	          client.getInetAddress().getHostName().startsWith("localhost.") ||
                         incoming.equals(localaddr));

            if (!new File(propertiesFile).exists()) {
                BufferedReader propfile = new BufferedReader(new InputStreamReader(
       ClassLoader.getSystemResourceAsStream("properties/" + propertiesFile)));

                buffy = new StringBuilder();

                for (String v; (v = propfile.readLine()) != null;) {
                    if (v.indexOf("HOSTNAME") >= 0) {
                        v = "HOSTNAME=" + ZEFMServer.localhostname;
                    }

                    buffy.append(v + "\n");
                }

                PrintWriter ptw = new PrintWriter(new FileWriter(propertiesFile),
                        true);
                ptw.print(buffy.toString().trim());
                ptw.close();
            }
        } catch (Exception ioe) {
        }

        ////////////////////////
        InputStream infile0 = new FileInputStream("Mime.properties");
        mimeinfo.load(infile0);

        InputStream infile = new FileInputStream(propertiesFile);
        fileinfo.load(infile);

        if (fileinfo.containsKey("LOCALHOST")) {
            ZEFMServer.localhost = fileinfo.getProperty("LOCALHOST");
        }

        if (fileinfo.containsKey("WEBANNOTATE")) {
            if (fileinfo.getProperty("WEBANNOTATE").equals("no")) {
                ZEFMServer.webed = false;
            }
        }

        passwords = ZEFMServer.passwords;
    }

    //////////////////////////// CHECK ADDRESS /////////////////
/*
    public void check(String addrr) throws Exception {
        if (local) {
            System.out.println("OK local");
            currentclient = incoming;
            logging = 0;
            return;
        }

        if (ZEFMServer.ServerRoot != null) {
            currentclient = incoming;
            logging = 0;
            return;
        }

        String checkinetdom = addrr.substring(1 + addrr.indexOf("/"),
                addrr.lastIndexOf("."));
        String checkinetaddr = addrr.substring(1 + addrr.indexOf("/"));

        for (int i = 0; i < domains.length; i++) {
            if (checkinetdom.equals(domains[i])) {
                System.out.println("OK domain");
                currentclient = incoming;
                logging = 0;
                return;
            }
        }

        for (int a = 0; a < addresses.length; a++) {
            if (checkinetaddr.equals(addresses[a])) {
                System.out.println("OK address");
                currentclient = incoming;
                logging = 0;
                return;
            }
        }

        if (passwords.length > 0) {
            for (int i = 0; i < passwords.length; i++) {
                if (checkinetdom.equals(passwords[i]) ||
                        checkinetaddr.equals(passwords[i])) {
                    allowlogin = true;
                    loggedin = (currentclient.equals(incoming));

                    if (loggedin) {
                        logging = 0;
                    }
                    return;
                }
            }
        }

        loggedin = false;
    }
*/

    ////////////////////////// RUN ////////////////////
    public void run() {
        InetAddress addrss = client.getInetAddress();
        String addr = addrss.toString();
        incoming = client.getInetAddress().getHostAddress();

        skip = false;
        whichproc = "";

        System.out.println("Connected to " + addr);

        try {
            in = new BufferedReader(new InputStreamReader(client.getInputStream()));
            out = client.getOutputStream();
            pout = new PrintWriter(new OutputStreamWriter(out, "UTF-8"), true);

            st = new StringTokenizer(in.readLine());

            prequest = st.nextToken();
            request = st.nextToken();

            System.out.print((new java.util.Date()).toString() + " ");
            System.out.println("user " + ServPak.jv.Logging.user + " at " +
                currentclient + " incoming " + incoming);

  //          if (!loggedin) {
 //               check(addr);
//            }

	loggedin = true;
	allowlogin = true;
	logging = 0;

/*
            loggedin = (currentclient.equals(incoming) || local ||
                (ZEFMServer.ServerRoot != null) ||
                (request.indexOf("Registering.jav?") >= 0) ||
                (request.indexOf("new=Register") >= 0));

            if (loggedin) {
                logging = 0;
            }

            if (allowlogin &&
                    (!loggedin || ServPak.jv.Logging.user.equals("User??") ||
                    ServPak.jv.Logging.user.equals("??")) && (logging < 1)) {
                logging++;
                doLogin(incoming, addrss.getHostName());
                allowlogin = false;
                client.close();
                return;
            }
*/
            System.out.println("Checked address: " + allowlogin + " Logged in: " + loggedin);

            uploading = request.equals("permission-to-upload");

            if (!(loggedin || (request.indexOf("Logging.jav?") >= 0) ||
                    (request.indexOf("Register") >= 0) || uploading)) {
 //               System.out.println("Address unaccepted.");
//                pout.println("Not Available.");
//                client.close();
                logging = 0;
            } else {
                System.out.println("TO " + currentclient + "/" + logging);

                if ((request.indexOf("Logging.jav?") > 0) &&
                       request.endsWith("login=GO") &&
                     (  request.indexOf("Register") < 0)) {
                    //logging++;
		logging = 0;
                }


                ////////////////// downloads ////////////////////////////
                if (!local) {
                    if ((request.indexOf("fileops=QQQ&") > 0) ||
                            (request.indexOf("fileops=EEE&") > 0)) {

		request = ZEFMServer.converter(request);

                        String filein = 
		request.substring(request.indexOf("fileops=") + 12,request.indexOf("@!!@x"));

                        System.out.println("DOWNLOAD: " + filein);

                        final FileInputStream din = new FileInputStream(filein);

		String localname = InetAddress.getLocalHost().getHostName();

	out.write(new String("HTTP/1.1 200 OK\nContent-Type: application/nomime\r\n\r\n")
			.getBytes());
	out.write(new String(localname+filein+"\r\n").getBytes("UTF-8"));

                        final byte[] conts = new byte[din.available()];

                        Thread t = new Thread() {
                                public void run() {
                                    try {
                                        din.read(conts);
                                        out.write(conts);
                                        out.flush();
                                    } catch (Exception e) {
                                    }
                                }
                            };

                        t.start();
                        t.join();
                        client.close();
                        return;
                    }
                }

                ///////////////////////////////// UPLOADS //////////////////////////
                if (prequest.equals(ZEFMServer.message)) {
                    System.out.println("UPLOAD");

                    final int port = 45212 + (int) Math.round(20000 * Math.random());

                    try {
                        Socket checker = new Socket(addrss, Integer.parseInt(request));
                        OutputStream kout = checker.getOutputStream();
                        PrintWriter kpout = 
			new PrintWriter(new OutputStreamWriter(kout, "UTF-8"), true);
                        BufferedReader kin = 
			new BufferedReader(new InputStreamReader(checker.getInputStream()));

                        kpout.println("GET permission-to-upload");

                        String kresponse = kin.readLine() + "\n" + kin.readLine() + "\r\n";

                        kpout.close();
                        checker.close();

                        if (!kresponse.equals(header)) {
                            client.close();
                            return;
                        }

                        System.out.println("Starting connection on port " + port);
                        uplds = new ServerSocket(port);
                        pout.println(port);

                        tt = new FileUpConnection(uplds.accept());
                        tt.start();
                    } catch (Exception exupl) {
                        return;
                    } finally {
                        return;
                    }
                }

                ////////////////// mimetypes ///////////////////////////////////////
                withmime = false;

                if (request.indexOf("?") < 0){
						
                    ext = request.substring(request.lastIndexOf(".") + 1).toLowerCase();

                    if (mimeinfo.containsKey(ext)) {
                        withmime = true;

                        String desc = mimeinfo.getProperty(ext);

                        System.out.println("Content-Type: " + desc);

                        if (!fileinfo.containsKey(ext)) {
                            try {

		request = ZEFMServer.converter(
			request.substring(request.indexOf(ZEFMServer.port) + 1));

                                System.out.println(request);

                                FileInputStream fis = new FileInputStream(request);

                                int len = fis.available();

                                byte[] data = new byte[len];
                                fis.read(data);

                                pout.println("HTTP/1.1 200 OK\nContent-Type: " + desc);
                                pout.println("Content-Length: " + len + "\r\n");
                                out.write(data);
                                out.flush();
                            } catch (Exception emi) {
                            } finally {
                                client.close();
                                return;
                            }
                        }

                        pout.println("HTTP/1.1 200 OK\nContent-Type: " + desc + "\r\n");
                    }
                }

                //////////////////////////// end mimetypes /////////////////////////////////////////
                if (loggedin || (!withmime && (logging == 0)) || uploading) {
                    pout.println(header);
                }

                if (!local && !loggedin && (logging < 5)) {
                    logging++;
                }

                if (uploading) {
                    uploading = false;
                    client.close();
                    return;
                }


	////////////////// POST ///////////////

                if (prequest.equals("POST")) {
                    System.out.println("POST: " + request);

                    int len = 0;
                    String v = "";

                    while ((v = in.readLine()).toCharArray().length != 0) {
                        if (v.indexOf("Content-Length") >= 0) {
                            len = Integer.parseInt(v.substring(v.indexOf(":") + 2));
                        }
                    }

                    bst = new char[len];
                    in.read(bst); 
                    Commands.directory = request.substring(0, request.lastIndexOf("/"));

	        Commands.result = null;

                    new Commands(request + "?" + new String(bst));

                    if (Commands.result != null) {
                        out.write(Commands.result.getBytes("UTF-8"));
		out.flush();
                    }

                    client.close();

                    return;
                }


	//////////////////// GET /////////////////

                if (prequest.equals("GET")) {
                    if ((ZEFMServer.ServerRoot != null) &&
                            (!request.startsWith(ZEFMServer.DocRoot) ||
                            (request.indexOf("^") >= 0) ||
                            (request.indexOf("?home") >= 0) || request.endsWith("?updat") ||
                            request.endsWith("?update"))) {
                        pout.println("400 Bad Request");
                        System.out.println("FAKY REQUEST: File/Directory " + request);
                        client.close();
                        return;
                    }

            if (request.equals("/topLevel.html")) {
		goFile(request);
                        return;
                    }

                    if (request.endsWith("/")) {
                        request = request.substring(0, request.lastIndexOf("/"));
                    }

                    request = ZEFMServer.converter(request);

                    if ((request.indexOf("?") > 0) &&
                            request.substring(request.indexOf("?") + 1).equals("home")) {

		goFile("HTML/zserve.html");
                        return;
                    }

                    if (!(request.indexOf("editmode") > 0)) {
                        System.out.println("REQUEST: " + request);
                    }

                    boolean updating = false;
	        String reqq = request;

		if(request.indexOf("GoFM.jav?")>=0 && request.indexOf("^")>0){

		String prerq = request.substring(request.indexOf("?")+1);
	                       reqq = prerq.substring(0, prerq.indexOf("^") );

		} 

                    if (request.indexOf("?") < 0) {

   		String dircheck = reqq;
        		         bgupdate = false;

		if(!new File(dircheck).isDirectory()) 
			dircheck = reqq.substring(0, reqq.lastIndexOf("/"));

		if(! dirsvisited.contains(dircheck) 
                      && !request.endsWith(csss) &&! request.endsWith(jsss)) {
			if(dirsvisited.size()>15) dirsvisited.removeElementAt(0);
			dirsvisited.add(dircheck);
  		            XCommands.direc = dircheck;
			XCommands.reqfile = request;
			if(!reqq.equals(dircheck)) bgupdate = true;
			update(dircheck,bgupdate);
			System.out.println("UPDATING "+dircheck);
			if(bgupdate) {

		String resume = 
"<html>\n<head><script>function go(){ location.reload(true);}</script></head>\n"
+"<body onload=\"go()\">\n\n";

		out.write(resume.getBytes());
		out.write(
		new String("--- Refresh to view formatted page. ---<p>\n\n<pre>").getBytes());
//				goFile(request, false);
				out.write(new String("</pre>\n</body></html>").getBytes());
				out.flush();
				client.close();

			}
				return;
		}
          }

                    if (request.endsWith("?update")) {

		            request = request.substring(0, request.indexOf("?"));
	                        updating = true;

		if(!(new File(request).isDirectory()) ){
			request = request.substring(0, request.lastIndexOf("/"));
		}
                    }

                    while (new File(request).isDirectory()) {

		XCommands.direc = request;

                        if (request.endsWith("/")) {
                            request = request.substring(0, request.length()-1);
                        }

                        String listfile = request.replace('/', '_') + ".listing.html";

                        XCommands.reqfile = listfile;

		if (ZEFMServer.ServerRoot != null) {
                            request = request + "/index.html";
		    break;
                        } 

                        if ( !ZEFMServer.testKey(conn, listfile, "listings") ) {
                            updating = true;
                        }

                        if (updating) {

			update(request);
			return;		

                        } else {
		     out.write(ZEFMServer.rs.getBytes("data"));	
		     out.flush();
		     client.close();
		     return;
		}
                    }


                     if (request.indexOf("?NNN") > 0) {
                        int ncut = request.indexOf("?NNN");
                        request = request.substring(0, ncut) + "NNN?" + request.substring(ncut + 4);
                    }


                  if (request.indexOf("SSS&") > 0) {
	
		request = request.replace('&','?');
	
                    }

                    for (int q = 0; q < processes.length; q++) {
                        if (request.indexOf(processes[q]) > 0) {
                            skip = true;
                            whichproc = processrun[q];
                        }
                    }

/*
	// Check SSS //

		if(whichproc.equals("runS")) {
		       String req = request.substring(0,request.indexOf("@!!@"));
		        request = req.substring(req.indexOf("SSS?")+4);
 		        skip = false;
		        ServPak.jv.FileOps.processcall = "SSS?";

	if(XCommands.direc != null) {
		        XCommands.checkListing(
			XCommands.direc.replace('/', '_') + ".listing.html", "SSS?");
			                      } 
					          }
*/

          if (skip) {
                            cary = new XCommands(request);

                            if (cary.returns != null) {
	try{						
                                out.write(cary.returns.getBytes("UTF-8"));
                                out.flush();
      } catch (Exception e) { 
      } finally {
                            client.close();
                            return;
                                       }
			                            }                 
                        }

                    if ( request.indexOf("^") > 0 || request.endsWith(".listing.html")) {
                        XCommands.reqfile = request;
	}

	        // get file           

                    boolean runcommand = false;
                    String ext1 = "";
                    String extension = "";

                    if (request.indexOf("?") > 0) {
                        String subreq = request.substring(0, request.indexOf("?"));
                        ext1 = subreq.substring(subreq.lastIndexOf(".") +1);
                    } else {
                        extension = request.substring(request.lastIndexOf(".") +1);
                    }

                    if (fileinfo.containsKey(extension) ||
                            fileinfo.containsKey(ext1)) {
                        runcommand = true;
                    }

                    if (loggedin && !runcommand && new File(request).isFile()) {
                        try {
     
			goFile(request);

                        } catch (Exception ioe) {
                            pout.println("404 Not Found");
                        } finally {
                            client.close();
                            return;
                        }
                    } else {
                        if (runcommand) {
                            Commands.directory = request.substring(0, request.lastIndexOf("/"));

                            try {

			Commands.result = null;
                             new Commands(request);

                                if (Commands.result != null) {
                                    out.write(Commands.result.getBytes("UTF-8"));
                                    out.flush();
                                } 
                            } catch (Exception ecm) {
                            } finally {
                                client.close();
                                return;
                            }
                        } else {
                            cary = new XCommands(ZConnection.request);
                            out.write(cary.returns.getBytes("UTF-8"));
                            out.flush();
                            client.close();
                            return;
                        }
                    }
                }

                client.close();
            }
        } catch (Exception e3) {
            System.out.println(e3.getMessage());

            try {
                client.close();
            } catch (Exception ecc) {
            }
	               return;
        }
    }

    ////////////////////////////////////////////////////////
    /////////////// GET DATA //////////////////////////////
    ////////////////////////////////////////////////////////
    static String[] getStringData(String filein) {
        return getStringData(filein, false);
    }

    static String[] getStringData(String filein, boolean isLocal) {
        String[] stary = null;
        BufferedReader bin = null;

        try {
            if (!isLocal) {
                bin = new BufferedReader(new InputStreamReader(
                            ClassLoader.getSystemResourceAsStream(filein)));
            } else {
                bin = new BufferedReader(new FileReader(filein));
            }

            Stack <String>data = new Stack<String>();

            for (String v; (v = bin.readLine()) != null;) {
                data.push(v);
            }

            stary = new String[data.size()];
	data.toArray(stary);

        } catch (Exception ioe) {
            System.out.println("File is Missing");
        }

        return stary;
    }

    ///////////////////////////////////////////////////////////
    /////////////////////////// DOLOGIN //////////////////////
    //////////////////////////////////////////////////////////
        void doLogin(String _addr, String _address) {
        buffy = new StringBuilder(
                "<html><head><title>LogIn </title></head><body>\n");
        buffy.append("<h2> Login " + _address +
            "</h2>\n<blockquote><blockquote>");
        buffy.append("<form action=Logging.jav?" + _addr + " method=GET>");
        buffy.append("Name <input name=\"" + _addr + "\"/>\n<p/>");
        buffy.append(
            "Password <input type=\"password\" name=\"password\"/>\n<p/>");
        buffy.append(
            "<input type=submit name=login value=\"GO\">\n<p/><input type=reset></form>");
        buffy.append("</blockquote><p/>&nbsp;<p/><hr/>");
        buffy.append(
            "<p/> To login you must be registered. Go here to register: <p/>\n");
        buffy.append("<form action=Logging.jav? method=GET>");
        buffy.append("<input type=submit name=new value=\"Register\"></form>");
        buffy.append("</blockquote></body></html>");

        try {
            out.write(buffy.toString().getBytes());
            out.flush();
        } catch (Exception ex) {
        }
    }

///////////////////// UPDATING ////////////////
	
	void update(String _request){
		update(_request, false);
	}

	void update(String _request, boolean noClose) {
try{
	               XCommands.pushListing(_request);
                           if (!noClose) {
			out.flush();
			out.close();
			client.close();
		}
}catch(Exception exup){}
	}

///////////////////// GOFILE ////////////////////////

    void goFile(String _request) {
	goFile(_request, true);
	}

    void goFile(String _request, boolean doClose){
try{
                       InputStream ins = new FileInputStream(_request);

                        byte[] data = new byte[ins.available()];
                        ins.read(data);
                        out.write(data);
	if(doClose){
                        out.flush();
                        out.close();
		client.close();
	}		
		}catch(Exception eex){}
	}
}