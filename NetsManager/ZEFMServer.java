package NetsManager;
import java.net.*;
import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.util.*;
import java.util.zip.*;

import ZEdit.*;
import java.sql.*;

public class ZEFMServer { 
    //Class

    ServerSocket ss;
    ZConnection Terry;

    static String DocRoot;
    static String ServerRoot;

	static String message = "ok";
	static String replymsg = "ok";

 public static int port;

	static ZEditor zigli;
	static boolean nozedit;
	static String donozedit;
	static boolean webed;

	public static final String username = System.getProperty("user.name");
	public static final String userhome = System.getProperty("user.home");

	public static String word="";

	public static String userdir;
	public static String localdir;
	public static String localhost;
	public static String localhostname;

 final String[] xsls = new String[]{"TPW","generic.xsl","db2clsv.xsl","javawords","properties.dtd"};
 final String[] pls = 
	new String[]{"jv2jxml.pl","java2jv.pl","f.prl","calculator.phtml","jv2jxmlinline.pl","java2jvinline.pl"};
 final String[] pngs = new String[]{"file.png","dir.png","fil.png","dr.png"};
 final String[] jss = 
new String[]{"listing.js","navigating.js","quickdel.js","webnavigate.js","webedit.js","jquery.js","mathformat.js"};
 final String[] csss = new String[]{"listing.css","math.css"};
 final String[] htmls = new String[]{"query.html"};

	Stack<String> staci;
	String[] dbases;

	public static String styledata;


	static String[] passwords = {};

	           StringBuilder buffy;
	  
      public static ResultSet rs;

	/////////////////  MAIN  //////////////////////////

	public static void main(String[] qubits) throws Exception{

	new ZEFMServer(qubits);

	}

    public ZEFMServer(int _port) throws Exception {
	this(_port,null);
	}

