package ServPak.jv;

import NetsManager.*;

import java.io.*;

import java.util.*;


public class FormEntry {
    static String filename;
    public String printout;
    String[] champs;
    String formatstring;

    public FormEntry(String string) throws Exception {
        if (string.indexOf("formmode") >= 0) {
            string = DBM.converter(string);

            String[] entry = string.split("&");
	int qq = 0;

            for (String x : entry) {
                entry[qq] = x.substring(x.indexOf("=") + 1).replace('+', ' ');
	    qq++;
            }

            StringBuilder bufv = new StringBuilder();

            FileWriter fwrite = new FileWriter(filename, true);
            PrintWriter prt = new PrintWriter(fwrite, true);

            for (int q = 0; q < (entry.length - 1); q++) {
                bufv.append(entry[q] + ":");
            }

            bufv.append(entry[entry.length - 1]);
            prt.println(bufv.toString());
            prt.close();

            printout = bufv.toString();
        } else {
            int cut = string.indexOf("&");
            String filestring = string.substring(0, cut);
            String fmtstring = string.substring(cut + 1);

            filename = filestring.substring(filestring.indexOf("=") + 1);
            formatstring = fmtstring.substring(fmtstring.indexOf("=") + 1);
            champs = getFields(filename);
            printout = formEntry(champs).toString();
        }
    }

    String[] getFields(String filein) {
        System.out.println(filein);

        String[] temp = null;
        String v = "";

        try {
            BufferedReader bufr = new BufferedReader(new FileReader(filein));

            bufr.readLine();
            v = bufr.readLine();

            while (v.indexOf(":") < 0) {
                v = bufr.readLine();
            }

            if (v.indexOf(":") >= 0) {
                System.out.println(v);
                temp = v.split(":");
            }
        } catch (Exception ex) {
        }

        return temp;
    }

    StringBuilder formEntry(String[] fields) throws Exception {
        char[] cari = formatstring.toCharArray();

        StringBuilder stringbuffer = new StringBuilder();

        stringbuffer.append("<html>\n");
        stringbuffer.append("<head><title>" + filename + "</title>\n");
        stringbuffer.append("</head>\n");
        stringbuffer.append("<body bgcolor=#eeeedd>\n");
        stringbuffer.append("<h2> Entry  </h2>");
        stringbuffer.append(
            "<form action=\"FormEntry.jav\" method=\"post\"><table width=\"90%\">");

        for (int q = 0; q < (fields.length - 1); q++) {
            stringbuffer.append("<tr>");
            stringbuffer.append("<th align=right>" + DBgo.dataCheck(champs[q]) +
                "&nbsp;&nbsp;</th>");

            if (cari[q] == 'i') {
                stringbuffer.append("<td><input name=" + champs[q] +
                    " size=20></td></tr>\n");
            } else {
                stringbuffer.append("<td><textarea name=" + champs[q] +
                    " rows=3 cols=60></textarea></td></tr>\n");
            }

            stringbuffer.append("<tr><th><br></th><td><br></td></tr>\n");
        }

        stringbuffer.append(
            "</table><input type=submit value=GO name=formmode></form>");
        stringbuffer.append(
            "<p><b>Note:</b>Please use a -, a dash, for blank entries.\n");
        stringbuffer.append("</body>\n");
        stringbuffer.append("</html>\n");

        return stringbuffer;
    }
}
