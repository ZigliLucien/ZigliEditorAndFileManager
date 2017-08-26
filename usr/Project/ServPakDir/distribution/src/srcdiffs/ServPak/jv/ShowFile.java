package ServPak.jv;

import java.io.*;
import java.text.*;
import java.util.*;

public class ShowFile{

	public String printout;

   	static  final  SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yy");
   	static  final  SimpleDateFormat stf = new SimpleDateFormat("hh:mm:ss");

	Date d = new Date();

	public ShowFile(String input) throws Exception {

	File current = new File(input);

	StringBuilder bufy = new StringBuilder("<html><head><title>"+input+"</title></head>");
 
            bufy.append("<body>size: " + String.valueOf(current.length()));
            bufy.append("<br/> last modified at "+ stf.format(d) +"<br/> on "+ sdf.format(d));
	bufy.append("</body></html>");
 
		printout = bufy.toString();
	}
     }