package Plugins;

import NetsManager.*;
import java.io.*;

public class GoProperties{

    public String printout;
	BufferedReader buf;
	StringBuilder sb;

    public GoProperties(String rfile) throws Exception{

		FileInputStream fins = new FileInputStream(rfile);
		byte[] data = new byte[fins.available()];
		fins.read(data);

		 buf = new BufferedReader(new StringReader(new String(data)));
		 sb = new StringBuilder("<?xml version=\"1.0\"?>\n");
		sb.append("<properties>\n");

		for(String v;(v=buf.readLine()) != null;) {

		if(v.startsWith("#")) continue;
		if(v.indexOf("=")<0) continue;

			String key = v.substring(0,v.indexOf("="));
			String value = v.substring(v.indexOf("=")+1);
			sb.append("<entry key=\""+key+"\">"+value+"</entry>\n");
		}

			sb.append("</properties>");

			byte[] out =   sb.toString().getBytes("UTF-8");

	            new Traxit(out, "ServPak/xsl/readProps.xsl", null);
		 buf = new BufferedReader(new StringReader(new String(Traxit.tabby)));
		 sb = new StringBuilder();
		for(String v;(v=buf.readLine()) != null;) {
		if(v.trim().startsWith("<h1>"))	{
			v = "<h1>"+rfile.substring(rfile.lastIndexOf("/")+1)+"</h1>\n";
		}
			sb.append(v+"\n");
		}		
			
			printout = sb.toString();
	    }
     }