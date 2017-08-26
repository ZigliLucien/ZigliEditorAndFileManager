package ServPak.jv;

import NetsManager.ZEFMServer;
import ZEdit.DBStart;
import java.io.*;

import java.net.*;
import java.util.*;
import java.sql.*;

public class MySQL {

    public String printout;
               static Connection conn;
	   ResultSet rs;	   
	   static String post;
	   static String postpre;
		String pre;

	   static String firstColumn;

	   	 ResultSetMetaData rsmd;
	             int numberOfColumns;

    public MySQL(String string) throws Exception {

	StringBuffer buf = new StringBuffer(2050);

if(string.contains("basename=")) {

	if(string.contains("tablename=")) {
                     pre = string.substring(string.indexOf("&") + 1);
        	         post = string.substring(string.indexOf("=") + 1, string.indexOf("&"));
	         postpre = pre.substring(pre.indexOf("=") + 1);
	} else {
        	         post = string.substring(string.indexOf("=") + 1);
	         postpre = "";
	}

		if(postpre.equals("")) {
try{
	Class.forName("com.mysql.jdbc.Driver");

  	conn = DriverManager.getConnection(
	"jdbc:mysql://localhost:"+ZEdit.DBStart.dataport+"/"+post+"?characterEncoding=utf8","root", "");

	DatabaseMetaData dmd = conn.getMetaData();
	
	rs = dmd.getTables(post,null,null,null);

		Stack staci = new Stack<String>();	

		while(rs.next()) staci.push(rs.getString(3));
	
		 String[] tables  = new String[staci.size()];
		staci.toArray(tables);
		Arrays.sort(tables);
   
		buf.append("<html><header><title>"+post+"</title></header>\n<body>");
		buf.append("<h2>Tables in database \""+post+"\"</h2><p/>&nbsp;<br/>");
	 for (String v : tables) {
		buf.append(
"<a href=MySQL.jav?basename="+post+"&tablename="+ZEFMServer.hexi(v)+">"+v+"</a><p/>\n");
	}
		buf.append("</body>\n</html>");

   }catch( Exception e ) {           
	new ZEdit.DOps(); 
	System.out.println(e.getMessage()); 
    }
		} else {
try{
	Class.forName("com.mysql.jdbc.Driver");

  	conn = DriverManager.getConnection(
	"jdbc:mysql://localhost:"+ZEdit.DBStart.dataport+"/"+post+"?characterEncoding=utf8","root", "");

	rs = conn.createStatement().executeQuery("select * from "+postpre+" limit 1");
 	rsmd = rs.getMetaData();

	rs.next();
	firstColumn = rsmd.getColumnLabel(1);

     rs = conn.createStatement().executeQuery("SELECT "+firstColumn+" FROM "+postpre);

	if(!postpre.equals("sentMail")) {
		buf.append("<html><header><title>"+post+"</title></header>\n<body>");
		buf.append("<h2>"+postpre+"</h2><p/>&nbsp;<br/>");
	  while(rs.next()){
		String name = rs.getObject(firstColumn).toString();

		buf.append(
		"<a href=\"MySQL.jav?ENTRY="+ZEFMServer.hexi(name)+"\">"+name+"</a><p/>\n");
	}
		buf.append("</body>\n</html>");
	} else {
		buf.append("<?xml version='1.0'?>\n");
		buf.append("<sentmail>");
	  while(rs.next()){
		buf.append("\n<entry>\n");
		String name = rs.getObject(firstColumn).toString();

		String outname = name;

		String check = name.substring(0,name.indexOf('@'));
		String postcheck = name.substring(name.indexOf('@')+1);

		check = check.replaceAll("_","");
		name = check+'@'+postcheck;

		String towhom = name.substring(0,name.indexOf('_'));
		String split1 = name.substring(name.indexOf('_')+1);

		buf.append("<towhom>\n");
		buf.append(towhom+"\n");
		buf.append("</towhom>\n");

		String subject = split1.substring(0,split1.indexOf('_'));
		String split2 = split1.substring(split1.indexOf('_')+1);

		buf.append("<subject>\n");
		buf.append(subject+"\n");
		buf.append("</subject>\n");

		String date = split2.substring(0,split2.indexOf('.'));
		String split3 = split2.substring(split2.indexOf('.')+1);

		String yr = date.substring(date.lastIndexOf('_')+1);
		String moday = date.substring(0,date.lastIndexOf('_'));

		date = "20"+yr+"_"+moday;

		date = date.replace('_','/');

		buf.append("<date>\n");
		buf.append(date+"\n");
		buf.append("</date>\n");

		String time = split3.substring(0,split3.indexOf('.'));

		time = time.replace('_',':');

		buf.append("<time>\n");
		buf.append(time+"\n");
		buf.append("</time>\n");

		buf.append("<reference>\n");
		buf.append("<a href=\"MySQL.jav?ENTRY="+ZEFMServer.hexi(outname)+"\">"+outname+"</a><p/>\n");
		buf.append("</reference>");
		buf.append("\n</entry>\n");
	}
		buf.append("</sentmail>");
	}

    }catch( Exception e ) {           
	new ZEdit.DOps(); 
	System.out.println(e.getMessage()); 
    }
		}

	} else  if  (string.contains("ENTRY=")){

	string = string.substring(string.indexOf("=")+1);

	 buf.append("<html><header><title>"+post+"</title></header>\n<body>");

   try{

	 int approx = (int)(100/(numberOfColumns+2));

   	String sql = 
		"SELECT * FROM "+postpre+" where "+firstColumn+"=?";
		PreparedStatement stmt = conn.prepareStatement(sql); 

		stmt.setString(1,string);
	rs = stmt.executeQuery();

	rsmd = rs.getMetaData();
	rs.next();

            numberOfColumns = rsmd.getColumnCount();

          		buf.append("<h2>"+string+"</h2><p/>&nbsp;<br/>");
		buf.append("<table border=\"1\">\n");
	for(int q=1;q<numberOfColumns;q++) {
		buf.append("<tr><th width=\""+12+"%\">"+rsmd.getColumnLabel(q)+"</th>");
		String align = "center";
		String out = rs.getObject(q).toString();
		buf.append("<td align="+align+" width=\""+50+"%\"><pre>"+out+"</pre></td>");
		buf.append("</tr>\n");
	}
		buf.append("</table>\n<p/>\n");

	String fname = string;
	String aux = "";

	if(!postpre.equals("sentMail") && !postpre.equals("listings")) {
		if (string.contains(".") && ! string.contains("/")) {
				String str0 = string.substring(0,string.indexOf("."));
		            	String str1 = string.substring(string.indexOf(".")+1);		
		                        fname = str0.replace('_','/')+"/"+str1;
		} else {
				if(string.contains("_")) fname = string.replace('_','/');
		}

	} else {
				aux = "MySQL.jav?LOG=";
	}	

		buf.append(
		"<a href='"+aux+ZEFMServer.hexi(fname)+"'>See File</a><p/>\n");
		buf.append(
   "<a href='MySQL.jav?DELETE="+ZEFMServer.hexi(string)+"'>Delete Entry from Database</a><p/>\n");
		buf.append("</body>\n</html>");
 }catch( Exception e ) {           
		System.out.println(e.getMessage()); 
    }

	} else if (string.contains("LOG=")) {
try{

	buf.append("<html><header><title>From Logs/Listings</title></header>\n<body>\n<pre>");

		String fname = string.substring(string.indexOf("LOG=")+4);
		BufferedReader brdr = 
			new BufferedReader(ZEFMServer.getStream(conn, fname, postpre));

		for (String v; (v = brdr.readLine()) != null;) {
			buf.append(v+"\n");
		}
			buf.append("\n</pre>\n</body>\n</html>");

}catch( Exception e ) {           
		System.out.println(e.getMessage()); 
    }
	} else {

	string = string.substring(string.indexOf("=")+1);

            buf.append("<html><header><title>Deleting Entry</title></header>\n<body>");

try{

 	String sql = 
		"DELETE FROM "+postpre+" WHERE "+firstColumn+"=?";
		PreparedStatement stmt = conn.prepareStatement(sql); 

		stmt.setString(1,string);
	int n = stmt.executeUpdate();
	System.out.println("Deleting "+string+" from "+postpre+" with result "+n);

	if(n>0){
buf.append(
"<p/>&nbsp;<p/>&nbsp;<p/>Entry &nbsp; <tt>"+string+"</tt> &nbsp; has been deleted.<p/>\n");
	} else {
buf.append(
	"<p/>&nbsp;<p/>&nbsp;<p/>Entry <tt>"+string+"</tt> has <b>not</b> been deleted. "+ 
            "Check database permissions.<p/>\n");
	}
		buf.append("<a onclick=\"history.go(-2)\"> Back </a>\n");
		buf.append("</body>\n</html>");

 }catch( Exception e ) {           
		System.out.println(e.getMessage()); 
    }
	}

		printout = buf.toString();
   }
}