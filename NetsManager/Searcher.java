package NetsManager;

import java.io.*;

import java.util.*;


public class Searcher {
    //Class
    int epsilon;
    String datafile;
    String stringProcessFile;
    String sortFile;
    public byte[] searchResults;
    String value;
    String objectvalu;
    StringTokenizer info;

    public Searcher(String file, String val) throws Exception {
        // Constructor
        String twovalues = "";
        String name = null;

        try {
            if (file.endsWith("sdb")) {
                name = file.substring(0, file.indexOf(".sdb"));
            } else {
                Exception e = new Exception("FileType Error");
                e.getMessage();
            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        epsilon = 2;
        datafile = name.substring(name.indexOf("DB/"))+".xml";

        stringProcessFile = "XSL/xmlquery.xsl";
        sortFile = "XSL/xrunit.xsl";

        String infotok;

        info = new StringTokenizer(val, "&");

        StringBuilder buff = new StringBuilder();

        while (info.hasMoreTokens()) {
            infotok = info.nextToken();
            objectvalu = infotok.substring(infotok.indexOf("=") + 1);

            if (!objectvalu.toLowerCase().equals("all")) {
                if (value != null) {
                    buff.append("!" + objectvalu);
                } else {
                    value = objectvalu;
                    buff.append(value);
                }
            }
        }

        StringTokenizer valley = new StringTokenizer(buff.toString(), "!");

        int numtokens = valley.countTokens();

        if (numtokens > epsilon) {
            for (int q = 0; q < numtokens; q++) {
                if (q == 0) {
                    new Traxit(datafile, stringProcessFile, valley.nextToken());
                }

                if ((q > 0) & (q < (numtokens - epsilon))) {
                    new Traxit(Traxit.tabby, stringProcessFile,
                        valley.nextToken());
                }

                if (q == (numtokens - epsilon)) {
                    switch (epsilon) {
                    case (1):
                        new Traxit(Traxit.tabby, sortFile,
                            valley.nextToken().toLowerCase());

                        break;

                    default:
                        twovalues = (new String(valley.nextToken() + "-" +valley.nextToken())).toLowerCase();

                        new Traxit(Traxit.tabby, sortFile, twovalues);
                    }
                }
            }
        } else {
            switch (epsilon) {
            case (1):
                new Traxit(datafile, sortFile, valley.nextToken().toLowerCase());

                break;

            default:
                twovalues = (new String(valley.nextToken() + "-" + valley.nextToken())).toLowerCase();

                new Traxit(datafile, sortFile, twovalues);
            }
        }

        searchResults = Traxit.tabby;

        new Traxit(datafile, "ServPak/xsl/xsort.xsl", twovalues);

        FileOutputStream flt = new FileOutputStream(name + ".sdb.xml");
        flt.write(Traxit.tabby);
        flt.flush();
        flt.close();
    }
}
