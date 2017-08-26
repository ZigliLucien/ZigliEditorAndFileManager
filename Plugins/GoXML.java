package Plugins;

import ZEdit.DOps;
import NetsManager.*;
import java.io.*;

import java.util.*;
import java.util.zip.*;
import java.sql.*;


public class GoXML {
    //Class
    String stylefile;
    public String printout;
    static String dirname;
 
    Connection conn;

    public GoXML(String xfile) throws Exception {
        this(xfile, null);
    }

    public GoXML(String xfile, String _stylefile)
        throws Exception {
        //Constructor

             conn = ZEdit.DOps.goMysql;

        if (_stylefile != null) {
            this.stylefile = _stylefile;
        }

        	 dirname = System.getProperty("user.dir");

        if (!(new File(dirname + "/XML").exists())) {
            new File(dirname + "/XML").mkdir();
        }

     if(ZEFMServer.testKey(conn, xfile, "xml")  &&  
        ZEFMServer.rs.getLong("time") >= new File(xfile).lastModified()) {
            System.out.println("Unzipping " + xfile);
        } else {

	if(xfile.endsWith(".tpml") || TPMLCheck(xfile)) {

		new Traxit(goTPML(xfile),"ServPak/xsl/tpw.xsl",xfile);

	} else {

     	       if (_stylefile != null) {
            	    new Traxit(xfile, stylefile);
	            } else {
            	    new Traxit(xfile);
	            }
	}
     
            byte[] din = Traxit.tabby;

            if (din.length > 0) {
                ZEFMServer.Zipper(conn, xfile, din, "xml");
            }
        }

	BufferedReader buf = ZEFMServer.getZipFile(conn, xfile,"xml");
	StringBuilder sb = new StringBuilder(4097);	

	for(String v;(v=buf.readLine())!=null;){
		sb.append(v+"\n");
	}

	printout = sb.toString().trim();
    }

	///////////////////// GOTPML ///////////////////////

