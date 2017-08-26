/* ShowNotes - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

import NetsManager.Traxit;

import java.io.*;

import java.net.*;
import java.sql.*;

public class ShowNotes {
    public String printout;
               Connection conn;
	   ResultSet rs;

    public ShowNotes(String string) throws Exception {

		conn = ZEdit.DOps.goMysql;

        String pre = string.substring(string.indexOf("&") + 1);
        String post = string.substring(string.indexOf("=") + 1, string.indexOf("&"));
        String postpre = pre.substring(pre.indexOf("=") + 1);

        postpre = DBM.converter(postpre);

try{
                  rs = conn.createStatement().executeQuery(
		"SELECT data FROM notes WHERE filename='"+post+"' and link like '"+postpre+"'");

	                                   rs.next();
    }catch( Exception e ) {            
	System.out.println(e.getMessage()); 
    }

        StringBuilder stringbuffer = new StringBuilder("<?xml version=\"1.0\"?>\n <notesml>\n");
        stringbuffer.append(new String(rs.getBytes("data"), "UTF-8"));
        stringbuffer.append("\n</notesml>");

        new Traxit(stringbuffer, "ServPak/xsl/shownotes.xsl", postpre);

        BufferedReader bufr = new BufferedReader(new StringReader(new String(Traxit.tabby)));

        boolean istpml = false;

        String externalReference = "";

        for (String v; (v = bufr.readLine()) != null;) {
            v = v.trim();

            if (v.indexOf("<reference>") >= 0) {
                istpml = true;

                continue;
            }

            if (istpml) {
                externalReference = v;

                break;
            }
        }

        byte[] fin = null;

        if (istpml) {
	
	System.out.println("Getting "+externalReference);

            if (!externalReference.startsWith("http://")) {
                FileInputStream inputstream = new FileInputStream(externalReference);

                fin = new byte[inputstream.available()];
                inputstream.read(fin);
            }

            String stylefile = "";

            if (!externalReference.endsWith(".tpml") &&
                    !externalReference.endsWith(".xml")) {
                if (externalReference.startsWith("http://")) {
                    try {
                        URL url = new URL(externalReference);

                        URLConnection urla = url.openConnection();
                        InputStream GetIt = urla.getInputStream();
                        ByteArrayOutputStream Fileit = new ByteArrayOutputStream();

                        for (int q = 0; (q = GetIt.read()) != -1;) {
                            Fileit.write(q);
                        }

                        Fileit.flush();
                        printout = new String(Fileit.toByteArray());
                    } catch (Exception urlex) {}
                } else {
                    printout = new String(fin);
                }
            } else {
                BufferedReader src = new BufferedReader(new StringReader(new String(fin)));

                for (String v; (v = src.readLine()) != null;) {
                    if (v.indexOf("?xml-stylesheet") > 0) {
                        stylefile = v.substring(v.indexOf("href=") + 6, v.lastIndexOf('"'));

                        break;
                    }
                }

                new Traxit(fin, stylefile, null);

                printout = new String(Traxit.tabby);
            }
        } else {
            printout = new String(Traxit.tabby);
        }
    }
}