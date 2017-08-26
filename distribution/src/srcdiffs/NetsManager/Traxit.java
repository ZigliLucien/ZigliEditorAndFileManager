package NetsManager;

import java.io.*;

import java.net.*;

import java.util.*;

import net.sf.saxon.om.*;
import javax.xml.transform.*;
import javax.xml.transform.stream.*;

public class Traxit {
             String parameter;
             BufferedReader src;
    	 ByteArrayOutputStream jack;
    	 StreamSource xmlin;
    	 StreamSource ssrc;
    	 InputStream xslIS;
             Transformer transformer;
    public static byte[] tabby;
    static final byte[] except = ("Check the xml file.").getBytes();

    public Traxit(String xml) {
        this(xml, null, null);
    }

    public Traxit(String xml, String xsl, String _parameter) {
        //Constructor
        this.parameter = _parameter;

        String xls = xsl;

        if (xsl == null) {

            xls = getXSL(xml,0);

	if(xls.equals("goGeneric") || xls.endsWith("generic.xsl")) {
		System.out.println("Going generic 1");

		genericRun(xml,1);
		return;
	}
	           System.out.println("Found style file 1 " + xls);

            } else {
	          System.out.println("Using style file 1 " + xls);
	}

        try {
            objTrans(xml, xls, 1);
        } catch (Exception ex) {
            tabby = except;

            return;
        }
    }

    public Traxit(String xml, String xsl) {
        this(xml, xsl, null);
    }

    public Traxit(byte[] xml, String xsl, String _parameter) {
        parameter = _parameter;
        String xls = xsl;
	if (xsl == null) {

	 xls = getXSL(new String(xml),1);

	if(xls.equals("goGeneric") || xls.endsWith("generic.xsl")) {
		System.out.println("Going generic 2");

		genericRun(xml,2);
		return;
	}
	           System.out.println("Found style file 2 " + xls);

            } else {

	        System.out.println("Using style file 2 " + xls); 
    }

        try {
            objTrans(xml, xsl, 2);
        } catch (Exception ex) {
            tabby = except;

            return;
        }
    }

    public Traxit(StringBuilder xml, String xsl, String _parameter) {
        this.parameter = _parameter;
        String xls = xsl;
	if (xsl == null) {

		xls = getXSL(xml.toString(),1);

	if(xls.equals("goGeneric") || xls.endsWith("generic.xsl")) {
		System.out.println("Going generic 0");

		genericRun(xml,0);
		return;
	}
	           System.out.println("Found style file 0 " + xls);

            } else {
	           System.out.println("Using style file 0 " + xls);
	}

        try {
            objTrans(xml, xsl, 0);
        } catch (Exception ex) {
            tabby = except;

            return;
        }
    }

    public  void objTrans(Object input, String xslID, int signature)
        throws IOException, TransformerException, 
            TransformerConfigurationException, FileNotFoundException {
        if (!new File(xslID).exists()) {
            xslIS = ClassLoader.getSystemResourceAsStream(xslID);
        } else {
            xslIS = new FileInputStream(xslID);
        }

        ssrc = new StreamSource(xslIS, "file:" + xslID);

        transformer =  TransformerFactory.newInstance().newTransformer(ssrc);

        transformer.setParameter("value", parameter);

        switch (signature) {
        case (0):
            xmlin = new StreamSource(
		new ByteArrayInputStream(((StringBuilder) input).toString().getBytes("UTF-8")));

            break;

        case (1):
            xmlin = new StreamSource(new FileInputStream((String) input));

            break;

        case (2):
            xmlin = new StreamSource(new ByteArrayInputStream((byte[]) input));
        }

        xmlin.setSystemId("file:" + xslID);
        jack = new ByteArrayOutputStream();

        transformer.transform(xmlin, new StreamResult(jack));
        jack.flush();

        tabby = jack.toByteArray();
    }

        String getXSL(String input, int signature) {
        try {

if(signature==0){
            		src = new BufferedReader(new FileReader(input));
	} else {
			src = new BufferedReader(new StringReader(input));	
	}

            for (String v; (v = src.readLine()) != null;) {
                if (v.indexOf("?xml-stylesheet") > 0) {
		int cut = v.indexOf("href=") + 6;
                    return v.substring(cut, v.indexOf('"',cut));
                }
            }
        } catch (Exception ioe) {
		return ioe.getMessage();
        }
	        return "goGeneric";
    }


	void genericRun(Object input, int signature) {

	try{

switch (signature) {
        case (0):
            xslIS = new ByteArrayInputStream(((StringBuilder) input).toString().getBytes("UTF-8"));

            break;

        case (1):
            xslIS = new FileInputStream((String) input);

            break;

        case (2):
            xslIS = new ByteArrayInputStream((byte[]) input);
        }
		tabby = (new Query(xslIS, "ServPak/xql/generic.xql", null, true)).qtabby.toByteArray();
	}catch(Exception iie){
		System.out.println(iie.getMessage());
	}

	}
}
