package Plugins;

import NetsManager.*;
import java.util.Date;
import java.io.*;

public class GoSearch{

    public String printout;
	String value;
	String texfilename;

    public GoSearch(String cmd) throws Exception{


	 value = "search";
	 texfilename = cmd;

        if (cmd.indexOf("?") > 0) {

                  value = cmd.substring(cmd.lastIndexOf("?") + 1);
                  texfilename  = cmd.substring(0, cmd.lastIndexOf("?"));
        } else {

	FileInputStream fins = new FileInputStream(cmd);
	byte[] data = new byte[fins.available()];
	fins.read(data);
	printout = new String(data);
	return;
	}
try{
            Searcher sally = new Searcher(texfilename, value);

            if (sally.searchResults != null) {
                printout = new String(sally.searchResults);
            } else {
                printout = "No matches found.";
            }

        }catch(Exception ex) {
	printout = new Date().toString();
        }
    }
}