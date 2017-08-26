package Plugins;

import java.io.*;

public class GoRTL{

    public String printout;

    public GoRTL(String rfile) {

try{
            FileInputStream fins = new FileInputStream(rfile);
	byte[] data = new byte[fins.available()];
	fins.read(data);

	StringBuilder resultb = new StringBuilder(
"<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">"+
"\n<style> body{font-size: 150%} </style></head>\n"+
"<body dir=\"rtl\">\n\n");

	BufferedReader bufr = new BufferedReader(new StringReader(new String(data, "UTF-8")));
	for (String v; (v = bufr.readLine()) != null;) {
		resultb.append(v+"<br/>\n");
	}
	resultb.append("\n\n</body></html>");

	printout = resultb.toString();

}catch(Exception ioee){}
        }
    }

