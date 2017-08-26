package ServPak.jv;

import ZEdit.DBStart;
import NetsManager.Query;

import java.sql.*;
import java.io.*;

public class Dictionary {

	public String printout;
	String[] arg;
  
public Dictionary(String in){

	in = in.replace('+',' ');
	in = converter(in);

	Connection con;

      try {

	 arg = in.split("=");

String db = "dictionaries";
String lang = arg[1].substring(0,arg[1].indexOf('&'));
String wd = doUnicode(arg[2]);
String which = "x";
if(arg.length==4) {
		which =arg[2];
		wd = arg[2].substring(0,arg[2].indexOf('&'));
	}

	FileOutputStream ffout = new FileOutputStream("CHECK.txt");
		ffout.write(wd.getBytes("UTF-8"));
		ffout.flush();
		ffout.close();

	Class.forName("com.mysql.jdbc.Driver");
	con = DriverManager.getConnection("jdbc:mysql://localhost:"+
	DBStart.dataport+"/ZEFMdb?characterEncoding=utf8","root", "");
 
String from = "word";

if(which.contains("data"))  from = "data"; 

String sql =    
"SELECT  *  FROM "+db+" WHERE lang='"+lang+"' and "+from+" regexp ?";

 		PreparedStatement stmt = con.prepareStatement(sql); 

	          if(from.equals("word"))  stmt.setString(1, wd);  
	          if(from.equals("data"))   stmt.setBytes(1, wd.getBytes("UTF-8"));  

	           ResultSet rs = stmt.executeQuery();
	
		StringBuilder sb = new StringBuilder("<?xml version=\"1.0\"?>\n");
		sb.append("<dictionaryResults>\n");

		StringBuilder results = new StringBuilder();

		while(rs.next()){		
			results.append("<entry>\n");
			results.append("<word>"+rs.getString("word")+"</word>\n");
			results.append("<translation>"+
			new String(rs.getBytes("data"),"UTF-8")+"</translation>\n");
			results.append("</entry>\n\n");
		}
	
		if(results.toString().length()>5){
			sb.append(results.toString());
		}else{
			sb.append("<entry>\n");
			sb.append("<result>Nothing found in "+lang+" for "+wd+"</result>\n");
			sb.append("</entry>\n\n");	
		}

		sb.append("</dictionaryResults>\n");		
	
	byte[] xxx = new NetsManager.Traxit(sb, "ServPak/xsl/dictgeneric.xsl", null).tabby;

		printout =  new String(xxx, "UTF-8");

 		}catch(Exception ex){
				ex.printStackTrace();
				printout = "Not found.";
				return;  	
		}
	     }

public static void main(String args[]){
	if(args.length==0){
	System.out.println("Port Lang Word/Data which(=x or data)");
	System.exit(0);
	}

	new Dictionary(args[0]);

	}
  //////////////// CONVERTER /////////////////////
    public static String converter(String string) {

        String x;
        String y;
        String z;

        for (/**/; string.indexOf("%") >= 0; string = x + y + z) {
            int i = string.indexOf("%");

            x = string.substring(0, i);
            y = string.substring(i + 1, i + 3);
            z = string.substring(i + 3);

            int q = ((16 * Byte.parseByte(y.substring(0, 1), 16)) +
                Byte.parseByte(y.substring(1, 2), 16));

            y = String.valueOf((char) q);
        }

        return string;

    }

	static String doUnicode(String y){

		if(! y.contains("&#")) return y;

		String z = y.replaceAll("\\&\\#(.*?)\\;","$1 ");
		String[] zz = z.split("\\s+");
		String yy = "";
		for(String v : zz) yy = yy.concat(String.valueOf((char)Integer.parseInt(v)));

		return yy;
	}
     }
