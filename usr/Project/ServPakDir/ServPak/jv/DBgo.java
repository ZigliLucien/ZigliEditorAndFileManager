/* DBgo - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

import NetsManager.Traxit;
import NetsManager.Query;
import NetsManager.ZConnection;
import NetsManager.ZEFMServer;

import java.io.*;

import java.util.*;


public class DBgo {
    static String filename;
    static String[][] tableset;
     StringBuilder stringbuffer;
     PrintWriter printwriter;
    public String printout;
    static  String[] champs;
	static String fname;
	public static String entryname;
	String elements;
	String[] elts;

    /////////////////////////////////////////////////////////
    ///////////////////// CONSTRUCTOR /////////////////////
    /////////////////////////////////////////////////////////
    public DBgo(String string) throws Exception {
        if (!new File("DB").exists()) {
            new File("DB").mkdir();
        }

        boolean bool = false;
        boolean showtable = true;
        HashMap<String,String> hashmap = parseQuery(string);

        if (string.indexOf("tablename") > -1) {
            filename = hashmap.get("tablename");

            int i = filename.indexOf("=");

            filename = filename.substring(i + 1);
            filename = filename.replace('+', '_');

	 fname = "DB/" + filename + ".xml";
	entryname = "entry";

	String direc = fname.substring(0,fname.lastIndexOf('/'));
	if(! new File(direc).isDirectory()) new File(direc).mkdirs();

	if(new File(fname).exists()) {
		elements = new String(new Traxit(fname,"ServPak/xsl/listElements.xsl").tabby);
		elts = elements.split("!");
	 	entryname = elts[1].trim();
	}

            File file = new File(fname);

	System.out.println("OK "+entryname);

            if (hashmap.get("newtable") != null) {
                String hmap = hashmap.get("newtable");

                printwriter = new PrintWriter(new FileWriter(fname), true);
                stringbuffer = new StringBuilder();

	    String xmlname = filename.substring(filename.lastIndexOf('/')+1);	

                stringbuffer.append("<?xml version=\"1.0\"?>\n");
                stringbuffer.append("<" + xmlname + ">\n\n");
                stringbuffer.append("<"+entryname+">\n");
                stringbuffer.append("<" + hmap + "> - </" + hmap + ">");
                stringbuffer.append("\n</"+entryname+">");
                stringbuffer.append("\n\n</" + xmlname + ">");
                printwriter.print(stringbuffer.toString());
                printwriter.close();
            }

            if (hashmap.containsKey("tableview")) {
                String ldir = ZEFMServer.localdir;

                if (ldir.indexOf(":") > 0) {
                    int ii = ldir.indexOf(":");

                    ldir = ldir.substring(ii + 1);
                    ldir = ldir.replace('\\', '/');
                }

                String out0 = (ldir + "/DB/" + filename);

                stringbuffer = new StringBuilder(
	  "<html><head><meta http-equiv=\"refresh\" content=\"url=0;"+out0+".sdb\"></head>\n");
	    stringbuffer.append("<body><h2> To " + filename + "</h2><p>\n");
                stringbuffer.append("<a href=" + out0 + ".sdb> Go to " +
                    filename + "</a><p>\n</body></html>");
                printout = stringbuffer.toString();

                return;
            }
        } else {
            	     getFields(fname);
            tableset = readXML(fname, champs.length);

            if (hashmap.containsKey("addrow")) {
                tableset = addRow(tableset);
            }

            if (hashmap.containsKey("addfield")) {
                addField(fname, hashmap.get("addfield"));
                bool = true;
            }

            if (hashmap.containsKey("change")) {
                printout = changeMode(tableset).toString();
                return;
            }

            if (hashmap.containsKey("editmode")) {
                tableset = editMode(hashmap, tableset.length, tableset[0].length);
                champs = tableset[0];
            }

            if (hashmap.containsKey("searchsort")) {
                printout = goSearch(filename, champs).toString();

                return;
            }

            if (hashmap.containsKey("analyze")) {
                new DBanalyze(tableset, filename);
                printout = getFile("HTML/dbanalyze.html");
                showtable = false;
            }

            if (hashmap.containsKey("rcops")) {
                new DBrcops(tableset, filename);
                printout = getFile("HTML/dbrcops.html");
                showtable = false;
            }

    	 if (hashmap.containsKey("goquery")) {
                printout = getFile("HTML/query.html");
                showtable = false;
            }

            if (hashmap.containsKey("formentry")) {
                printout = formEntry(champs).toString();

                return;
            }

            if (hashmap.containsKey("formmode")) {
                string = DBM.converter(string);

                int q = 0;
                String[] newrow = string.split("&");

                for (String x : newrow) {
                    newrow[q] = x.substring(x.indexOf("=") + 1).replace('+', ' ');
	        q++;
                }

                tableset = addRow(tableset, newrow);
            }

            if (!bool) {
                writeXML(filename, tableset);
            }
        }

        if (showtable) {
            printout = showTable(fname);
        }
    }

///////////// ADDROW /////////
    String[][] addRow(String[][] tablein) {
        int cols = tablein[0].length;
        String[] newrow = new String[cols];

        Arrays.fill(newrow, "-");

        return addRow(tablein, newrow);
    }

    String[][] addRow(String[][] tablein, Object[] newrow) {
        String[][] localtable = new String[tablein.length + 1][tablein[0].length];

        for (int i = 0; i < tablein.length; i++) {
            for (int j = 0; j < tablein[0].length; j++) {
                localtable[i][j] = tablein[i][j];
            }
        }

        for (int i = 0; i < tablein[0].length; i++) {
            localtable[tablein.length][i] = newrow[i].toString();
        }

        return localtable;
    }

//////// ADDFIELD ////////////
    void addField(String basename, String fld) throws Exception {
        new Traxit(basename, "ServPak/xsl/newfield.xsl", fld);
        
        FileOutputStream fts = new FileOutputStream(basename);

        fts.write(Traxit.tabby);
        fts.flush();
        fts.close();

    }

/////////// FORMENTRY //////
    StringBuilder formEntry(String[] fields) throws Exception {
        stringbuffer = new StringBuilder();

        stringbuffer.append("<html>\n");
        stringbuffer.append("<head><title>" + filename + "</title>\n");
        stringbuffer.append("</head>\n");
        stringbuffer.append("<body bgcolor=#eeeeee>\n");
        stringbuffer.append("<h2> Entry  </h2>");
        stringbuffer.append(
            "<form action=\"DBgo.jav\" method=\"get\"><table width=\"90%\">");

        for (int q = 0; q < fields.length; q++) {
            stringbuffer.append("<tr>");
            stringbuffer.append("<th align=right>" + dataCheck(champs[q]) + "&nbsp;&nbsp;</th>");
            stringbuffer.append("<td><input name=" + champs[q] + " size=20></td></tr>\n");
            stringbuffer.append("<tr><th><br></th><td><br></td></tr>\n");
        }

        stringbuffer.append(
            "</table><input type=submit value=GO name=formmode></form>");
        stringbuffer.append(
            "<p><b>Note:</b>Please use a -, a dash, for blank entries.\n");
        stringbuffer.append("</body>\n");
        stringbuffer.append("</html>\n");

        return stringbuffer;
    }

////// CHANGEMODE /////
    StringBuilder changeMode(String[][] strings) throws Exception {	

        stringbuffer = new StringBuilder();

        int i = strings[0].length;
        int hsize = -2 + Math.round((float) (90 / i));

        stringbuffer.append("<html>\n");
        stringbuffer.append("<head><title>" + filename + "</title>\n");
        stringbuffer.append("</head>\n");
        stringbuffer.append("<body>\n");
        stringbuffer.append("<h2> Editing " + filename + "</h2>");
        stringbuffer.append(
            "<form action=\"DBgo.jav\" method=\"get\"><table width=\"90%\">");
        stringbuffer.append("<tr>");

        for (int q = 0; q < i; q++) {
            stringbuffer.append("<th>" + champs[q] + "</th>");
        }

        stringbuffer.append("</tr>\n");

        for (int q = 0; q < strings.length; q++) {
            stringbuffer.append("<tr>");

            for (int qq = 0; qq < i; qq++) {
                String string = strings[q][qq];

                string = DBM.fixgtlt(string);
                stringbuffer.append(
	"<td width=\"" + hsize + "%\"><input name=\"" + q + "," + qq + "\" value=\"" +
                string + "\" size=\"" + hsize + "\"></td>\n");
            }

            stringbuffer.append("</tr>\n");
        }

        stringbuffer.append("</table><input type=submit value=GO name=editmode></form>");
        stringbuffer.append("</body>\n");
        stringbuffer.append("</html>\n");

        return stringbuffer;
    }

/////////// EDITMODE /////////

    String[][] editMode(HashMap<String, String> hashmap, int i, int j) throws Exception {
        String[][] strings = new String[i][j];

        for (int q = 0; q < i; q++) {
            for (int q1 = 0; q1 < j; q1++) {
	    String string = hashmap.get(String.valueOf(q) + "," + String.valueOf(q1));

                strings[q][q1] = string.replace('+', ' ');
            }
        }

        return strings;
    }

	//////////////// READXML //////////////////////////////
    public static String[][] readXML(String basename, int i) throws Exception {

	try{
	new NetsManager.Query(
		new FileInputStream(basename), "for $i in /*/* return data($i)");
	}catch (Exception ee){
		ee.printStackTrace();
	 }

	BufferedReader buff = new BufferedReader(
		new StringReader(NetsManager.Query.qtabby.toString()));

	Stack<String[]> staci = new Stack<String[]>();

	staci.push(champs);

	String[] line = new String[i];
	int cc = 0;
	int ccc = 0;

	for(String v;(v=buff.readLine())!=null;){

	ccc = (cc % (i+1));
	  cc++;

	if(ccc>0){	
		line[ccc-1] = ZEdit.MailFiles.ampcheck(v);
	}		

	if((cc % (i+1)) == 0) { 
			staci.push(line);
			line = new String[i]; 
		}
	}

	           String[][] tbl = new String[staci.size()][i];

		staci.toArray(tbl);

   	            return tbl;
    }

