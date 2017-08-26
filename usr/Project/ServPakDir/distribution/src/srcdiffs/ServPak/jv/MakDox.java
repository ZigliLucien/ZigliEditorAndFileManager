package ServPak.jv;

import NetsManager.Traxit;
import NetsManager.ZEFMServer;

import java.io.*;

import java.util.*;


public class MakDox {
    static FileOutputStream ff;
    public String printout;
    String filename;
    StringBuilder bufi;

    public MakDox(String in) {
        boolean isMethod = false;

        try {
            if (!new File("DOX/Commented").exists()) {
                new File("DOX/Commented").mkdirs();
                System.out.println("Making DOX directory. Symlink and rerun.");
                printout = "Symlink or copy source files to the DOX directory for commenting.<p>\n";
                printout += "Commented files will be in the Commented subdirectory.";

                return;
            }


	 if (!new File("DOX/UnCommCopy").exists()) 
               	 new File("DOX/UnCommCopy").mkdirs();

            HashMap<String,String> hari = DBgo.parseQuery(in);
            String[] keys = new String[hari.keySet().size()];
	hari.keySet().toArray(keys);

            String quality = "";
            String name = "";
            String key = "";
            String classname = "";
            String temp = "";

            printout = "";

            bufi = new StringBuilder("<?xml version=\"1.0\"?>\n<jdox>\n");

            for (int q = 0; q < keys.length; q++) {
                temp = (hari.get(keys[q]) != null)
                    ? clear(hari.get(keys[q])) : "";
                key = clear(keys[q]);

                if (key.indexOf("!") < 0) {
                    continue;
                }

                quality = key.substring(0, key.indexOf("!"));
                name = key.substring(key.indexOf("!") + 1);

                if (quality.equals("class")) {
                    hari.put("class", temp);
                    classname = name;

                    continue;
                }

                bufi.append("\n<" + quality + ">\n");
                bufi.append("<name>" + name + "</name>\n");
                bufi.append("<comment>" + temp + "</comment>");
                bufi.append("\n</" + quality + ">\n");
            }

            bufi.append("\n<class>\n");

            temp = (hari.get("class") != null)
                ? clear(hari.get("class")) : "";
            bufi.append("\n<comment>" + temp + "</comment>");

            temp = (hari.get("author") != null)
                ? clear(hari.get("author")) : "";
            bufi.append("\n<author>" + temp + "</author>");

            temp = (hari.get("version") != null)
                ? clear(hari.get("version")) : "";
            bufi.append("\n<version>" + temp + "</version>");

            bufi.append("\n</class>\n");

            bufi.append("\n</jdox>");

            ff = new FileOutputStream(ZEFMServer.userdir +
                    "/DOX/UnCommented/cmnt.xml");
            ff.write(bufi.toString().getBytes());
            ff.flush();
            ff.close();

            String filenameXml = ZEFMServer.userdir + "/DOX/UnCommented/" +
                classname + ".xml";

            String filenameXmlCopy = ZEFMServer.userdir + "/DOX/UnCommCopy/" +
                classname + ".xml";

            String dirstring;

            if (classname.indexOf(".") > 0) {
                dirstring = classname.substring(0, classname.lastIndexOf("."));

                if (!new File("DOX/Commented/" + dirstring.replace('.', '/')).exists()) {
                    new File("DOX/Commented/" + dirstring.replace('.', '/')).mkdirs();
                }
            }

            String filenameCom = ZEFMServer.userdir + "/DOX/Commented/" +
                classname.replace('.', '/') + ".java";

            new Traxit(filenameXml, "ServPak/xsl/merge.xsl",
                ZEFMServer.userdir + "/DOX/UnCommented/cmnt.xml");

            ff = new FileOutputStream(filenameXml);
            ff.write(Traxit.tabby);
            ff.flush();
            ff.close();

            ff = new FileOutputStream(filenameXmlCopy);
            ff.write(Traxit.tabby);
            ff.flush();
            ff.close();

            new Traxit(Traxit.tabby, "ServPak/xsl/javaskel.xsl", null);

            ff = new FileOutputStream(filenameCom);
            ff.write(Traxit.tabby);
            ff.flush();
            ff.close();

            printout = "<html><body><h2>" + classname + "</h2>";

            printout += ("<pre>\n" + new String(Traxit.tabby) + "\n</pre>");
        } catch (Exception e) {
            System.out.println(e.getMessage());
            printout = "Error";
        }
    }

    static String clear(String in) {
        if (in != null) {
            return in.replace('+', ' ');
        }

        return "";
    }
}
