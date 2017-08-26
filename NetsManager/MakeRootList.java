package NetsManager;

import java.io.*;

import java.util.*;


public class MakeRootList {
    //Class
    public MakeRootList(){
        try {
            // RootLister
            Stack <String>stacy = new Stack<String>();

            File dirr = new File("/");

            String[] listdir = dirr.list();

            for (int q = 0; q < listdir.length; q++) {
                String w = listdir[q];

                if (w.startsWith(".")) {
                    continue;
                }

                File testit = new File("/" + w);

                if (testit.isDirectory()) {
                    stacy.push(w);
                }
            }

          StringBuilder buffy = 
  new StringBuilder("<html><head><style>td{background-color: #DDDDFF}</style></head><body>\n");

            String[] dirlist = new String[stacy.size()];
	stacy.toArray(dirlist);

            Arrays.sort(dirlist);

            int numrows = (int) Math.round(dirlist.length / 4);
            int tail = dirlist.length % 4;

            buffy.append(
                "<table align=center style=\"background-color: yellow\">\n");
            buffy.append("<caption><b>DIRECTORIES</b></caption><tr></tr>\n");

            int cc = 0;

            if (numrows > 0) {
                for (int q = 1; q <= numrows; q++) {
                    buffy.append("<tr>\n");

                    for (int q0 = 1; q0 < 5; q0++) {
                        String dtemp = dirlist[cc];

		String dirltemp = dtemp.replaceAll("\\s+","%20");

                        buffy.append("<td><a href=/" + dirltemp + ">" + dirlist[cc] + "</a></td>\n");

                        cc++;
                    }

                    buffy.append("</tr>\n");
                }
            }

            if (tail > 0) {
                buffy.append("<tr>\n");

                for (int q = 1; q <= tail; q++) {
                    String dtemp = dirlist[cc];

                    String dirltemp = dtemp.replaceAll("\\s+","%20");

                    buffy.append("<td><a href=/" + dirltemp + ">" + dirlist[cc] + "</a></td>\n");
                    cc++;
                }

                buffy.append("</tr>\n");
            }

            buffy.append("</table><p>\n</body></html>");

            PrintWriter outpt = new PrintWriter(new FileWriter("/topLevel.html"), true);
            outpt.print(buffy.toString());
            outpt.close();

            System.out.println("Top Level Directories Listed");
        } catch (Exception eee) {
            System.out.println(eee.getMessage());

            return;
        }
    }

	public static void main(String[] qubits) {
		
		new MakeRootList();

	}
}