///////// WRITEXML ////////
    void writeXML(String name, String[][] table) throws Exception {
        printwriter = new PrintWriter(new FileWriter("DB/" + name + ".xml"),
                true);
        stringbuffer = new StringBuilder();

        String _name = name.substring(name.lastIndexOf("/")+1);
        String _entry = entryname;
        String[] _row = table[0];

        stringbuffer.append("<?xml version=\"1.0\"?>\n");
        stringbuffer.append("<" + _name + ">\n");

        for (int i = 1; i < table.length; i++) {

            String[] localrow = table[i];

            stringbuffer.append("\n<" + _entry + ">\n");

            for (int q = 0; q < localrow.length; q++) {
                String rname = _row[q].toLowerCase();

                stringbuffer.append("<" + rname + ">" +
                    localrow[q] + "</" + rname + ">\n");
            }

            stringbuffer.append("</" + _entry + ">\n");
        }

        stringbuffer.append("\n</" + _name + ">");
        printwriter.print(stringbuffer.toString());
        printwriter.close();
    }

//////// SHOWTABLE /////////
    static String showTable(String basename) throws Exception {

	FileInputStream fins = new FileInputStream(basename);
	new Query(fins, "ServPak/xql/dbgeneric.xql", DBM.zefmhome, true);
	return Query.qtabby.toString();
    }

