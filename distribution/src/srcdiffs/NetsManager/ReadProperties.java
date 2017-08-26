package NetsManager;

import java.io.*;
import java.util.Properties;


public class ReadProperties {
 
    public byte[] out;

    public ReadProperties(String input) throws Exception {

		Properties props = new Properties();

		InputStream ins = new FileInputStream(input);
		props.load(ins);

		OutputStream bout = new ByteArrayOutputStream();	

		props.store(bout, input.substring(input.lastIndexOf("/")+1));

		BufferedReader buf = new BufferedReader(new StringReader(bout.toString()));

		StringBuilder sb = new StringBuilder("<?xml version=\"1.0\"?>\n");
		sb.append("<properties>\n");

		for(String v;(v=buf.readLine()) != null;) {
		String[] tmp = v.split("=");
		sb.append("<entry key="+tmp[0]+">"+tmp[1]+"</entry\n");
		}

			sb.append("</properties>");
	System.out.println(sb.toString());
			out =   sb.toString().getBytes("UTF-8");
    }
}