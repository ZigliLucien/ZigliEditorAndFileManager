package Plugins;

import NetsManager.ZEFMServer;

public class GoEPerl {

	public String printout;
	String runfile;
	String val;
	String filename;
 
    public GoEPerl(String cmd) {

if(cmd.contains("?")){
	              val = cmd.substring(cmd.lastIndexOf("?") + 1);
	             String subcmd = cmd.substring(0, cmd.lastIndexOf("?"));
	              filename = subcmd.substring(subcmd.lastIndexOf("/") + 1);  
	} else {
		val = "";
		filename = cmd.substring(cmd.lastIndexOf("/") + 1);  
	}

	if(val.length()>0) {

	runfile = "ServPak/nph-eperl -D QUERYSTRING=" + val + " " +"ServPak/pl/" + filename;
        } else {
	            	 runfile = "ServPak/nph-eperl ServPak/pl/" + filename;
        }

        NetsManager.Commands.runIt(runfile);
	printout = NetsManager.Commands.result;
    }
 }