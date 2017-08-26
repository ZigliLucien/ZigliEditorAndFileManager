package ServPak.jv;

import NetsManager.Traxit;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

import java.util.*;


public class DBrcops {
    static String[][] table;
    static String[][] table2;
    static String filenomen;
    static String filename;
    static String infilename;
    static int numcols;
    static int numrows;
    static boolean renew;
     StringBuilder stringbuffer;
     PrintWriter printwriter;
    public String printout;

    public DBrcops(String string) throws Exception {
        renew = false;

        if (string.indexOf("renew") >= 0) {
            renew = true;
            new DBrcops(table2, filename);
            printout = DBgo.getFile("HTML/dbrcops.html");
        } else {
            numrows = table.length;
            numcols = table[0].length;

            try {
                if (string.indexOf("show") > -1) {
                    for (int i = 0; i < numrows; i++) {
                        for (int j = 0; j < numcols; j++) {
                            table2[i][j] = table[i][j];
                        }
                    }
                }

                if (string.indexOf("skeleton") > -1) {
                    String[][] strings = new String[numrows][numcols];

                    for (int i = 1; i < numrows; i++) {
                        for (int j = 1; j < numcols; j++) {
                            strings[i][j] = "-";
                            table2[i][j] = table[i][j];
                        }
                    }

                    strings[0][0] = "_0_" + table[0][0];
                    table2[0][0] = table[0][0];

                    for (int i = 1; i < numcols; i++) {
                        strings[0][i] = "COL-" + String.valueOf(i) + "-" + table[0][i];
                        table2[0][i] = table[0][i];
                    }

                    for (int i = 1; i < numrows; i++) {
                        strings[i][0] = "ROW-" + String.valueOf(i) + "-" + table[i][0];
                        table2[i][0] = table[i][0];
                    }

                    writeMatrix2XML(filename + "_skel", strings);
                    printout = showTable(filename + "_skel");
                } else if (string.indexOf("savetable") > -1) {
                    writeMatrix2XML(infilename, table);
                    printout = showTable(infilename);
                } else {
                    if (string.indexOf("insertrow") > -1) {
		String[] toks = string.split("&");

                        String tokn = toks[1];
                        String toki = tokn.substring(tokn.indexOf("=") + 1);
                        int nmrws = Integer.parseInt(toki);

                        tokn = toks[2];
                        numrows++;
                        table2 = new String[numrows][numcols];

                        for (int i = 0; i < nmrws; i++) {
                            for (int j = 0; j < numcols; j++) {
                                table2[i][j] = table[i][j];
                            }
                        }

                        table2[nmrws][0] = tokn.substring(tokn.indexOf("=") + 1);

                        for (int j = 1; j < numcols; j++) {
                            table2[nmrws][j] = "-";
                        }

                        for (int i = nmrws + 1; i < numrows; i++) {
                            for (int j = 0; j < numcols; j++) {
                                table2[i][j] = table[i - 1][j];
                            }
                        }

                        realign(table2);
                    }

                    if (string.indexOf("rowdel") > -1) {
		String[] toks = string.split("&");

                        String string_30_ = toks[1].substring(toks[1].indexOf("=") + 1);

                        string_30_ = DBM.converter(string_30_);

                        if (string_30_.indexOf(",") < 0) {
                            int i = Integer.parseInt(string_30_.replace('+',' ').trim());

                            numrows--;
                            table2 = new String[numrows][numcols];

                            for (int A = 0; A < i; A++) {
                                for (int B = 0; B < numcols; B++) {
                                    table2[A][B] = table[A][B];
                                }
                            }

                            for (int A = i + 1; A < (numrows + 1); A++) {
                                for (int B = 0; B < numcols; B++) {
                                    table2[A - 1][B] = table[A][B];
                                }
                            }

                        } else {

		    String[] tox35 = string_30_.trim().split(",");
		
                            int i = tox35.length;

                            table2 = new String[numrows - i][numcols];

		    int[] nums = new int[i+1];

		    nums[i] = numrows;

		    int counter = 0;

		    for (String v : tox35) {
				nums[counter] = Integer.parseInt(v.replace('+',' ').trim());
				counter++;
			}

		   Arrays.sort(nums);

		    int r = 0;

                            for (int A = 0; A < numrows; A++) {
                                if ( A == nums[r] ) {
                                    r++;
                                } else {
                                    for (int B = 0; B < numcols; B++) {
                                        table2[A - r][B] = table[A][B];
                                    }
                                }
                            }
                        }
                        realign(table2);
                    }

                    if (string.indexOf("xrows") > -1) {
		        String[] toks = string.split("&");
                        
                        String str1 = toks[1].substring(toks[1].indexOf("=") + 1);
                        int i = Integer.parseInt(str1);

                        str1 = toks[2].substring(toks[2].indexOf("=") + 1);

                        int i1 = Integer.parseInt(str1);

                        exRows(i, i1);
                        realign(table2);
                    }

                    if (string.indexOf("insertcol") > -1) {
                     	        String[] toks = string.split("&");

                        String string_43_ = toks[1].substring(toks[1].indexOf("=") + 1);
                        int i = Integer.parseInt(string_43_);

                        numcols++;
                        table2 = new String[numrows][numcols];

                        for (int A = 0; A < numrows; A++) {
                            for (int B = 0; B < i; B++) {
                                table2[A][B] = table[A][B];
                            }
                        }

                        table2[0][i] = toks[2].substring(toks[2].indexOf("=") + 1);

                        for (int s = 1; s < numrows; s++) {
                            table2[s][i] = "-";
                        }

                        for (int p = 0; p < numrows; p++) {
                            for (int q = i + 1; q < numcols; q++) {
                                table2[p][q] = table[p][q - 1];
                            }
                        }

                        realign(table2);
                    }

                    if (string.indexOf("coldel") > -1) {
	        String[] toks = string.split("&");

                        String string_50_ = toks[1].substring(toks[1].indexOf("=") + 1);

                        string_50_ = DBM.converter(string_50_);

                        if (string_50_.indexOf(",") < 0) {
                            int i = Integer.parseInt(string_50_.replace('+',' ').trim());

                            numcols--;
                            table2 = new String[numrows][numcols];

                            for (int p = 0; p < i; p++) {
                                for (int q = 0; q < numrows; q++) {
                                    table2[q][p] = table[q][p];
                                }
                            }

                            for (int p = i + 1; p < (numcols + 1); p++) {
                                for (int q = 0; q < numrows; q++) {
                                    table2[q][p - 1] = table[q][p];
                                }
                            }
                        } else {

		    String[] tox55 = string_50_.trim().split(",");
		
                            int i = tox55.length;

                            table2 = new String[numrows][numcols - i];

		    int[] nums = new int[i+1];

		    nums[i] = numcols;

		    int counter = 0;

		    for (String v : tox55) {
				nums[counter] = Integer.parseInt(v.replace('+',' ').trim());
				counter++;
			}

		   Arrays.sort(nums);

                            int A = 0;

                            for (int B = 0; B < numcols; B++) {
                                if (B == nums[A] ) {
                                    A++;
                                } else {
                                    for (int C = 0; C < numrows; C++) {
                                        table2[C][B - A] = table[C][B];
                                    }
                                }
                            }
                        }

                        realign(table2);
                    }

                    if (string.indexOf("xcols") > -1) {
	        String[] toks = string.split("&");

                        String i1 = toks[1].substring(toks[1].indexOf("=") + 1);
                        int i = Integer.parseInt(i1);

                        i1 = toks[2].substring(toks[2].indexOf("=") + 1);

                        int c = Integer.parseInt(i1);

                        exCols(i, c);
                        realign(table2);
                    }

                    if (string.indexOf("colimport") > -1) {
	        String[] toks = string.split("&");

                        String string_63_ = toks[1].substring(toks[1].indexOf("=") + 1);

                        string_63_ = DBM.converter(string_63_);

                        String string_64_ = toks[2].substring(toks[2].indexOf("=") + 1);
                        		DBgo.getFields(string_64_);
                        String[][] strings_65_ = DBgo.readXML(string_64_, DBgo.champs.length);

                        strings_65_[0] = DBgo.champs;

                        boolean bool = strings_65_.length < numrows;

                        if (string_63_.indexOf(",") < 0) {
                            int i = Integer.parseInt(string_63_);

                            table2 = new String[numrows][numcols + 1];

                            for (int ii = 0; ii < numrows; ii++) {
                                for (int j = 0; j < numcols; j++) {
                                    table2[ii][j] = table[ii][j];
                                }
                            }

                            for (int A = 0; A < numrows; A++) {
                                if (bool && (A >= strings_65_.length)) {
                                    table2[A][numcols] = "-";
                                } else {
                                    table2[A][numcols] = strings_65_[A][i];
                                }
                            }
                        } else {
                           String[] tokk = string_63_.split(",");

                            table2 = new String[numrows][numcols + tokk.length];

                            for (int A = 0; A < numrows; A++) {
                                for (int B = 0; B < numcols; B++) {
                                    table2[A][B] = table[A][B];
                                }
                            }

                            int[] is = new int[tokk.length];

		for(int q=0; q<tokk.length; q++) is[q] = Integer.parseInt(tokk[q]);

                            for (int Q = 0; Q < tokk.length; Q++) {
                                for (int P = 0; P < numrows; P++) {
                                    table2[P][numcols + Q] = strings_65_[P][is[Q]];
                                }
                            }
                        }

                        realign(table2);
                    }

                    filenomen = filename + "_X";
                    writeMatrix2XML(filenomen, table2);
                    printout = showTable(filenomen);
                }
            } catch (Exception exception) {
                System.out.println(exception.getMessage());
            }
        }
    }

