package Plugins;

import NetsManager.*;
import java.io.*;

public class GoMime{

	public String printout;

    public GoMime(String rfile) throws Exception {

            String outfile = rfile.substring(0, rfile.indexOf(".mime"));

            new ZEdit.UnPackEm(rfile, outfile);

	if(new File(outfile).exists() && new File(outfile).length()>0) {
		if(new File(rfile).delete())System.out.println(rfile+" deleted");
	}

            String ext = outfile.substring(outfile.lastIndexOf(".") + 1)
                                .toLowerCase();

	String locdir = outfile.substring(0,outfile.lastIndexOf("/"));

	String url = "http://"+ZEFMServer.localhost+":"+ZEFMServer.port;
/*
         String msgout = 
	"<html>\n<head>"
	+"<script> function go(){window.location=\""+url+locdir+"?update\";}</script>"
	+"</head>"
	+"<body onload=\"go()\">\n<p>&nbsp;<p>&nbsp;<p>&nbsp;"
	+ "<a  href=\""+url+locdir+"?update\">DONE</a></body></html>";
*/

      String msgout = 
	"<html>\n<head>"
	+"<script> function go(){"
	+"window.location.replace(\""+url+outfile+"\");"
	+"}</script></head>"
	+"<body onload=\"go()\">\n<p>&nbsp;<p>&nbsp;<p>&nbsp;&nbsp;&nbsp;"
	+ "<a href=\""+url+locdir+"?update\"> Back </a>\n</body></html>";

            if (ext.equals("jpg") || ext.equals("jpeg") || ext.equals("png") || ext.equals("gif")) {
               msgout = "<html>\n<head>"
	+"<script> function go(){window.location=\""+url+outfile+"\";}</script>"
	+"</head>"
	+"<body onload=\"go()\">"
	+"\n<p>&nbsp;<p>&nbsp;<p>&nbsp;"
	+"<a  href=\""+url+outfile + "\">See Picture</a>\n</body></html>";
            }
	            printout = msgout;
    }
}
