package Plugins;

import NetsManager.*;

public class GoMail{

	public String printout;

    public GoMail(String cmd) throws Exception{

            int cut = cmd.lastIndexOf("/");
            String direc = cmd.substring(0, cut);

            String user = direc.substring(direc.lastIndexOf("/") + 1);

            XmlMail readmail = new XmlMail(cmd, user);

            printout = readmail.viewmail;

     }

}
