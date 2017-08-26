package Plugins;

import NetsManager.ZEFMServer;

public class GoDot{
	public String printout;
	String runfile;
	String val;
	String filename;
 
    public GoDot(String cmd) {

		String fileout = ZEFMServer.userdir+"/dottmp.gif";
		
		runfile = "/usr/local/bin/dot -Tgif -o "+fileout+" "+cmd;
        

              NetsManager.Commands.runIt(runfile);
	printout = "<html><body><img src="+fileout+"/></body></html>";

       }

}