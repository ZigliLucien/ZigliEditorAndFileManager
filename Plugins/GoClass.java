package Plugins;

import ServPak.jv.ReadClass;


public class GoClass {

  public String printout;

    public GoClass(String _cmd) {
	    try{
        ReadClass rclass;

            rclass = new ReadClass(_cmd);

            printout = rclass.printout;
	    }catch(Exception ex){
		    	ex.printStackTrace();
			printout = _cmd+" not found.";
		}
        }
    }
