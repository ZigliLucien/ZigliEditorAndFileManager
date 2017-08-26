package Plugins;


public class GoPerl{

	public String printout;
	String runfile;
	String val;
	String filename;
 
    public GoPerl(String cmd) {

if(cmd.contains("?")){
	              val = cmd.substring(cmd.lastIndexOf("?") + 1);
	             String subcmd = cmd.substring(0, cmd.lastIndexOf("?"));
	              filename = subcmd.substring(subcmd.lastIndexOf("/") + 1);  
	} else {
		val = "";
		filename = cmd.substring(cmd.lastIndexOf("/") + 1);  
	}

	if(val.length()>0) {

	runfile = "perl ServPak/pl/" + filename+" "+val;
        } else {
	            	 runfile = "perl ServPak/pl/" + filename;
        }

        NetsManager.Commands.runIt(runfile);
	printout = NetsManager.Commands.result;
    }
}