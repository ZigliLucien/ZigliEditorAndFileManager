package ZEdit;

import java.awt.*;

import java.io.*;

import java.util.*;


public class Clsv {
    public String xmltext;
    String document;
    String entryname;

    String[] data;
    String[] elts;

    StringBuilder buffy = new StringBuilder(
            "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/plain\" href=\"ServPak/xsl/generic.xsl\"?>");
    int numtokens;
    boolean fileinput = false;

    public Clsv(String input) throws Exception {
        this(input, null);
    }

    public Clsv(String input, String outfile) throws Exception {
        BufferedReader src;

        if (outfile == null) {
            fileinput = true;
        }

        if (!fileinput) {
            src = new BufferedReader(new StringReader(input));
        } else {
            src = new BufferedReader(new InputStreamReader(
                        new FileInputStream(input), "UTF-8"));
        }

        xmltext = "";

        boolean doc = true;
        boolean fields = true;

        try {
            for (String v; (v = src.readLine()) != null;) {
                // read in    
                if ((v.length() == 0) || v.startsWith("#")) {
                    continue;
                }

                if (doc) {
                    v = v.replace(' ', '_');

                    document = v.substring(v.indexOf(":") + 1);
                    buffy.append("\n\n<" + document + ">\n");
                    doc = false;

                    continue;
                }

                if (fields) {
                    v = ZEditor.crunch(v);
                    data = v.split(":");

                    for (String w : data) {
                        if (Character.isDigit(w.charAt(0))) {
                            	w = "_" + w;
                        }
                    }

                    entryname = data[data.length - 1];
                    fields = false;

                    continue;
                }

                elts = v.split(":");
                buffy.append("\n<" + entryname + ">\n");

                for (int q = 0; q < (data.length - 1); q++) {
	      buffy.append("<" + data[q] + ">" + elts[q] + "</" + data[q] + ">\n");
                }

                buffy.append("</" + entryname + ">\n");
            }

            buffy.append("\n</" + document + ">");

            xmltext = buffy.toString();

            if (!fileinput) {
                FileOutputStream fo = new FileOutputStream(outfile);
                fo.write(xmltext.getBytes("UTF-8"));
                fo.flush();
                fo.close();
            }
        } catch (Exception e) {
            e.getMessage();
        }
    }
}