    public ZEFMServer(int _port, String _donozedit) throws Exception {	

	System.setProperty("javax.xml.parsers.SAXParserFactory",
		"com.sun.org.apache.xerces.internal.jaxp.SAXParserFactoryImpl");

	System.setProperty("javax.xml.transform.TransformerFactory",
		"net.sf.saxon.TransformerFactoryImpl");

             if(!ZEdit.DBStart.DBChecked) {
		new DBStart();
                            System.out.println("Initializing database through NetsManager");
		new KeepAlive();
	}


try{

   	   Class.forName("com.mysql.jdbc.Driver");
	   Connection conn = 
		DriverManager.getConnection("jdbc:mysql://localhost:"+DBStart.dataport+"/","root", "");

	DatabaseMetaData dmd = conn.getMetaData();
		ResultSet rs = dmd.getCatalogs();
	
		staci = new Stack<String>();	

		while(rs.next()) staci.push(rs.getString(1));
	
		 dbases  = new String[staci.size()];
		staci.toArray(dbases);
	
}catch(Exception exdb){System.out.println(exdb.getMessage());}

		XCommands.listcontrol0 = "locxsorter.xsl";
		XCommands.listcontrol1 = "lister.xsl";

	ZEFMServer.donozedit = _donozedit;
	ZEFMServer.port = _port;
	
		webed = true;

		try{
			localhost = InetAddress.getLocalHost().getHostName();
			localhostname = localhost;
	if(localhost.indexOf(".")>0) localhostname = localhost.substring(0,localhost.indexOf("."));	

		}catch ( Exception ioe0){ 
		localhost =  "localhost";
			localhostname = localhost;				
	System.out.println("Check host name\n"+ioe0.getMessage());
	}

		if(! new File("/topLevel.html").exists()) new MakeRootList();

try{
	if(!new File("ServPak").exists()) new File("ServPak").mkdir();
	if(!new File("ServPak/xsl").exists()) new File("ServPak/xsl").mkdir();
	if(!new File("HTML").exists()) new File("HTML").mkdir();
	if(!new File("ServPak/pl").exists()) new File("ServPak/pl").mkdir();
	if(!new File("ServPak/js").exists()) new File("ServPak/js").mkdir();
	if(!new File("ServPak/css").exists()) new File("ServPak/css").mkdir();
	if(!new File("Listings").exists()) new File("Listings").mkdir();
	if(!new File("Annotations").exists()) new File("Annotations").mkdir();

	putFile("properties/Mime.properties","Mime.properties");
	putFile("properties/MimeExtensions.properties","MimeExtensions.properties");

	 for (String v : xsls){
	 putFile("ServPak/xsl/"+v,"ServPak/xsl/"+v);
	}

	 for (String v : htmls){
	 putFile("HTML/"+v,"HTML/"+v);
	}

	 for (String v : pls){
	 putFile("ServPak/pl/"+v,"ServPak/pl/"+v);
		}

	 for (String v : jss){
	 putFile("ServPak/js/"+v,"ServPak/js/"+v);
		}

	 for (String v : csss){
	 putFile("ServPak/css/"+v,"ServPak/css/"+v);
		}

	 for (String v : pngs){
	 putFile("ServPak/"+v,"ServPak/"+v);
		}

	////////////// set directories ///////////////////////////////////


		userdir = System.getProperty("user.dir");

		userdir = userdir.replace('\\','/');

		if(userdir.indexOf(":")>0) 	userdir = userdir.substring(userdir.indexOf(":")+1);

		localdir = hexi(userdir);	
	
	/////////////////////////////////////////////////////////////
	////////////////////// SET HOME PAGE ///////////////////////
	/////////////////////////////////////////////////////////////

	              new File("HTML/zserve.html").delete();
		  putFile("HTML/zserve.html","HTML/zserve.html");

	String hostname = 
		localhostname.substring(0,1).toUpperCase()+localhostname.substring(1).toLowerCase();

		 BufferedReader bin = new BufferedReader(new FileReader("HTML/zserve.html"));
		StringBuilder buffy  = new StringBuilder();	

	for( String v;(v=bin.readLine()) != null;){
	
	if(v.indexOf("ZQQZ")>0)  {
		v = "<title>zefm@"+localhostname
+"</title>\n<style> a.w:link{color: blue} a.w:visited{color: blue} a.w:hover{color: #bb88ff}</style>\n";
	}

	if(v.indexOf("ZZZZ")>0)  v = "<h1>zefm@"+hostname+"</h1>";

	if(v.indexOf("usr/local")>0 && v.indexOf("INBOXES")>0) {
		v = "<a class=\"w\" href="+localdir+"/mail.html> Check Email  </a>";
	}
	if(v.indexOf("MZAZIZLZ")>=0) {
v = 
"<p/><a class=\"w\" href="+localdir
+"/INBOXES> Go to Email Directory </a>\n <p/><a class=\"w\" href=\"SendEmail.jav?e@@it\"> Send Email </a>";
v += "<p/><a class=\"w\" href=\"SentMail.jav?sentMail\"> Sent Mail </a>";
	}
	if(v.indexOf("Main Directory")>0) {
	v = "<a class=\"w\" href="+localdir+"> -> GO TO Main Directory -> </a>";
	} 

if(v.indexOf("XXXMYSQLXXX")>=0) {
v= "<form action=\"MySQL.jav\" method=\"get\">\n"+
"         <table>\n"+
"            <tr>"+
"               <td align=\"center\">  Name of database  </td>\n"+
"               <td align=\"center\">\n";
  
               v =  v.concat("<select name=\"basename\" value=\"ZEFMdb\">\n");

	    Arrays.sort(dbases);

                for (String vx : dbases) {
                    v =  v.concat("<option>" + vx + "</option>\n");
                }

                v =  v.concat("</select>\n");

	v = v+"               </td><td><br/></td>\n"+
"               <td><input type=\"submit\" value=\"GO\"></td>               "+
"            </tr>            "+
"         </table>\n         "+
"      </form>\n";

}

	if(v.indexOf("XXQQEERRYY")>=0) {
v = 
"<a class=\"w\" href="+localdir
+"/HTML/query.html> -&gt;Run an XQuery&lt;- </a>";
	}

	buffy.append(v+"\n");
		}

	if( new File(".passwords.data").exists() ) {
	passwords = ZConnection.getStringData(".passwords.data",true);	

	 buffy.append(
"<li style=\"list-style-type: square\">\n<a class=\"w\" href=\"Logging.jav?lgout\"/> Logout </a>\n</li><p/>");	
	}

	PrintWriter ptw = new PrintWriter(new FileWriter("HTML/zserve.html"),true);
	ptw.print(buffy);
	ptw.close();

	////////////////////////////home page////////////////////////


	//////////////////// DO MAIL PAGE /////////////////////////////

	Properties getmailinfo = new Properties();
	InputStream infile = new FileInputStream("GetMail.properties");
		getmailinfo.load(infile);
	Object[] obie = getmailinfo.keySet().toArray();
	Arrays.sort(obie);

	FileOutputStream mout = new FileOutputStream("mail.html");
	buffy = new StringBuilder("<html><head><title>Get Mail </title>\n");
	buffy.append( 
"<style> a.w:link{color: blue} a.w:visited{color: blue} a.w:hover{color: #bb88ff}</style>\n");
	buffy.append("</head><body>\n");
	buffy.append("<h2> Mail </h2>\n<blockquote><blockquote>");

	for(int q=0;q<obie.length;q++){

	if(obie[q].toString().startsWith("~~")) continue;

buffy.append("<a class=\"w\" href=Email.jav?"+obie[q].toString()+">"+ obie[q].toString()+"</a><p/>\n"); 
	}

	buffy.append("</blockquote></blockquote></body></html>");
	
	mout.write(buffy.toString().getBytes());
	mout.flush();
	mout.close();

		///////////////////////////mail page//////////////////////////////////
	
	}catch ( Exception ioe1){
			System.out.println("Setting Up Exception: "+ioe1.getMessage());
	}

	if( donozedit == null ) {			
			zigli = new ZEditor("Zigli's Editor");
		} else {

	if(donozedit.startsWith("+")) {

			String ttl = donozedit.substring(1);
			zigli = new ZEditor(ttl);
		} else {
			nozedit = true;

		if(donozedit.indexOf("/")>=0){
	DocRoot = donozedit; 
	ServerRoot = DocRoot.substring(0,DocRoot.lastIndexOf("/"));
		}
	      }	 
	}


	////////////////////// START SERVER ///////////////////

	ServerSocketChannel ssc = ServerSocketChannel.open();
	ss = ssc.socket();	
	ss.bind(new InetSocketAddress(port));

//	           ss = new ServerSocket(port);
	           System.out.println("Starting server on port "+port);    

	if(ZEFMServer.ServerRoot != null) System.out.println("Server Mode "+DocRoot);

 try{       

	 while ( true ){ 

	System.out.println("AT PORT "+port);
	
     		  Terry = new ZConnection( ss.accept() );
   		  Terry.start();
		       }

 }catch (IOException ioe){
		System.exit(0);
	} finally {System.out.println("Exiting");
		ZEdit.DOps.stopMySQL();
	}
    }

