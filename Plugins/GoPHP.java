package Plugins;


public class GoPHP{

	public String printout;
	String runfile;
	String val;
	String filename;
 
    public GoPHP(String cmd) {

if(cmd.contains("?")){
	              val = cmd.substring(cmd.lastIndexOf("?") + 1);
	             String subcmd = cmd.substring(0, cmd.lastIndexOf("?"));
	              filename = subcmd.substring(subcmd.lastIndexOf("/") + 1);  
	} else {
		val = "";
		filename = cmd.substring(cmd.lastIndexOf("/") + 1);  
	}

	if(val.length()>0) {

	runfile = "php ServPak/php/" + filename+" "+val;
        } else {
	            	 runfile = "php ServPak/php/" + filename;
        }

        NetsManager.Commands.runIt(runfile);
	printout = NetsManager.Commands.result;
    }
}