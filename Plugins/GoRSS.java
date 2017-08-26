package Plugins;

import java.io.*;

public class GoRSS {

  public String printout;

    public GoRSS(String cmd) {
	    try{
/*
		FileInputStream fins = new FileInputStream(cmd);
		byte[] data = new byte[fins.available()];
		fins.read(data);

		printout = new String(data, "UTF-8");
*/
		printout = cmd;
  
	    }catch(Exception ex){
		    	ex.printStackTrace();
		}
        }
    }
