/* DBanalyze - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

import Jama.Matrix;

import NetsManager.Traxit;

import java.io.FileWriter;
import java.io.PrintWriter;

import java.util.Arrays;
import java.util.StringTokenizer;


public class DBanalyze {
    static String[][] table;
    static String filenomen;
    static String filename;
    static String[] grds = { "", "", "", "", "" };
    static Matrix matty;
    static Matrix Scores;
    static Matrix Totals;
    static double[][] doby;
    static int numcols;
    static int numrows;
    static double maximum;
    static double mean;
    static double std;
    static double setmax;
    static double setmean;
    static boolean renew;
     PrintWriter printwriter;
     StringBuilder stringbuffer;
    public String printout;
    Matrix Out;
    boolean transpose;
    boolean statistics;
    boolean scores;

    public DBanalyze(String string) throws Exception {
        renew = false;

        if (string.indexOf("renew") >= 0) {
            renew = true;
            new DBanalyze(table, filename);
            printout = DBgo.getFile("HTML/dbanalyze.html");
        } else {
            numrows = matty.getRowDimension();
            numcols = matty.getColumnDimension();

            if (string.indexOf("transpose") > -1) {
                transpose = true;
                matty = matty.transpose();
                doby = matty.getArray();
            }

            if (string.indexOf("grddist") > -1) {
                String string_9_ = ("<p>&nbsp;<p> For a maximum of " + setmax +
                    " with a mean of " + setmean + "<p>&nbsp;<p>");

                string_9_ += ("A  &#160;&#160;&#160; " + grds[0] + "<p>\n");
                string_9_ += ("B  &#160;&#160;&#160; " + grds[1] + "<p>\n");
                string_9_ += ("C  &#160;&#160;&#160; " + grds[2] + "<p>\n");
                string_9_ += ("D  &#160;&#160;&#160; " + grds[3] + "<p>\n");
                string_9_ += ("F   &#160;&#160;&#160; " + grds[4]);
                grds = new String[] { "", "", "", "", "" };
                printout = string_9_;
            } else if (string.indexOf("prtgrds") > -1) {
                String[][] strings = new String[numrows + 1][2];
                double[][] ds = Scores.getArray();

                for (int i = 1; i <= numrows; i++) {
                    strings[i][0] = table[i][0];

                    double d = roundMe(ds[i - 1][0]);

                    strings[i][1] = String.valueOf(d);
                }

                strings[0][0] = "Name";
                strings[0][1] = "zzScore";
                filenomen = filename + "_list";
                writeMatrix2XML(filenomen, strings);
                printout = showTable(filenomen);
            } else if (string.indexOf("interpolation") > -1) {
                String[][] strings = new String[numrows + 1][3];
                double[][] ds = Totals.getArray();
                double[] ds_10_ = null;
                double[] ds_11_ = null;
                StringTokenizer stringtokenizer = new StringTokenizer(string,
                        "&");

                while (stringtokenizer.hasMoreTokens()) {
                    String string_12_ = stringtokenizer.nextToken();

                    if (string_12_.indexOf("ins") >= 0) {
                        int i = string_12_.indexOf("=");
                        StringTokenizer stringtokenizer_13_ = new StringTokenizer(string_12_.substring(i +
                                    1), "+");

                        ds_10_ = new double[stringtokenizer_13_.countTokens()];

                        int i_14_ = 0;

                        while (stringtokenizer_13_.hasMoreTokens()) {
                            ds_10_[i_14_] = Double.parseDouble(stringtokenizer_13_.nextToken());
                            i_14_++;
                        }
                    }

                    if (string_12_.indexOf("outs") >= 0) {
                        int i = string_12_.indexOf("=");
                        StringTokenizer stringtokenizer_15_ = new StringTokenizer(string_12_.substring(i +
                                    1), "+");

                        ds_11_ = new double[stringtokenizer_15_.countTokens()];

                        int i_16_ = 0;

                        while (stringtokenizer_15_.hasMoreTokens()) {
                            ds_11_[i_16_] = Double.parseDouble(stringtokenizer_15_.nextToken());
                            i_16_++;
                        }
                    }
                }

                for (int i = 1; i <= numrows; i++) {
                    strings[i][0] = table[i][0];

                    double d = roundMe(ds[i - 1][0]);

                    strings[i][1] = String.valueOf(d);
                    strings[i][2] = String.valueOf(interP(d, ds_10_, ds_11_));
                }

                strings[0][0] = "Name";
                strings[0][1] = "zzTotals";
                strings[0][2] = "zzScores";
                filenomen = filename + "_list";
                writeMatrix2XML(filenomen, strings);
                printout = showTable(filenomen);
            } else {
                if (string.indexOf("totals") > -1) {
                    Matrix matrix = new Matrix(numcols, 1, 1.0);
                    Matrix matrix_17_ = new Matrix(numrows, 1, 1.0);

                    Totals = matty.times(matrix);

                    if (string.indexOf("statistics") > -1) {
                        statistics = true;
                        Out = new Matrix(numrows + 1, numcols + 3);
                        Out.setMatrix(1, numrows, numcols + 1, numcols + 1,
                            Totals);
                        Out.setMatrix(1, numrows, 1, numcols, matty);
                        mean = (Totals.transpose().times(matrix_17_).get(0, 0) * (1.0 / (double) numrows));

                        double[][] ds = Totals.transpose().getArray();
                        double[] ds_18_ = ds[0];

                        Arrays.sort(ds_18_);
                        maximum = ds_18_[numrows - 1];
                        std = Math.sqrt((Totals.transpose().times(Totals).get(0,
                                    0) * (1.0 / (double) numrows)) -
                                (mean * mean));
                        mean = roundMe(mean);
                        std = roundMe(std);
                    } else {
                        Out = new Matrix(numrows + 1, numcols + 2);
                        Out.setMatrix(1, numrows, numcols + 1, numcols + 1,
                            Totals);
                        Out.setMatrix(1, numrows, 1, numcols, matty);
                    }

                    doby = Out.getArray();
                }

                if (string.indexOf("scores") > -1) {
                    scores = true;

                    StringTokenizer stringtokenizer = new StringTokenizer(string,
                            "&");

                    while (stringtokenizer.hasMoreTokens()) {
                        String string_19_ = stringtokenizer.nextToken();

                        if (string_19_.indexOf("aximum") > 0) {
                            setmax = Double.parseDouble(string_19_.substring(string_19_.indexOf(
                                            "=") + 1));
                        }

                        if (string_19_.indexOf("ean") > 0) {
                            setmean = Double.parseDouble(string_19_.substring(string_19_.indexOf(
                                            "=") + 1));
                        }
                    }

                    Matrix matrix = new Matrix(numrows, numrows, 1.0);
                    Matrix matrix_20_ = Matrix.identity(numrows, numrows);
                    Matrix matrix_21_ = (matrix_20_.minus(matrix.timesEquals(
                                1.0 / (double) numrows)));
                    Matrix matrix_22_ = matrix_21_.times(matty);
                    Matrix matrix_23_ = matty.transpose().times(matrix_22_);
                    Matrix matrix_24_ = new Matrix(numcols, numcols);

                    for (int i = 0; i < numcols; i++) {
                        matrix_24_.set(i, i,
                            Math.sqrt((double) numrows / matrix_23_.get(i, i)));
                    }

                    Matrix matrix_25_ = matrix_22_.times(matrix_24_);
                    Matrix matrix_26_ = new Matrix(numcols, 1, 1.0);

                    Totals = matrix_25_.times(matrix_26_);

                    double[][] ds = Totals.transpose().getArray();
                    double[] ds_27_ = ds[0];

                    Arrays.sort(ds_27_);

                    double d = ds_27_[numrows - 1];

                    Scores = new Matrix(numrows, 1);

                    for (int i = 0; i < numrows; i++) {
                        double d_28_ = (setmean +
                            (((setmax - setmean) * Totals.get(i, 0)) / d));

                        Scores.set(i, 0, d_28_);

                        if (d_28_ == 100.0) {
                            grds[0] += "#";
                        } else {
                            String string_29_ = String.valueOf(d_28_);
                            int i_30_ = Integer.parseInt(string_29_.substring(
                                        0, 1));

                            if (i_30_ > 5) {
                                grds[9 - i_30_] += "#";
                            }

                            if (i_30_ < 6) {
                                grds[4] += "#";
                            }
                        }
                    }

                    Out = new Matrix(numrows + 1, numcols + 3);
                    Out.setMatrix(1, numrows, numcols + 1, numcols + 1, Totals);
                    Out.setMatrix(1, numrows, numcols + 2, numcols + 2, Scores);
                    Out.setMatrix(1, numrows, 1, numcols, matrix_25_);
                    doby = Out.getArray();
                }

                String[][] strings = new String[doby.length][doby[0].length];

                for (int i = 0; i < doby.length; i++) {
                    for (int i_31_ = 0; i_31_ < doby[0].length; i_31_++) {
                        double d = roundMe(doby[i][i_31_]);

                        strings[i][i_31_] = String.valueOf(d);
                    }
                }

                if (!transpose) {
                    for (int i = 0; i <= numcols; i++) {
                        strings[0][i] = stripZZ(table[0][i]);
                    }

                    for (int i = 1; i <= numrows; i++) {
                        strings[i][0] = table[i][0];
                    }

                    strings[0][numcols + 1] = "Totals";

                    if (statistics) {
                        strings[0][numcols + 2] = "Statistics";
                        strings[1][numcols + 2] = "Max = " + maximum;
                        strings[2][numcols + 2] = "mean = " + mean;
                        strings[3][numcols + 2] = "std_dev = " + std;

                        for (int i = 4; i <= numrows; i++) {
                            strings[i][numcols + 2] = "-";
                        }
                    }

                    if (scores) {
                        strings[0][numcols + 2] = "Scores";
                    }
                }

                filenomen = filename + "_Z";
                writeMatrix2XML(filenomen, strings);
                printout = showTable(filenomen);
            }
        }
    }

    public DBanalyze(String[][] strings, String string)
        throws Exception {
        table = strings;

        if (renew) {
            filename = string;

            if (!filename.startsWith("DB")) {
		filename = "DB/" + string; 
		System.out.println("Correcting file location.");
				    }

        } else {
            filename = "DB/" + string;
        }

        numrows = table.length - 1;
        numcols = table[0].length - 1;

        double[][] ds = new double[numrows][numcols];

        for (int i = 1; i < table.length; i++) {
            for (int i_32_ = 1; i_32_ < table[0].length; i_32_++) {
                ds[i - 1][i_32_ - 1] = Double.parseDouble(table[i][i_32_]);
            }
        }

        matty = new Matrix(ds);
    }

       void writeMatrix2XML(String string, String[][] strings)
        throws Exception {
        printwriter = new PrintWriter(new FileWriter(string + ".xml"), true);
        stringbuffer = new StringBuilder();

        String string_0_ = "matrix";
        String string_1_ = "entry";
        String[] strings_2_ = strings[0];

        stringbuffer.append("<?xml version=\"1.0\"?>\n");
        stringbuffer.append("<" + string_0_ + ">\n");

        for (int i = 1; i < strings.length; i++) {
            String string_3_ = "";
            String[] strings_4_ = strings[i];

            stringbuffer.append("\n<" + string_1_ + ">\n");

            for (int i_5_ = 0; i_5_ < strings_4_.length; i_5_++) {
                String string_6_ = strings_2_[i_5_].toLowerCase();

                stringbuffer.append("<" + string_6_ + ">" + strings_4_[i_5_] +
                    "</" + string_6_ + ">\n");
            }

            stringbuffer.append("</" + string_1_ + ">\n");
        }

        stringbuffer.append("\n</" + string_0_ + ">");
        printwriter.print(stringbuffer.toString());
        printwriter.close();
    }

    static String showTable(String string) throws Exception {
        new Traxit(string + ".xml", "ServPak/xsl/dbalz.xsl", DBM.zefmhome);

        return new String(Traxit.tabby);
    }

    static double roundMe(double d) {
        return (double) Math.round(100.0 * d) / 100.0;
    }

    static String stripZZ(String string) {
        if (string.substring(0, 2).equals("zz")) {
            if (Character.isDigit(string.charAt(2))) {
                return "_" + string.substring(2);
            }

            return string.substring(2);
        }

        return string;
    }

    static double interP(double d, double[] ds, double[] ds_7_) {
        int i = 0;

        for (int i_8_ = 0; i_8_ < ds.length; i_8_++) {
            if (d <= ds[i_8_]) {
                i = i_8_ - 1;

                break;
            }
        }

        return roundMe(ds_7_[i] +
            ((ds_7_[i + 1] - ds_7_[i]) / (ds[i + 1] - ds[i]) * (d - ds[i])));
    }
}
