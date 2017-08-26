package Plugins;

import NetsManager.ZEFMServer;

public class GoMD{
	public String printout;
	String runfile;
	String val;
	String fileout;
	String header;
 
    public GoMD(String cmd) {

		runfile = "/usr/local/bin/markdown -f latex -f nostyle "+cmd;
	 	NetsManager.Commands.runIt(runfile);
		fileout = NetsManager.Commands.result;

	header = "<script type=\"text/x-mathjax-config\">"
	   + "MathJax.Hub.Config({tex2jax: {inlineMath: [['\\$','\\$'], ['\\\\(','\\\\)']]}}); </script>\n"
	+    "<script src=\"http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML\" type=\"text/javascript\">"
               +"     </script>\n"
	+"<script type='text/javascript' src='/ServPak/js/jquery.js'></script>\n"
	+"<script type='text/javascript' src='/ServPak/js/mathformat.js'></script>\n"
	+"<link rel='stylesheet' type='text/css' href='/ServPak/css/math.css'/>\n"
	+ "</head>";


        		printout = "<html>\n<head>\n"+header+"\n<body>"+fileout+"\n</body></html>";

       }

}