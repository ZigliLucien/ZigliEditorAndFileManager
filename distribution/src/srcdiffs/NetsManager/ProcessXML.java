package NetsManager;

import java.io.*;

import java.util.*;
import java.util.zip.*;
import java.sql.*;


public class ProcessXML {
    //Class
    String stylefile;
    String zipout;
 
    Connection conn;

    public ProcessXML(String xmlfile) throws Exception {
        this(xmlfile, null);
    }

    public ProcessXML(String xmlfile, String _stylefile)
        throws Exception {
        //Constructor

             conn = ZEdit.DOps.goMysql;

        String xfile = Commands.directory + "/" + xmlfile;

        if (_stylefile != null) {
            this.stylefile = _stylefile;
        }

        String dirname = System.getProperty("user.dir");

        if (!(new File(dirname + "/XML").exists())) {
            new File(dirname + "/XML").mkdir();
        }

     if(ZEFMServer.testKey(conn, xfile, "xml")  &&  
        ZEFMServer.rs.getLong("time") >= new File(xfile).lastModified()) {
            System.out.println("Unzipping " + xfile);
        } else {

	if(xmlfile.endsWith(".tpml") || TPMLCheck(xfile)) {

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

	zipout = sb.toString().trim();
    }

	///////////////////// GOTPML ///////////////////////

	public static StringBuilder goTPML(String filein){

	String conts = "";

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
 		conts = conts.replaceAll("\\s\\|\\s","</_><_>");
		conts = conts.replace("@@","</_>");
		conts = conts.replace("@","<_>");

		conts = conts.replaceAll("\\\\section\\{(.*?)\\}","<section id=\"$1\">");
		conts = conts.replaceAll("\\\\subsection\\{(.*?)\\}","<subsection id=\"$1\">");
		conts = conts.replaceAll("\\\\subsubsection\\{(.*?)\\}","<subsubsection id=\"$1\">");
		conts = conts.replaceAll("\\\\paragraph\\{(.*?)\\}","<paragraph id=\"$1\">");
		conts = conts.replaceAll("\\\\subparagraph\\{(.*?)\\}","<subparagraph id=\"$1\">");

		conts = conts.replace("<::","<display>");
		conts = conts.replace("::>","</display>");

		conts = conts.replace("<:|","<xmth><_>");
		conts = conts.replace("|:>","</_></xmth>");
		conts = conts.replace("<||","<row><_>");
		conts = conts.replace("||>","</_></row>");

		conts = conts.replace("<:","<xmth>");
		conts = conts.replace(":>","</xmth>");
		conts = conts.replace("<|","<row>");
		conts = conts.replace("|>","</row>");


	conts = conts.replaceAll("(.)\\^\\{(.*?)\\}","$1<sup>$2</sup>");
	conts = conts.replaceAll("(.)_\\{(.*?)\\}","$1<sub>$2</sub>");	

	conts = conts.replaceAll(
		"\\\\(frac)\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
		"<$1 width=\"$4\"><numer>$2</numer><denom>$3</denom></$1>");

	conts = conts.replaceAll(
		"\\\\(frac)\\{(.*?)\\}\\{(.*?)\\}",
		"<$1><numer>$2</numer><denom>$3</denom></$1>");

	conts = conts.replaceAll(
		"\\\\(choose)\\{(.*?)\\}\\{(.*?)\\}",
		"<$1><uu>$2</uu><ll>$3</ll></$1>");

	conts = conts.replaceAll(
		"\\\\(sum|prod|int)\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
		"<$1><ll>$2</ll><uu>$3</uu>$4</$1>");

		conts = conts.replaceAll(
		"\\\\sumtype\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}\\{(.*?)\\}",
"<sumtype limsize=\"-1\"><ll>$1</ll><uu>$2</uu><symbol symsize=\"3\">$3</symbol>$4</sumtype>");

	conts = conts.replaceAll(
		"\\\\sym\\{(.*?)\\}\\{(.*?)\\}",
		"<symbol symsize=\"$1\">$2</symbol>");

	conts = conts.replaceAll("(\\w)\\^(.)\\b","$1<sup>$2</sup>");
	conts = conts.replaceAll("(\\w)_(.)\\b","$1<sub>$2</sub>");

	conts = conts.replaceAll("\\\\\\\\(\\w+)\\b","</$1>");	
	conts = conts.replaceAll("\\\\(\\w+)\\\\","&$1;");
	conts = conts.replaceAll("\\\\(\\w+)\\b","<$1>");
}catch(Exception eon){}

	System.out.println("Preprocessing "+filein);

	return new StringBuilder(conts);

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