	public static StringBuilder goTPML(String filein){

	String conts = "";
	StringBuilder bff = new StringBuilder(8193);

try{
		FileInputStream fins = new FileInputStream(filein);
		byte[] data = new byte[fins.available()];
		fins.read(data);
		fins.close();

		conts = new String(data,"UTF-8");

		String x,y,z;
		int i,j;

 for (/**/; conts.indexOf("\\ref{") >= 0; conts = x + y + z) {
            i = conts.indexOf("\\ref{");

            x = conts.substring(0, i);

	j = conts.substring(i+5).indexOf("}");

            y = conts.substring(i +5,i+5+j);
            z = conts.substring(i +6+j);

	y = "<notes link=\""+XCommands.hexml(y)+"\">"+y+"</notes>";

        }

	String v = "";
try{
	BufferedReader br = new BufferedReader(new StringReader(conts));
	
	for(String w;(w=br.readLine())!=null;) {

	if(w.trim().equals("<tpwm>")){
		bff.append("<tpwm>\n");
bff.append("<script type='text/javascript' src='/ServPak/js/jquery.js'></script>\n");
bff.append("<script type='text/javascript' src='/ServPak/js/mathformat.js'></script>\n");
bff.append("<link rel='stylesheet' type='text/css' href='/ServPak/css/math.css'/>\n");

		continue;
	}

		if(w.trim().length()==0) {
			bff.append("<br/>\n");
			continue;
		}

	String[] line = w.split("`");

	for(int q=0;q<line.length;q=q+2){

		v = line[q];

		v = v.replaceAll("\\s\\|\\s","</_><_>");
		v = v.replace("@@","</_>");
		v = v.replace("@","<_>");

		v = v.replaceAll(
			"\\\\(section|subsection|subsubsection|paragraph|subparagraph)\\{(.*?)\\}\\{(.*?)\\}",
			"<$1 id=\"$2\" name=\"$3\">");
		v = v.replaceAll(
		"\\\\begin\\{(section|subsection|subsubsection|paragraph|subparagraph)\\}\\{(.*?)\\}\\{(.*?)\\}",
			"<$1 id=\"$2\" name=\"$3\">");
		v = v.replaceAll(
		"\\\\end\\{(section|subsection|subsubsection|paragraph|subparagraph)\\}",
			"</$1>");
		v = v.replaceAll(
		"\\\\\\\\(section|subsection|subsubsection|paragraph|subparagraph)",
			"</$1>");

		v = v.replaceAll(
			"\\\\(section|subsection|subsubsection|paragraph|subparagraph)\\{(.*?)\\}",
			"<$1 id=\"$2\">");
		v = v.replaceAll(
			"\\\\begin\\{(section|subsection|subsubsection|paragraph|subparagraph)\\}\\{(.*?)\\}",
			"<$1 id=\"$2\">");
	
		v = v.replaceAll(		
			"\\\\(lemma|proposition|theorem|remark|example|corollary)\\{(.*?)\\}\\{(.*?)\\}",
			"<$1 name=\"$2\" id=\"$3\">");
		v = v.replaceAll(		
			"\\\\begin\\{(lemma|proposition|theorem|remark|example|corollary)\\}\\{(.*?)\\}\\{(.*?)\\}",
			"<$1 name=\"$2\" id=\"$3\">");
		v = v.replaceAll(		
			"\\\\\\\\(lemma|proposition|theorem|remark|example|corollary)",
			"</$1>");
		v = v.replaceAll(		
			"\\\\end\\{(lemma|proposition|theorem|remark|example|corollary)\\}",
			"</$1>");


		v = v.replaceAll(		
			"\\\\(lemma|proposition|theorem|remark|example|corollary)\\{(.*?)\\}",
			"<$1 name=\"$2\">");
		v = v.replaceAll(		
			"\\\\begin\\{(lemma|proposition|theorem|remark|example|corollary)\\}\\{(.*?)\\}",
			"<$1 name=\"$2\">");

		v = v.replaceAll(		
			"\\\\(lemma|proposition|theorem|remark|example|corollary)",
			"<$1>");
		v = v.replaceAll(		
			"\\\\begin\\{(lemma|proposition|theorem|remark|example|corollary)\\}",
			"<$1>");

		v = v.replace("<::","<display>");
		v = v.replace("::>","</display>");

		v = v.replace("<:|","<xmth><_>");
		v = v.replace("|:>","</_></xmth>");
		v = v.replace("<||","<row><_>");
		v = v.replace("||>","</_></row>");

		v = v.replace("<:","<xmth>");
		v = v.replace(":>","</xmth>");
		v = v.replace("<|","<row>");
		v = v.replace("|>","</row>");

		v = v.replaceAll(
		"\\.\\.(frac)\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
		"<$1 width=\"$4\"><numer>$2</numer><denom>$3</denom></$1>");

		v = v.replaceAll(
			"\\.\\.(frac)\\{(.*?)\\}\\{(.*?)\\}",
			"<$1><numer>$2</numer><denom>$3</denom></$1>");

		v = v.replaceAll(
			"\\.\\.(choose)\\{(.*?)\\}\\{(.*?)\\}",
			"<$1><uu>$2</uu><ll>$3</ll></$1>");

		v = v.replaceAll(
			"\\.\\.(sum|prod|int)\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
			"<$1><ll>$2</ll><uu>$3</uu>$4</$1>");

		v = v.replaceAll(
		"\\.\\.sumtype\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
"<sumtype limsize=\"-1\"><ll>$1</ll><uu>$2</uu><symbol symsize=\"3\">$3</symbol>$4</sumtype>");

	v = v.replaceAll(
			"\\.\\.sym\\{(.*?)\\}\\{(.*?)\\}",
			"<symbol symsize=\"$1\">$2</symbol>");

		line[q] = v;
	}
		w = line[0];

	if(line.length>1) {

		for(int q=1;q<line.length;q=q+2){
			w = w.concat("`"+line[q]+"`");
			if(q+1<line.length) w = w.concat(line[q+1]);	
		}
	}

		w = w.replaceAll("\\.\\.\\\\(\\w+)\\b","</$1>");	
		w = w.replaceAll("\\\\end\\{(.*?)\\}","</$1>");	
		w = w.replaceAll("\\\\begin\\{(.*?)\\}","<$1>");
		w = w.replaceAll("\\.\\.(\\w+)\\b","<$1>");

		bff.append(w+"\n");
	}

}catch(Exception ee){}
}catch(Exception eon){}

	System.out.println("Preprocessing "+filein);

	return bff;

	}

	///////////// TPML Check ////////////////
	boolean TPMLCheck(String filename) throws Exception{
	
	boolean result = false;
	String v = "";

		BufferedReader buf = new BufferedReader(new FileReader(filename));
		for(int q=0;q<5 && v !=null;q++) {
			v = buf.readLine();
			if(v.contains("tpw.xsl") || v.contains("<tpwm>")) result = true;		
		}

	return result;
	}
}