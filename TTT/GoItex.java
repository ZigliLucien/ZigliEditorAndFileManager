import ServPak.jv.*;
import java.io.*;
import NetsManager.ZEFMServer;

public class GoItex{
	public String printout;
	String runfile;
	String filename;
 
    public GoItex(String cmd) {

		String basename = cmd.substring(0,cmd.lastIndexOf("."));

		String filextout = basename+".xhtml";
try{
System.out.println("Converting itex file: "+cmd+" to "+filextout);

	System.loadLibrary("itex2MML");

	FileInputStream fins = new FileInputStream(cmd);
	byte[] data = new byte[fins.available()];
	fins.read(data);

	String output =  "HELLO";
	String inp = clear(new String(data));

		int x = itex2MML.itex2MML_html_filter(inp,(long)inp.length());

		if(x==0) output = itex2MML.itex2MML_output();

	FileOutputStream foutxx = new FileOutputStream(filextout);
	foutxx.write(output.getBytes("UTF-8"));
	foutxx.close();
}catch(Exception ee){}
	printout = "<html><head> <script> window.location='"+filextout+"'</script></head><body></body></html>";
		
       }

	/////////////////////// CLEAR ////////////////////////

	String clear(String inn){

	StringBuilder bff = new StringBuilder(8193);
	String v = "";

try{
BufferedReader br = new BufferedReader(new StringReader(inn));
	
	for(String w;(w=br.readLine())!=null;) {

/*
		if(w.trim().length()==0) {
			bff.append("<p/>\n");
			continue;
		}
*/
		bff.append(w+"\n");
	}

		v = bff.toString();
		String elts =
"section|subsection|subsubsection|paragraph|subparagraph|lemma|proposition|theorem|remark|example|corollary|proof";
		v = v.replaceAll(
			"\\\\("+elts+")\\{(.*?)\\}\\{(.*?)\\}",
			"<div class=\"$1\" id=\"$2\" name=\"$3\">");
		v = v.replaceAll(
		"\\\\begin\\{("+elts+")\\}\\{(.*?)\\}\\{(.*?)\\}",
			"<div class=\"$1\" id=\"$2\" name=\"$3\">");
		v = v.replaceAll(
		"\\\\end\\{("+elts+")\\}",
			"</div>");
		v = v.replaceAll(
		"\\\\\\\\("+elts+")",
			"</div>");

		v = v.replaceAll(
			"\\\\("+elts+")\\{(.*?)\\}",
			"<div class=\"$1\" id=\"$2\">");
		v = v.replaceAll(
			"\\\\begin\\{("+elts+")\\}\\{(.*?)\\}",
			"<div class=\"$1\" id=\"$2\">");
	
		v = v.replaceAll(		
			"\\\\(lemma|proposition|theorem|remark|example|corollary|proof)",
			"<div class=\"$1\">");
		v = v.replaceAll(		
			"\\\\begin\\{(lemma|proposition|theorem|remark|example|corollary|proof)\\}",
			"<div class=\"$1\">");

}catch(Exception ee){}
			 return v;
       }

public static void main(String[] args) {
		new GoItex(args[0]);
	}
}