	public ZEFMServer(String[] qubits) throws Exception {

	String portry = qubits[0];
	int prt = 0;

	if(portry.indexOf("x")>0) {
		word = portry.substring(portry.indexOf("x")+1);
		prt = Integer.parseInt(portry.substring(0,portry.indexOf("x")));
	} else {
		prt = Integer.parseInt(portry);
	}
	switch(qubits.length) {

	case(4): 
		message  = "ok";
		replymsg = "ok";

           	case(2): new ZEFMServer(prt,qubits[1]); 
				break;
	case(3):
		message = "ok";
		replymsg = "ok";

	default:  new ZEFMServer(prt);

			}
	}

    public ZEFMServer(String args) throws Exception {

	String[] qubits = args.split("\\s+");
	
	new ZEFMServer(qubits);
  }

	/////////////////// COPY FROM RESOURCES /////////////////////

       public static void Copy(InputStream fromStream, String toFile) throws Exception{	

		FileOutputStream fout = new FileOutputStream(toFile);
	
		for(int q=0; (q=fromStream.read()) != -1;) fout.write(q);

		fout.flush();
		fout.close();
		}

	///////////////////  PUTFILE FROM RESOURCES /////////////////

	public static void putFile(String resource, String localfile) {

		try{	
	if(! new File(localfile).exists()) {
	Copy(ClassLoader.getSystemResourceAsStream(resource),localfile);
		}
		}catch(Exception exx){}
	}

	//////////////////////////// HEX CONVERTER //////////////////////////////

        public static String converter(String y) {

		    String y0,y1,y2;
		    int cut;

	while(y.indexOf("%")>=0) {

		cut = y.indexOf("%");
	  	 y0 = y.substring(0,cut);
	 	 y1 = y.substring(cut+1,cut+3);
		 y2 = y.substring(cut+3);

                      int checkit = 16*Byte.parseByte(y1.substring(0,1),16)+Byte.parseByte(y1.substring(1,2),16);

	         y1 = String.valueOf((char) checkit);

	         y  = y0+y1+y2;
	}

			return y;
	     }

	//////////////////// SPACES TO HEX /////////////////////////////////

	public static String hexi(String in) {

	in = in.replace('\\','/');

	char[] z = in.toCharArray();

	String y = "";

	for(int q=0;q<z.length;q++){

		if( Character.isSpaceChar(z[q]) ) {
			y +="%"+Integer.toHexString(z[q]);	
	   } else {
			y += String.valueOf(z[q]);
		}
	}
		return y;
  	   }

	////////////////// STRING REPLACE ////////////////////////////

	public static String streplace(String str, String old, String nu){

	if( str.indexOf(old)<0 ) return str;

	while(str.indexOf(old)>=0){
		int cut = str.indexOf(old);
		str = str.substring(0,cut)+nu+str.substring(cut+old.length());
	}
	return str;

	}

////////////////////////////////////////////////////
//////////////////// DB OPS /////////////////////////
////////////////////////////////////////////////////

///////////////// GET DB ZIP FILE /////////////////////

public static BufferedReader getZipFile(Connection cct, String filename, String db) throws Exception{

	  	  InputStreamReader insr = null;
try{
		  insr = new InputStreamReader(new GZIPInputStream(getBits(cct, filename, db)));
}catch(Exception ioe){		new DOps();}
		return new BufferedReader(insr);
	}

///////////////// GET DB FILE /////////////////////

public static byte[] getFile(Connection conn, String filename, String db) throws Exception{	

try{
	 String sql =    
		       "SELECT filename, data " + "FROM "+db+" WHERE filename=?";

          	            PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,filename);

	            rs = stmt.executeQuery();
		rs.next();	

      }catch( Exception e ) {            
	System.out.println(e.getMessage()); 
		new DOps();
    }
	return rs.getBytes("data");
  }

