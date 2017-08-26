package NetsManager;

import java.io.*;
import java.lang.reflect.*;
import java.util.*;

public class Commands {

    public static String directory;
    static String cmd;

    public static String result;
    Properties fileinfo = ZConnection.fileinfo;

    public Commands(String _cmd) { 

		        cmd = _cmd;
		        result = null;
		        parseCmd();
    }

     void parseCmd() {
        // parse the request
        String apprun = "";

        if (cmd.indexOf("?") > 0) {
            // IF ENV QUERY
	
		String subcmd = cmd.substring(0,cmd.lastIndexOf("?"));
			
            for (Enumeration enume = fileinfo.propertyNames();
                    enume.hasMoreElements();) {
                String key = (String) enume.nextElement();

                if (subcmd.substring(subcmd.lastIndexOf(".") + 1).equals(key)) {
                    apprun = fileinfo.getProperty(key);
                }
            }
        } else {
            // File Extension Apps
            for (Enumeration enume = fileinfo.propertyNames();
                    enume.hasMoreElements();) {
                String key = (String) enume.nextElement();

                if (cmd.endsWith("." + key)) {
                    apprun = fileinfo.getProperty(key);
                }
            }
        }

	if(apprun.equals("")) return;

        String classname = "Plugins.Go" +apprun;	
	this.result = "";

try{
	            Class cappi = Class.forName(classname);

System.out.println("DOING "+cmd+ " VIA "+classname);	

	           Object obie = cappi.getConstructor(new Class[] { String.class })
	                                         .newInstance(new String[] { cmd });

	            result = (String) cappi.getField("printout").get(obie);
	        }catch(Exception ex) {
	            result = apprun+" NOT FOUND";
	        }
    }

    //////////////////////////////////////////////////////////////////////////////////////
    //////////////////////////// DEFAULT METHOD //////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////
    public static void goJJ() {
        try {
            if ((ZEFMServer.DocRoot != null) && (cmd.indexOf("?") > 0)) {
                ServPak.jv.Test tooti = new ServPak.jv.Test("");
                result = tooti.printout;
            }

            return;
        } catch (Exception e) {
            System.out.println(e.getMessage());

            return;
        }
    }

    ////////////////////////////////////////////////////////////////////////////////
    //////////////////////////////// RUNIT ////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////
    public static void runIt(String shellcommand) {

System.out.println("IN RUNIT FOR "+shellcommand);

        try {

	Runtime local = Runtime.getRuntime();
	Process out = local.exec(shellcommand);

            InputStream infoout = out.getInputStream();
            InputStream errout  = out.getErrorStream();

            ByteArrayOutputStream stdout = new ByteArrayOutputStream();

            ByteArrayOutputStream errorout = new ByteArrayOutputStream();

            for (int qq = 0; (qq = infoout.read()) != -1;) {
                stdout.write(qq);
            }

            for (int qq = 0; (qq = errout.read()) != -1;) {
                errorout.write(qq);
            }

            stdout.flush();

            errorout.flush();

            result = stdout.toString();

            System.out.println(errorout.toString());
        } catch (Exception e) {
            result = e.getMessage();
        }
    }
}
