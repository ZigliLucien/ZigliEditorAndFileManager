package NetsManager;

import org.apache.batik.bridge.*;
import org.apache.batik.parser.*;
import org.apache.batik.transcoder.*;
import org.apache.batik.transcoder.image.*;
import org.apache.batik.util.*;
import javax.xml.parsers.*;
import java.io.*;


public class ProcessSVG {
    InputStream out;

    public ProcessSVG(String arg) throws Exception {
        String zname = "";

        String filename = Commands.directory + "/" + arg;

        int cut = filename.lastIndexOf("/");

        String dirctry = Commands.directory.replace('/', '_');

        String xname = filename.substring(cut + 1) + "_" + dirctry;

        String dirname = System.getProperty("user.dir");

        if (!(new File(dirname + "/SVG").exists())) {
            new File(dirname + "/SVG").mkdir();
        }

        zname = dirname + "/SVG/" + xname + ".png";

        File xmli = new File(filename);

        File zxi = new File(zname);

        if (zxi.exists() && (xmli.lastModified() < zxi.lastModified())) {
            System.out.println("Showing " + zname);
        } else {
            PNGTranscoder t = new PNGTranscoder();

//     t.addTranscodingHint(PNGTranscoder.KEY_XML_PARSER_CLASSNAME, 
//	"com.sun.org.apache.xerces.internal.jaxp.SAXParserFactory");

            String svgURI = new File(filename).toURL().toString();
            TranscoderInput input = new TranscoderInput(svgURI);

            OutputStream ostream = new FileOutputStream(zname);

            TranscoderOutput output = new TranscoderOutput(ostream);

            t.transcode(input, output);

            ostream.flush();
            ostream.close();
        }

        this.out = new FileInputStream(zname);
    }
}
