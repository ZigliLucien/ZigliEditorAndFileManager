/* Webgrep - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

import NetsManager.ZEFMServer;
import NetsManager.ZConnection;

import java.io.*;
import java.util.Arrays;
import java.util.HashMap;


public class Webgrep {
     BufferedReader bufferedreader;
     StringBuilder stringbuffer;
    static HashMap <File,String> hashmap;
    public String printout;
    public File[] dockeys;

    public Webgrep(String string) throws Exception {
        hashmap = new HashMap<File,String>();

        String string_0_ = string;

        System.out.println("WebGrep " + string);

        int i = string_0_.indexOf("&");
        String string_1_ = string_0_.substring(0, i);
        String string_2_ = string_0_.substring(i + 1);
        String query = string_1_.substring(string_1_.indexOf("=") + 1);
        String string_4_ = string_2_.substring(0, string_2_.indexOf("="));
         String which = string_2_.substring(string_2_.indexOf("=")+1);	

        query = query.replace('+', ' ');
        query = DBM.converter(query);

        int i_5_ = (int) ((2.0 * Math.random()) + 0.5);
        String[] strings = {
            "Have a nice day.", "Please try new keywords.", "What to try next?"
        };
        String string_6_ = DBM.converter(string_4_);
        File file = new File(string_6_);

        if (!file.isDirectory()) {
            Exception exception = new Exception(
                    "Directory not found. Check the path.");

            printout = exception.getMessage();
        } else {
            String[] filelist = file.list();

            for (int q = 0; q < filelist.length; q++) {
                File filename = new File(string_6_ + "/" + filelist[q]);

                if (!filename.isDirectory()) {
                    if (!filename.canRead()) {
                        Exception exception = new Exception(
                                "Files not available.");

                        printout = exception.getMessage();

                        continue;
                    }

                    String filenomen = filelist[q];

                    if (filenomen.indexOf(query) >= 0) {
                        if (!hashmap.containsKey(filename)) {
                            hashmap.put(filename,
                                ("<font>" + filenomen + "</font> <br>"));
                        } else {
                            hashmap.put(filename,
                                (hashmap.get(filename) + "<font>" + filenomen +
                                "</font> <br>"));
                        }
                    }

	if (which.equals("FindFile") ) continue;

                    bufferedreader = new BufferedReader(new FileReader(filename));

                    Object object = null;
                    String v;

                    while ((v = bufferedreader.readLine()) != null) {
                        if (v.indexOf(query) > -1) {
                            int locq = v.indexOf(query);

                            v = (v.substring(0, locq) + "<em>" + query +
                                "</em>" + v.substring(locq + query.length()));

                            if (!hashmap.containsKey(filename)) {
                                hashmap.put(filename,
                                    ("<font>" + v + "</font> <br>"));
                            } else {
                                hashmap.put(filename,
                                    (hashmap.get(filename) + "<font>" + v +
                                    "</font> <br>"));
                            }
                        }
                    }
                }
            }

	dockeys = new File[hashmap.keySet().size()];

            hashmap.keySet().toArray(dockeys);
            Arrays.sort(dockeys);

            int lgth = dockeys.length;

            stringbuffer = new StringBuilder(2049);
            stringbuffer.append("<html>\n");
            stringbuffer.append("<head>\n<style> span.a{font-size: 80%}</style>\n");
            stringbuffer.append("<title> Search Results on " + query +
                " </title>\n");
            stringbuffer.append("</head>\n");
            stringbuffer.append("<body bgcolor=ffffff>\n");
            stringbuffer.append("<center><h1><b> Results </b></h1></center>\n");
            stringbuffer.append("<p>\n");
            stringbuffer.append("Found " + lgth + " files containing <tt>" +
                query + "</tt>.<p>\n");

            if (lgth == 0) {
                stringbuffer.append(strings[i_5_]);
            } else {
                for (int qq = 0; qq < lgth; qq++) {
                    String datum = dockeys[qq].toString();

                    stringbuffer.append("<hr></a>\n");
                    stringbuffer.append("In <b>" + datum +
                        "</b>&nbsp;&nbsp;");
                    datum = ZEFMServer.hexi(datum);
	        stringbuffer.append("<span class=\"a\">\n");
                    stringbuffer.append("<a href=" + datum +
                        "> <i>See</i> |</a>\n");

                    stringbuffer.append("<a href=VVV?" + datum +
                        "> <tt>View</tt> |</a>\n");
                    stringbuffer.append("<a href=CCC?" + datum +
                        "> <tt>Copy</tt> |</a>\n");
                    stringbuffer.append("<a href=MMM?" + datum +
                        "> <tt>Move</tt> |</a>\n");
                    stringbuffer.append("<a href=XXX?" + datum +
                        "> <tt>Delete</tt> |</a>\n");
                    stringbuffer.append("<a href=EEE?" + datum +
                        "> <tt>Edit</tt> |</a>\n");
                    stringbuffer.append("<a href=QQQ?" + datum +
                        "> <tt>QuickEdit</tt> |</a>\n");
                    stringbuffer.append("<a href=AAA?" + datum +
                        "> <tt>Notes</tt>  </a>\n");
	        stringbuffer.append("</span>\n");
                    stringbuffer.append("<p>\n");
                    stringbuffer.append(hashmap.get(dockeys[qq]) + "\n");
                }

                stringbuffer.append("</font>\n");
            }

            stringbuffer.append("<hr>\n");
            stringbuffer.append("</body>\n");
            stringbuffer.append("</html>\n");
	String where = System.getProperty("user.dir");
	PrintWriter pout = new PrintWriter(new FileWriter(where+"/SearchResults.html"),true);
	pout.print(stringbuffer.toString());
	pout.close();
	
	if(lgth>5) {

            printout =

"<html><head><meta http-equiv=\"refresh\" content=\"url=0;"+where+"/SearchResults.html\"> </head>\n"
+"<body><p/>&nbsp;<p/><p/>&nbsp;<p/><center><h2>--&gt;&gt; <a href=\""
+where+"/SearchResults.html\">Get Results </a>&lt;&lt;--</h2></center></body></html>" ;

		     } else {
				printout = stringbuffer.toString();
			    
			   }
        }
    }
}