    public DBrcops(String[][] strings, String string) throws Exception {
        if (!new File("DB").exists()) {
            new File("DB").mkdir();
        }

        table = strings;

        if (renew) {
            filename = string;

            if (!filename.startsWith("DB")) {
		filename = "DB/" + string; 
		System.out.println("Correcting RC file location.");
				    }
        } else {
            filename = "DB/" + string;
        }

        infilename = filename;

        if (filename.endsWith("_X")) {
            int i = filename.lastIndexOf("_X");

            infilename = filename.substring(0, i);
        }

        System.out.println("Working with " + infilename);
        table2 = new String[table.length][table[0].length];
    }

     void writeMatrix2XML(String string, String[][] strings)
        throws Exception {
        printwriter = new PrintWriter(new FileWriter(string + ".xml"), true);
        stringbuffer = new StringBuilder();

        String string_0_ = "array";
        String string_1_ = "entry";
        String[] strings_2_ = strings[0];

        stringbuffer.append("<?xml version=\"1.0\"?>\n");
        stringbuffer.append("<" + string_0_ + ">\n");

        for (int i = 1; i < strings.length; i++) {
            String string_3_ = "";
            String[] strings_4_ = strings[i];

            stringbuffer.append("\n<" + string_1_ + ">\n");

            for (int q = 0; q < strings_4_.length; q++) {
                String string_6_ = strings_2_[q].toLowerCase();

                stringbuffer.append("<" + string_6_ + ">" + strings_4_[q] +
                    "</" + string_6_ + ">\n");
            }

            stringbuffer.append("</" + string_1_ + ">\n");
        }

        stringbuffer.append("\n</" + string_0_ + ">");
        printwriter.print(stringbuffer.toString());
        printwriter.close();
    }

