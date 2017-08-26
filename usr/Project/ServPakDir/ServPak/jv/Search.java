package ServPak.jv;

import ZEdit.DBStart;
import NetsManager.*;
import java.io.*;
import java.util.*;
import java.sql.*;

public class Search {
	
    public String printout;

	Connection con;
	ResultSet rs;

    public Search(String string) throws Exception {

try{

Class.forName("com.mysql.jdbc.Driver");
	 con = DriverManager.getConnection(
	"jdbc:mysql://localhost:"+DBStart.dataport+"/ZEFMdb?characterEncoding=utf8","root", "");  

	}catch( Exception ee){}

        if (string.indexOf("&SEARCH") >= 0) {

            string = ZEFMServer.converter(string);

	String x = string.substring(0,string.indexOf("&"));

	x = x.substring(x.indexOf("=")+1);

	printout = "<html><body><h2> Search Results </h2>\n<p/>&nbsp;<br/>";

	while(x.indexOf("++")>=0) x = x.replace("++","+");
		x = x.replace("+"," +");

	StringBuilder sb = new StringBuilder("<p/> <b> Searching: </b> "+x+"<p/>&nbsp;<br/>");

	String sql = "select filename from texts where match(filename, data) "+ 
	"against( ? in boolean mode)";

		PreparedStatement stmt = con.prepareStatement(sql);
		stmt.setString(1, x);
		rs = stmt.executeQuery();

		String[] feeds = sortedResults(rs);

		sb.append("<h3>In Texts</h3>\n <ul>");
		sb.append(
	"<table><tr><th align=\"left\" width=\"10%\">"+
	"File</th><th align=\"left\" width=\"10%\">Directory</th>"+
	"<th align=\"left\" width=\"10%\"><br/></th></tr>\n");

		for(String v : feeds) sb.append(getRow(v));
		sb.append("</ul>\n<p/>&nbsp;<p/>");

	if(feeds.length==0) sb.append(
"<tr><td><tt>No matches found.</tt></td><td><br/></td><td><br/></td></tr><p/>");

		sb.append("</table>\n");

	printout += sb.toString()+"\n</body>\n</html>";


                   } else {

		printout = formEntry();	

	       }	
    }

 
     String formEntry() throws Exception {
        StringBuilder stringbuffer = new StringBuilder();

        stringbuffer.append("<html>\n");
        stringbuffer.append("<head><title>Search</title>\n");
        stringbuffer.append("<style>  h2{margin-top:2%;margin-left:3%}</style>\n");
        stringbuffer.append("</head>\n");
        stringbuffer.append("<body bgcolor=#eeeeee>\n");
        stringbuffer.append("<h2> Search ZEFM Database </h2><p/>&nbsp;<p/>");
        stringbuffer.append("<div style=\"margin-left: 10%;margin-top:8%\">"+
	"Enter search query:<p/>&nbsp;<br/>"+
	"<form action=\"Search.jav\" method=\"get\">\n");
        stringbuffer.append("<input name=words size=40>\n &nbsp;&nbsp; "+
            "<input type=submit value=GO name=SEARCH> "+
	" <input type=reset></form></div>");
                stringbuffer.append("</body>\n");
        stringbuffer.append("</html>\n");

        return stringbuffer.toString();
    }

/////// GET ROW ///////////
	public static String getRow(String ttl){

	String fdir = ttl.substring(0,ttl.lastIndexOf("/"));	

	return 
	"<tr><td align=\"left\" width=\"10%\"><a href=\""+ttl+"\">"+ttl+"</a></td> "+
	"<td align=\"left\"  width=\"10%\"><a href=\""+fdir+"\">"+fdir+"</a></td>"+
	"<td align=\"left\"  width=\"10%\"><br/></td></tr>\n";
	}

/////////// SORT RESULTS //////
	String[] sortedResults(ResultSet rrs){

	Stack staci = new Stack<String>();	

try{
		while(rrs.next())  staci.push(rrs.getString(1));
	}catch( Exception err){}

		 String[] out  = new String[staci.size()];
		staci.toArray(out);
		Arrays.sort(out);
		return out;
	}
}