package ServPak.jv;
import java.io.*;
import java.util.*;

public class InstallW {
    //Class

    public String printout;

    HashMap <String,String>data = new HashMap<String,String>();

    public InstallW(String queryline) throws Exception {
	//Constructor


/////////////////////////////////////////////////////////////////////////////////
 ///////////////////// Parsing GET query ///////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

	boolean sortmode = false;

	queryline = converter(queryline);                       // HEX conversion

          StringTokenizer info = new StringTokenizer(queryline,"&");

	     String testvalu,objectvalu,infotok;

	    while(info.hasMoreTokens()){
 		infotok    = info.nextToken();
		testvalu   = infotok.substring(0,infotok.indexOf("="));
		objectvalu = infotok.substring(infotok.indexOf("=")+1);

		data.put(testvalu,objectvalu);
             	     }


	    /////////////////// Query Parsed ////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////
          ////////////////////// Setting Up /////////////////////////
/////////////////////////////////////////////////////////////////////////////////

PrintWriter prt = new PrintWriter(new FileWriter("zserv.bat"),true);
  
String runedit = data.get("query");

String FMfile =  "ZEFM.jar";
String editonly = (runedit.startsWith("n")) 
                  ? " noedit":" +\""+data.get("hostname")+"\"";

String logout =data.get("logfile");

if(logout.length()>0) logout = " > "+data.get("logfile")+" 2>&1&";
if(!(logout.length()>0)) logout =  "";

prt.println("cd \\zefm\\ZigliFM");
prt.println("java -classpath "+
FMfile+" NetsManager.ZEFMServer "+data.get("portnumber")+editonly+logout);

prt.close();


/////////////////////////////////////////////////////////////////////////////////
   /////////////////////////Building Page/////////////////////////////////////

StringBuilder bufi = new StringBuilder();

bufi.append("<html>\n");
bufi.append("<head><title> Running Zigli's FM </title>\n");
bufi.append("<style type=\"text/css\">\n");
bufi.append("input { color: green; background-color: white}\n");
bufi.append("</style>\n");
bufi.append("</head>\n");
bufi.append("<body>\n");
bufi.append("<h1> Ready to Run </h1>\n");
bufi.append("<p>\n");
bufi.append("TO RUN THE SYSTEM: <p>\n");
bufi.append("In a console or (command) window<p>\n");
bufi.append("go to the directory \\zefm\\ZigliFM and run the command<p>\n");
bufi.append("<tt> zserv </tt>");
bufi.append("<p>(i.e., type zserv and hit enter)\n");
bufi.append("</body>\n");
bufi.append("</html>");
String name;

printout = bufi.toString();

}

    //////////////////////// Page Built/////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////////////////////
    //////////////// Assistant Methods ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

public static String converter(String y){

    String y0,y1,y2;
    int cut;

while(y.indexOf("%")>=0) {

	cut = y.indexOf("%");
  	 y0 = y.substring(0,cut);
	 y1 = y.substring(cut+1,cut+3);
	 y2 = y.substring(cut+3);

         y1 = String.valueOf((char) Byte.parseByte(y1,16));

         y  = y0+y1+y2;
}

return y;
     }
}