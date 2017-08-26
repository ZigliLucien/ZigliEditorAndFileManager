package Plugins;

public class GoJavaX {
	
	public String printout;

      public GoJavaX(String cmd) throws Exception{
   
	String header = 
		"<html><head><title>"+cmd+"</title></head>\n\n<body>\n<h2>"+cmd+"</h2>\n";
	String footer = "\n\n</body>\n</html>";

		 printout = header + new J2html.Java2Html(cmd).result + footer;
	}
     }