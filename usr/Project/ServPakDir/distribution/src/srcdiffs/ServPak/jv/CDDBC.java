package ServPak.jv;
	import java.net.*;
	import java.io.*;
	import java.util.*;
	import NetsManager.Traxit;

	public class CDDBC {

     private static  Splitz Loginfo;
     private static  Splitz PortInfo;
     private static  Splitz User;

	static String prehost;
	static String category;
	static String diskid;

	static String prexmlout;
	static String xmlout;

	static PrintWriter xout;
	static PrintWriter fout;
	static PrintWriter pout;

	static BufferedReader bin;

	public String printout;

 public  CDDBC(String textin) 
    {
   	if(textin.length()==0) {
		System.out.println("Usage: CDDBClient user@localhostname");
		System.exit(0);
	}

              User = new Splitz(textin,"@=");

		    prehost = "x";

	     String pwd=User.Id[1]+" "+User.Id[2];
	     System.out.println(pwd);

     try{
	
	Runtime ronny = Runtime.getRuntime();
	Process getInfo = ronny.exec("discid");

	BufferedReader buf = new BufferedReader(new InputStreamReader(getInfo.getInputStream()));

	String inputLine = buf.readLine();

	String fileout = inputLine.substring(0,inputLine.indexOf(" "))+".results";

		String host;
		int port;
		int cut = prehost.indexOf(":");
		if(cut<0){
				host = "freedb.org";
				port = 8880;
		}else{
				host = prehost.substring(0,cut);
				 port = Integer.parseInt(prehost.substring(cut+1));
		}
    Socket server = new Socket(host,port); 
    InputStream in = server.getInputStream(); 
    	         bin = new BufferedReader( new InputStreamReader( in ));
                            pout = new PrintWriter( server.getOutputStream(), true ); 
    
      server.setSoTimeout(3000);

                             fout = new PrintWriter(new FileWriter(fileout),true); 

     pout.println("cddb hello "+pwd+" CDDBChek 1.0"); 

    fout.println(GetResponse(bin).text);
    fout.println(GetResponse(bin).text);

    pout.println("cddb query "+inputLine);

	Loginfo = GetResponse(bin);
if( Loginfo.Id[0].equals("200")){
		category = Loginfo.Id[1];
		diskid = Loginfo.Id[2];
	} else {

		System.out.println("Error: "+Loginfo.text);
		System.exit(0);
	}


       pout.println("cddb read "+category+" "+diskid);

    while (true){
		  Loginfo = GetResponse(bin);
		
		if( Loginfo.Id[0].equals(".")   )  break;

		String line = Loginfo.text;
		       fout.println(line);

	if(line.startsWith("DTITLE")) {		
		        prexmlout = crunch(line.substring(line.indexOf("=")+1));
		        xmlout = prexmlout+".xml";

	              xout = new PrintWriter(new FileWriter(xmlout),true); 

		xout.println("<?xml version=\"1.0\"?>");
		xout.println("<?xml-stylesheet type=\"text/xsl\" href=\"ServPak/xsl/cddb.xsl\"?>");
		xout.println("<base>");
		xout.println("<ol>");
	}	
		if(line.startsWith("TTITLE"))  
			xout.println("<li>"+crunch(line.substring(line.indexOf("=")+1))+"</li>");
   	  }

	     pout.println("quit");

	     fout.println(GetResponse(bin).text);

		 server.close(); 

		xout.println("</ol>");
		xout.println("</base>");

		pout.close();
		fout.close();	
		xout.close();

		new Traxit(xmlout,"ServPak/xsl/cddb.xsl");

		FileOutputStream ffout = new FileOutputStream(prexmlout+".properties");
		ffout.write(Traxit.tabby);
		ffout.flush();	
		ffout.close();

NetsManager.ReadProperties   rprops = new NetsManager.ReadProperties(prexmlout+".properties");

		new NetsManager.Traxit(rprops.out,"ServPak/xsl/generic.xsl",null);

		printout = new String(Traxit.tabby);		

	} 	 
		catch (Exception e ) { 
		System.out.println(e);
	} 

		
      }

    /// Get Reply Method

    static Splitz GetResponse(BufferedReader bn) throws IOException{
    String reply = bn.readLine();
    System.out.println(reply);
    Splitz rply = new Splitz(reply);
    return rply;
}

    /// Put Method

    public static void PutInfo(String filename,DataOutputStream pwrite) 
throws IOException{
    
    FileInputStream fl = new FileInputStream(filename);

    try {
    byte [] data = new byte[fl.available()];
		fl.read(data);
		pwrite.write(data);
		pwrite.flush();
    } catch (Exception e){} // end PutInfo

    }



	/// Line Splitter 

   static class Splitz {

    String text, token;
    StringTokenizer tok;
    String [] Id;
    int NumTokens;

   Splitz(String Text, String Toke) {

	text = Text; token = Toke;

         tok = new StringTokenizer( Text, Toke); 
 
         NumTokens  = tok.countTokens();

         Id  = new String[NumTokens];

for (int i=0;i<NumTokens;i++) {
Id[i] = tok.nextToken();   
}

    } 

	////////// SPLITZ ONEARG ///////////


Splitz(String Text) {
	this(Text," ");

    }


	///////////// DROP PAREN ////////////////

    void DropParen() {

		int m=NumTokens-1;

	Id[m]=Id[m].substring(0,Id[m].indexOf(')'));
			       return;
    }        // DropParen


   } 


	/////////////////// CRUNCH //////////////////

	public static String crunch(String in) {

	char[] z = in.toCharArray();
	String y = "";

	for(int q=0;q<z.length;q++){
	              if(!Character.isLetterOrDigit(z[q])) z[q] = '_';
		y += String.valueOf(z[q]);
	}
		return y;
  	   }

     }