//////////// GET DB STREAM ///////////////////

public static Reader getStream(Connection conn, String filename, String db) throws Exception{

   try{
  	 String sql =    
		       "SELECT filename, data " + "FROM "+db+" WHERE filename=?";

          	            PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,filename);

	            rs = stmt.executeQuery();
		rs.next();	
    }catch( Exception e ) {
	            System.out.println(e.getMessage());
		new DOps();
    }
	return rs.getCharacterStream("data");
  }

//////////////////// SAVE DB DATA /////////////////////

	public static void goSave(Connection conn, String name, String jj, String db) {

   try{

	 String sql =   "INSERT INTO "+db+"(filename, data) " +
		"VALUES(?, ?)"+
		" ON DUPLICATE KEY UPDATE data=VALUES(data)";

		PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,name);
	            stmt.setString(2,jj);

		System.out.println("SAVING STRING "+name+" to db "+db);

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){ 		new DOps(); }
       }


//////////////////// SAVE BLOB DATA /////////////////////

	public static void goSaveBlob(Connection conn, String name, byte[] jj, String db) {

   try{

	 String sql =   "INSERT INTO "+db+"(filename, data) " +
		"VALUES(?, ?)"+
		" ON DUPLICATE KEY UPDATE data=VALUES(data)";

		PreparedStatement stmt = conn.prepareStatement(sql); 
		stmt.setString(1,name);
	            stmt.setBytes(2,jj);

		System.out.println("SAVING BYTES "+name+" to db "+db);

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){ 		new DOps();}
       }
//////////// GET BLOB STREAM ///////////////////

public static InputStream getBits(Connection conn, String filename, String db) throws Exception{

   try{
	String sql = 
		"SELECT data " + "FROM "+db+" WHERE filename=?";

		PreparedStatement stmt = conn.prepareStatement(sql); 
			          stmt.setString(1, filename);
			          rs = stmt.executeQuery();
                              	          rs.next();
    }catch( Exception e ) {
	            System.out.println(e.getMessage());
		new DOps();
    }

	return rs.getBinaryStream("data");
  }

	//////////////// ZIPPER ///////////////////

    public static void Zipper(Connection conn, String fileout, byte[] in, String db) {

try{

	ByteArrayOutputStream bout = new ByteArrayOutputStream();

 String sql =    (db.equals("xml")) ?
			 "INSERT INTO "+db+"(filename,data,time) " +
			"VALUES(?,?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data), time=VALUES(time)" :
			 "INSERT INTO "+db+"(filename,data) " +
			"VALUES(?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data)";
 
		PreparedStatement stmt = conn.prepareStatement(sql); 	

        GZIPOutputStream gzout = new GZIPOutputStream(bout);
        gzout.write(in);
        gzout.flush();
        gzout.close();
		stmt.setString(1, fileout);
		stmt.setBytes(2,bout.toByteArray());
		if(db.equals("xml")) stmt.setLong(3,new File(fileout).lastModified());

		System.out.println("ZIPPED "+fileout+" to db "+db);

	            stmt.executeUpdate();
	            stmt.close();

        }catch(Exception e){
		System.out.println(e.getMessage());
		new DOps();
	}
    }

/////////////// TEST IF KEY EXISTS /////////////////////

public static boolean testKey(Connection conn, String name, String db){
   
   try{

	String sql = 
		"SELECT * " + "FROM "+db+" WHERE filename=?";

		PreparedStatement stmt = conn.prepareStatement(sql); 
			          stmt.setString(1, name);
			          rs = stmt.executeQuery();
            
			return rs.next();

    }catch( Exception e ) {
		System.out.println(e.getMessage());
		new DOps();
	}	
		return false;
	}

/////////////// REMOVE KEY /////////////////////

public static boolean removeKey(Connection conn, String name, String db){
   
   try{

           String sql = 
		"DELETE FROM "+db+" WHERE filename=?";
	
		PreparedStatement stmt = conn.prepareStatement(sql); 
			          stmt.setString(1, name);

		int n = stmt.executeUpdate();

	System.out.println("Deleting "+name+" from "+db+" with result "+n);

	if(n==0) return false;

	}catch( Exception e ) {	
		new DOps(); 
		return false; 
	}

	return true;
	}
  }
