package ServPak.jv;

import net.sf.saxon.Configuration;
import net.sf.saxon.Controller;
import net.sf.saxon.instruct.UserFunction;

import net.sf.saxon.om.*;
import net.sf.saxon.query.*;

import net.sf.saxon.value.IntegerValue;
import net.sf.saxon.value.Value;

import net.sf.saxon.xpath.*;

import javax.xml.transform.*;
import javax.xml.transform.stream.*;

import java.io.*;
import java.util.Properties;


public class Query {

	public String printout;
	String qry;
 	boolean quick;
	static String result;
            Properties props = new Properties();

	public Query(String in){

	if(in.startsWith("name=")) {
		String name = in.substring(in.indexOf("name=")+5);
		saveview(name);
try{
		DBgo go = new DBgo("tablename="+name+"&newtable=");
		printout = go.printout;
	}catch(Exception dbe){}
		return;
	}

	String query = "";
try{
if(in.endsWith("query=")){
		quick = true;
		query = in.substring(0, in.indexOf("query="));
		String[] line = query.split("&|=");
		qry = 
"for $i in doc(\"DB/"+line[1]+".xml\")/*/* let $j:=$i[contains("+line[3]+",\""+
line[5]+"\")] return $j";
	} else {
	            query = in.substring(in.indexOf("query=")+6);
		qry = query.replace('+',' ');
	}

		System.out.println("Running Query: "+qry);
		QResult(qry);

	}catch(Exception e){System.out.println(e.getMessage());}
	    }

	
	    public void QResult(String query) throws Exception {

		props.setProperty(OutputKeys.METHOD, "html");
                        props.setProperty(OutputKeys.INDENT, "yes");

	        final Configuration config = new Configuration();
	        final StaticQueryContext sqc = new StaticQueryContext(config);
	        final XQueryExpression exp = sqc.compileQuery(query);

	        final DynamicQueryContext dynamicContext = new DynamicQueryContext(config);
		ByteArrayOutputStream jack = new ByteArrayOutputStream();
	try{

	                      exp.run(dynamicContext, new StreamResult(jack), props);
	}catch (Exception ee){ 
		jack.write(new String("Error in "+query).getBytes());
		printout = jack.toString();
		}

		result = jack.toString();

       if(quick){			

		printout = view(result);

	    } else {		
	StringBuilder ss = new StringBuilder(view(result));
ss.append("\n\n<html>\n<body>\n\n<p/><form action=\"Query.jav\" method=\"get\"> Name &nbsp;");
	ss.append("<input type=\"text\" size=10 name=\"name\"/>&nbsp;");
	ss.append("<input type=\"submit\" value=\"Save\"/></form>\n</body>\n</html>");

		printout = ss.toString();	

	    }
    	}

	public static void main(String[] qubits){

		new Query(qubits[0]);

	}

	public static String view(String in){
		String[] rslt = in.split("\\n");
		StringBuilder sb = new StringBuilder("<?xml version=\"1.0\"?>\n\n<qresult>\n\n");
		for(String v : rslt) {
			v = v.trim().replaceAll("<entry>", "<entry>\n");
			sb.append(v.replaceAll("(</.*?>)", "$1\n"));		
		}
		sb.append("\n\n</qresult>");

		new NetsManager.Query(sb.toString(),"ServPak/xql/generic.xql",null,true);
		return NetsManager.Query.qtabby.toString();	
	}

	public static void saveview(String name){
		String[] rslt = result.split("\\n");
		StringBuilder sb = new StringBuilder("<?xml version=\"1.0\"?>\n\n");
		sb.append("<"+name+">\n\n");
		for(String v : rslt) {
			v = v.trim().replaceAll("<entry>", "<entry>\n");
			sb.append(v.replaceAll("(</.*?>)", "$1\n"));		
		}
		sb.append("\n\n</"+name+">");
try{
		FileOutputStream fout = new FileOutputStream("DB/"+name+".xml");
		fout.write(sb.toString().getBytes("UTF-8"));
		fout.flush();
		fout.close();
}catch(Exception fio){}
		System.out.println("Table written to "+"DB/"+name+".xml");
	}
     }