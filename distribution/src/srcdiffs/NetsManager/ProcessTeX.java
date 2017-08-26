package NetsManager;

import java.io.*;

import java.util.zip.*;


public class ProcessTeX {
    //Class
    InputStream out;
    Process proc;
    String name;
    String basename;
    boolean latex;

    public ProcessTeX(String texfile) throws Exception {
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
        FileOutputStream fout = new FileOutputStream(name);

        byte[] filedata = new byte[flin.available()];
        flin.read(filedata);
        fout.write(filedata);
        fout.flush();
        fout.close();

        flin.close();

        String[] erasem = { ".log", ".aux", ".pdf", ".dvi", ".toc" };

        for (int i = 0; i < erasem.length; i++) {
            String filestogo = dirname + "/" + intername + erasem[i];
            new File(filestogo).delete();
        }

        this.out = new FileInputStream(name);
    }
}
