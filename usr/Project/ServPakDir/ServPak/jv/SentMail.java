package ServPak.jv;

import NetsManager.*;
import java.io.*;

public class SentMail{

	public String printout;

    public SentMail(String cmd) throws Exception{


if(cmd.contains("ENTRY")) {

		byte[] out = new String("HELLO").getBytes();

		ServPak.jv.MySQL data = new ServPak.jv.MySQL("MySQL.jav?"+cmd);	
		String listing = data.printout;	

		String query = "for $i in //tr let $k:=$i//th/node() let $j:=$i//td//pre/node() return element{$k}{$j}";

		
		listing = "<?xml version=\"1.0\"?>\n"+listing;

		BufferedReader bfr = new BufferedReader(new StringReader(listing));
		StringBuilder sbd = new StringBuilder();
	
	for(String v;(v=bfr.readLine()) !=null;){

		v = v.replaceAll("&nbsp;"," ");
		v = v.replaceAll("<br>","<br/>");
		v = v.replaceAll("align=center","align='center'");
		v = v.replaceAll("<(\\w*?@.*?)>","&lt;$1&gt;");
		if(v.startsWith("250") && v.matches(".*?<(.*?@.*?)>.*")) continue;

		sbd.append(v+"\n");
	}

		
		listing = sbd.toString().trim();

System.out.println(listing);
try{
		String out1 = (new NetsManager.Query(listing, query, null, false)).qtabby.toString(); 
		out1 = "<mail>\n"+out1+"\n</mail>";
		out = (new NetsManager.Traxit(out1.getBytes(),"ServPak/xsl/readSentMail.xsl",null)).tabby;

}catch(Exception ee){
			printout = "Check your database for well-formedness.";
		    }

		printout = new String(out);
	} else {
		ServPak.jv.MySQL data = new ServPak.jv.MySQL("basename=ZEFMdb&tablename=sentMail");	
		String listing = data.printout;	
		listing = listing.replaceAll("MySQL","SentMail");
		listing = listing.replaceAll("<(\\w*?@.*?)>","&lt;$1&gt;");

try{
			FileOutputStream fout = new FileOutputStream("/tmp/maillisting.txt");
			fout.write(listing.getBytes());
			fout.flush();
			fout.close();


		printout = (new NetsManager.Query(listing, "ServPak/xql/sentmail.xql", null, true)).qtabby.toString(); 
}catch(Exception eio){ 
			printout = "Check your database for well-formedness.";
		     }
	}

     }

}
