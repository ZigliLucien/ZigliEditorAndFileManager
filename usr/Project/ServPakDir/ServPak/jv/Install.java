package ServPak.jv;
import java.io.*;
import java.util.*;

public class Install {
    //Class

    public String printout;

    HashMap <String,String>data = new HashMap<String,String>();

    public Install(String queryline) throws Exception {
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

BufferedReader bin = new BufferedReader(new FileReader("Modes.properties"));

PrintWriter pout = new PrintWriter(new FileWriter("Modesprops"));

String javapath = data.get("pathtojava");

if(!javapath.startsWith("/")) javapath ="/"+javapath;
if(!javapath.endsWith("/")) javapath +="/";

for(String v;(v=bin.readLine())!=null;) {
if(! v.startsWith("Java=")) {
pout.println(v);
continue;
}
pout.println("Java="+javapath+"javac");
}

pout.close();

FileInputStream fin2 = new FileInputStream("Modesprops");
FileOutputStream fout2 = new FileOutputStream("Modes.properties");

byte[] filedata = new byte[fin2.available()];

fin2.read(filedata);
fout2.write(filedata);
fout2.flush();
fout2.close();

new File("Modesprops").delete();

String runedit = data.get("query");

String FMfile =  "ZEFM.jar";
String editonly = (runedit.startsWith("n")) 
                  ? " noedit":" +\""+data.get("hostname")+"\"";

String logout =data.get("logfile");

if(logout.length()>0) logout = " > "+data.get("logfile")+" 2>&1&";
if(!(logout.length()>0)) logout =  "";

PrintWriter prt = new PrintWriter(new FileWriter("/usr/local/ZigliFM/zserv"),true);
prt.println("cd /usr/local/ZigliFM");
prt.println(javapath+
"java -classpath "+FMfile+" NetsManager.ZEFMServer "+data.get("portnumber")+editonly+logout);
prt.close();

try{
               Runtime local = Runtime.getRuntime();
	       Process opt   = local.exec("chmod 755 zserv");
	       opt.waitFor();
}catch(Exception ex){}


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
bufi.append("go to the directory /usr/local/ZigliFM and run the command<p>\n");
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