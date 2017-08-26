package ZEdit;

import java.io.*;
import java.net.Socket;

	public class SFileClient {

    String host;
    String filename;
	public    String fileout;
    int port;
    Socket server;
	public    StringBuilder sysout;

    public SFileClient(String prehost, String _filename) throws Exception {

        sysout = new StringBuilder();

        int cut = prehost.indexOf(":");

        if (cut < 0) {
            this.host = prehost;
            this.port = 80;
        } else {
            this.host = prehost.substring(0, cut);
            this.port = Integer.parseInt(prehost.substring(cut + 1));
        }

        this.filename = _filename;

        this.fileout = "RemoteFiles/" + host + filename;

	String DIR = fileout.substring(0,fileout.lastIndexOf("/"));

        if (!new File(DIR).exists()) new File(DIR).mkdirs();

        String message = "GET " + filename + " HTTP/1.0";

        this.server = new Socket(host, port);

        InputStream in = server.getInputStream();

        OutputStream out = server.getOutputStream();
        PrintWriter pout = new PrintWriter(out, true);

        FileOutputStream fout = new FileOutputStream(fileout);

        server.setSoTimeout(3000);

        sysout.append("\n" + "Trying to get file " + filename);

        pout.println(message);

        BufferedReader bufi = new BufferedReader(new InputStreamReader(in));

        String w = bufi.readLine();

        if (w.indexOf("HTTP/1.1 200 OK") < 0) {
            fout.write(new String(w + "\n").getBytes());
        }

        for (int q = 0; (q = in.read()) != -1;) fout.write(q);

        fout.flush();
        fout.close();

        sysout.append("\n" + "DONE!");

        server.close();
    }
}
