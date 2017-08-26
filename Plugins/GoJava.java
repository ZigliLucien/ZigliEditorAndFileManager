package Plugins;

import java.io.*;
import java.lang.reflect.*;
import java.util.*;



public class GoJava {

	public String printout;

    public GoJava(String cmd) throws Exception{
 
             // File Extension Apps

         String value = cmd.substring(cmd.lastIndexOf("?") + 1);
         String subcmd = cmd.substring(0,cmd.lastIndexOf("?")); 
         String filename = subcmd.substring(subcmd.lastIndexOf("/") + 1); 
         String clas = filename.substring(0, filename.indexOf("."));
         String classname = "ServPak.jv." + clas;
System.out.println("IN FILE FOR "+classname+" AND "+value);
            Class cappi = Class.forName(classname);

           Object obie = cappi.getConstructor(new Class[] { String.class })
                                         .newInstance(new String[] { value });

            printout = (String) cappi.getField("printout").get(obie);
    }
}