////// HASHMAP ///////
    public static HashMap<String,String> parseQuery(String string) {
        HashMap<String,String> hashmap = new HashMap<String,String>();
        String query = string.substring(string.indexOf("?") + 1);

	if(query.length()==0) return hashmap;

        query = DBM.converter(query);
        String[]querystring = query.split("&");

	for (String querybit : querystring){
            String testvalu = querybit.substring(0, querybit.indexOf("="));
            String objectvalu = "";

            if (!querybit.endsWith("=")) {
                objectvalu = querybit.substring(querybit.indexOf("=") + 1);
            } else {
                objectvalu = null;
            }
                hashmap.put(testvalu, objectvalu);
        }

        return hashmap;
    }

/////////// GOSEARCH /////

    StringBuilder goSearch(String string, String[] strings)
        throws Exception {
        stringbuffer = new StringBuilder();

        int i = strings.length;

        stringbuffer.append("<html>\n");
        stringbuffer.append("<head><title>" + string + "</title>\n");
        stringbuffer.append("</head>\n");
        stringbuffer.append("<body>\n");
        stringbuffer.append("<h2> Search/Sort " + string + "</h2>");
        stringbuffer.append("Check the fields you want to sort on.<p>");
        stringbuffer.append("<form action=\"DBM.jav\" method=\"get\">");
        stringbuffer.append("<table>");
        stringbuffer.append("<tr>");

        for (int q = 0; q < i; q++) {
            stringbuffer.append("<td><input type=checkbox name=" +
                strings[q] + ">" + dataCheck(strings[q]) + "</td>");
        }

        stringbuffer.append("</tr><tr>");
        stringbuffer.append("<td align=left colspan=" + i + ">");
        stringbuffer.append(
            "Enter default field for sorting (if numerical, starts with 'zz')&nbsp;");
        stringbuffer.append("<select name=sortdefault>\n");

        for (int q = 0; q < strings.length; q++) {
            stringbuffer.append("<option>" + strings[q] + "</option>\n");
        }

        stringbuffer.append("</select>\n</td>");
        stringbuffer.append("</tr>");
        stringbuffer.append(
            "<tr><td> <b>View</b> (check one)</td><td> <input type=radio name=style value=search> Directory style<br><input type=radio name=style value=table>Table style</td></tr>");
        stringbuffer.append("</table><input type=submit value=GO name=\"dbase=" +
            string + "&entry="+entryname+"&fields=");

        for (int q = 0; q < (i - 1); q++) {
            stringbuffer.append(strings[q] + ",");
        }

        stringbuffer.append(strings[i - 1] + "\">");
        stringbuffer.append("</body>\n");
        stringbuffer.append("</html>\n");

        return stringbuffer;
    }
	
	/////// GET FIELDS ////////
    static void getFields(String basename) throws Exception {

	BufferedReader buf = new BufferedReader(new FileReader(basename));

	boolean flag = false;
	Stack<String> staci = new Stack<String>();

	for(String v;!(v=buf.readLine()).contains("</"+entryname+">");) {
		if(v.contains("<"+entryname+">")) { flag = true; continue; }
		if(!flag) continue;
		String[] line = v.trim().split("\\s+|<|>");
		staci.push(line[1]);
	}

		champs = new String[staci.size()];
		staci.toArray(champs);
    }

/////////////// DATACHECK /////////
    static String dataCheck(String string) {
        if (string.startsWith("zz")) {
            string = string.substring(string.indexOf("zz") + 2);
        }
        return string;
    }

    public static String getFile(String fname) throws Exception {
        	InputStream din = ClassLoader.getSystemResourceAsStream(fname);

	ByteArrayOutputStream bout = new ByteArrayOutputStream();

	for(int i=0; (i=din.read())!=-1;) bout.write(i);


	return bout.toString();
    }
}