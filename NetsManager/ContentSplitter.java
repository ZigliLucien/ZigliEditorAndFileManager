package NetsManager;

import java.io.*;
import java.util.*;
import java.sql.*;

public class ContentSplitter {

	boolean contsflag;
	boolean output;
              boolean named;
	String name;
	String mimxt = "txt";
	PrintWriter pwt;
	int counter;

	String prefix;
	String prefixdir;
	String postfix;


    public ContentSplitter(String filename, String user) {
        try {

	 prefix = "INBOXES/"+user;
       	 prefixdir = System.getProperty("user.dir").replace('\\', '/');

		if(!new File(prefixdir+"/"+prefix).isDirectory()) 
			new File(prefixdir+"/"+prefix).mkdirs();

	              if (prefixdir.indexOf(":") >= 0) 
	                          prefixdir = prefixdir.substring(prefixdir.indexOf(":") +1);

	Properties mimexts = new Properties();

	InputStream infile = new FileInputStream("MimeExtensions.properties"); 
	mimexts.load(infile);
         
	BufferedReader buf = new BufferedReader(new FileReader(filename));

	for(String v; (v=buf.readLine())!=null;){

			v = XmlMail.fixAmps(v);
	
	if(v.trim().toLowerCase().startsWith("content-type") && ! v.toLowerCase().contains("multipart")) {
			contsflag = true;
			mimxt = "txt";
	for(Enumeration enume=mimexts.keys();enume.hasMoreElements();){
			String testext = enume.nextElement().toString();
			if(v.toLowerCase().indexOf(testext)>=0) {
					mimxt = mimexts.getProperty(testext);
					System.out.println("Mime-type "+mimxt);
					break;
			}
		}
			name = filename+"."+counter+"."+mimxt;
			counter++;
            }

	if(mimxt.equals("html") || counter==1 ) contsflag = false;

	if(!contsflag) continue;

	if(!named && v.contains("name=\"")){

		int cut = v.indexOf("name=\"");
		String prename = v.substring(cut+6);
	               name = prename.substring(0,prename.indexOf("\""));
		   named = true;
 		   continue;
	}

	if(!output && contsflag && v.trim().length()==0) {
		output = true;
		String outname = name;
		if(! outname.endsWith(".txt") && ! outname.endsWith("html")) outname += ".mime";
	
		 postfix = outname.substring(outname.lastIndexOf("/")+1);
	
  		 outname = prefixdir+"/"+prefix+"/"+postfix;
  		      name = prefixdir+"/"+prefix+"/"+name.substring(name.lastIndexOf("/")+1);

	            if(new File(outname).exists() || new File(name).exists() || mimxt.equals("txt")){ 
			output = false;
			contsflag = false;
			named = false;
			continue;
		}

		pwt = new PrintWriter(new FileWriter(outname),true);
		System.out.println("Mime Part "+outname);

		continue;
	}

	if(!output) continue;
	if(v.startsWith("--")){

try{
		String postt = postfix;
		if(postt.endsWith(".mime")) postt = postfix.substring(0,postfix.lastIndexOf(".mime"));

		 String postf = filename.substring(filename.lastIndexOf("/")+1);
		 String prereq0 = prefixdir.replace('/','_') + "_" +prefix.replace('/', '_') +"."+postf;
		 String prereq = prefixdir.replace('/','_') + "_" +prefix.replace('/', '_') +"."+postt;

 	             Connection conn = ZEdit.DOps.goMysql;

		byte[] data = ZEFMServer.getFile(conn, prereq0,"annotations");
		ZEFMServer.goSave(conn, prereq,  new String(data), "annotations");

}catch(Exception ql){ System.out.println(ql.getMessage());}

		output = false;
		contsflag = false;
		named = false;
		pwt.close();
		continue;
	}
			if(output) pwt.println(v);
	}

	if(pwt !=null) pwt.close();

        } catch (Exception e) {
	System.out.println(e.getMessage());
        }
    }
}
