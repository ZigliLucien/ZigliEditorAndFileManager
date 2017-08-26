package Plugins;
import NetsManager.*;


public class GoClsv {

	public String printout;
 	           String filename;
 
    public GoClsv(String cmd) throws Exception{
  
System.out.println("FOR "+cmd);

             ZEdit.Clsv claudia = new ZEdit.Clsv(cmd);

            new Query(claudia.xmltext, "ServPak/xql/generic.xql", null, true);
            printout = Query.qtabby.toString();
     }
}