    static String showTable(String string) throws Exception {
        new Traxit(string + ".xml", "ServPak/xsl/dbrcops.xsl", DBM.zefmhome);

        return new String(Traxit.tabby);
    }

    static void exRows(int i, int s) {
        int[] is = new int[numrows];

        for (int q = 0; q < numrows; q++) {
            is[q] = q;

            if (q == i) {
                is[q] = s;
            }

            if (q == s) {
                is[q] = i;
            }
        }

        for (int A = 0; A < numrows; A++) {
            for (int B = 0; B < numcols; B++) {
                table2[is[A]][B] = table[A][B];
            }
        }
    }

    static void exCols(int i, int j) {
        int[] is = new int[numcols];

        for (int q = 0; q < numcols; q++) {
            is[q] = q;

            if (q == i) {
                is[q] = j;
            }

            if (q == j) {
                is[q] = i;
            }
        }

        for (int A = 0; A < numrows; A++) {
            for (int B = 0; B < numcols; B++) {
                table2[A][is[B]] = table[A][B];
            }
        }
    }

    static String[][] transposed(String[][] strings) {

        String[][] strgs = new String[numcols][numrows];

        for (int A = 0; A < numrows; A++) {
            for (int B = 0; B < numcols; B++) {
                strgs[B][A] = strings[A][B];
            }
        }

        return strgs;
    }

    static void realign(String[][] strings) throws Exception {
        numrows = strings.length;
        numcols = strings[0].length;
        table = new String[numrows][numcols];

        for (int i = 0; i < numrows; i++) {
            for (int j = 0; j < numcols; j++) {
                table[i][j] = strings[i][j];
            }
        }
    }
}