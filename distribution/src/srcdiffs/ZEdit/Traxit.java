package ZEdit;

import org.xml.sax.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.xml.transform.*;
import javax.xml.transform.stream.*;


public class Traxit {
    //Class
    static String directory;

    public Traxit(String xml, String out) throws Exception {
        this(xml, null, out);
    }

    public Traxit(String xml, String xsl, String out) throws Exception {
        //Constructor
        directory = System.getProperty("user.dir");

        String xls = xsl;

        if (xsl == null) {
            xls = getXSL(xml);
        }

        System.out.println("Using style file " + xls);

        try {
            simpleTrans(xml, xls, out);
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
        }
    }

    public void simpleTrans(String input, String xslID, String fileout)
        throws Exception {
        InputStream xslIS = null;

        if (!new File(xslID).exists()) {
            xslIS = ZEdit.ZEditor.wrapper(xslID);
        } else {
            xslIS = new BufferedInputStream(new FileInputStream(xslID));
        }

        StreamSource ssrc = new StreamSource(xslIS, "file:" + xslID);

        TransformerFactory tfactory = TransformerFactory.newInstance();

        Transformer transformer = tfactory.newTransformer(ssrc);

        StreamSource xmlin = new StreamSource(new StringReader(input));

        xmlin.setSystemId("file:" + xslID);

        PrintWriter pout = new PrintWriter(new FileWriter(fileout), true);

        transformer.transform(xmlin, new StreamResult(pout));

        pout.close();
    }

    String getXSL(String input) throws IOException {
        BufferedReader src = new BufferedReader(new StringReader(input));
        String v;
        String stylefile = null;

        while ((v = src.readLine()) != null) {
            if (v.indexOf("?xml-stylesheet") > 0) {
                stylefile = v.substring(v.indexOf("href=") + 6,
                        v.lastIndexOf('"'));

                return stylefile;
            }
        }

        return "ServPak/xsl/generic.xsl";
    }
}
