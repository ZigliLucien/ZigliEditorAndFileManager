package Plugins;

import java.io.*;
import java.util.zip.*;


public class GoTeX {
    //Class
    public String printout;
    Process proc;
    String name;
    String basename;
    boolean latex;

    public GoTeX(String texfile) throws Exception {
        //Constructor
        String dirname = System.getProperty("user.dir");

        BufferedReader fin = new BufferedReader(new FileReader(texfile));

        int count = 0;
        latex = false;

        for (String v; (v = fin.readLine()) != null;) {
            if (v.indexOf("documentclass") > 0) {
                latex = true;
            }

            count++;

            if (count > 3) {
                break;
            }
        }

        basename = texfile.substring(0, texfile.indexOf(".tex"));

        String intername = basename.substring(basename.lastIndexOf("/") + 1);

        name = basename + ".pdf";

        Runtime local = Runtime.getRuntime();

        if (latex) {
            Process out1 = local.exec("latex -interaction=nonstopmode " + texfile);
            out1.waitFor();

            System.out.println("LaTeX file");

            proc = local.exec("pdflatex -interaction=nonstopmode " + texfile);
            proc.waitFor();
        } else {
            System.out.println("TeX file");

            proc = local.exec("pdftex -interaction=nonstopmode " + texfile);
            proc.waitFor();
        }

        String outname = dirname + "/" + intername + ".pdf";
        FileInputStream flin = new FileInputStream(outname);
        byte[] data = new byte[flin.available()];
        flin.read(data);
 
        FileOutputStream fout = new FileOutputStream(name);
	fout.write(data);
	fout.flush();
	fout.close();	

        String[] erasem = { ".log", ".aux", ".pdf", ".dvi", ".toc" };

        for (int i = 0; i < erasem.length; i++) {
            String filestogo = dirname + "/" + intername + erasem[i];
            new File(filestogo).delete();
        }

	System.out.println("Reading PDF file: "+data.length+" bytes.");

		NetsManager.ZConnection.out.write(data);
                	NetsManager.ZConnection.out.flush();

            printout = "";
    }
}
