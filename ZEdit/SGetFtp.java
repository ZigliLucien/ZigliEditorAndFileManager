package ZEdit;

import java.io.*;

import java.net.Socket;


	public class SGetFtp {
    String host;
    String filename;
	public    String fileout;
    int port;
    Socket server;
	public    StringBuilder sysout;
    String user;
    Splitz Loginfo;
    Splitz PortInfo;

    public SGetFtp(String[] argv) throws Exception {
        sysout = new StringBuilder();

        String prehost = argv[0];
        filename = argv[1];

        String pwd = argv[2];

        int atcut = prehost.indexOf("@");
        user = prehost.substring(0, atcut);
        prehost = prehost.substring(atcut + 1);

        int cut = prehost.indexOf(":");

        if (cut < 0) {
            this.host = prehost;
            this.port = 21;
        } else {
            this.host = prehost.substring(0, cut);
            this.port = Integer.parseInt(prehost.substring(cut + 1));
        }

       this.fileout = "RemoteFiles/" + host + filename;

	String DIR = fileout.substring(0,fileout.lastIndexOf("/"));

        if (!new File(DIR).exists()) new File(DIR).mkdirs();
        
        this.server = new Socket(host, port);

        server.setSoTimeout(4000);

        InputStream in = server.getInputStream();
        BufferedReader bin = new BufferedReader(new InputStreamReader(in));

        OutputStream out = server.getOutputStream();
        PrintWriter pout = new PrintWriter(out, true);

        FileOutputStream fout = new FileOutputStream(fileout);

        pout.println("user " + user);

        pout.println("pass " + pwd);

        while (true) {
            Loginfo = GetResponse(bin);

            if ((Loginfo.Id[0].equals("230")) &&
                    (Loginfo.text.indexOf(user) >= 0)) {
                break;
            }

            if ((Loginfo.Id[0].equals("530"))) {
                server.close();

                return;
            }
        }

        pout.println("type I");

        pout.println("pasv");

        while (true) {
            Loginfo = GetResponse(bin);

            if (Loginfo.Id[0].equals("227")) {
                break;
            }
        }

        String portinfo = Loginfo.text;

        PortInfo = new Splitz(portinfo, ",");
        PortInfo.DropParen();

        int pp1 = Integer.parseInt(PortInfo.Id[4]);
        int p1 = pp1 << 8;
        int p2 = Integer.parseInt(PortInfo.Id[5]);

        int prt = p1 + p2;

        Socket dataserver = new Socket(host, prt);

        InputStream dpin = dataserver.getInputStream();

        dataserver.setSoTimeout(5000);
        pout.println("retr " + filename);
        Loginfo = GetResponse(bin);

        if (!(Loginfo.Id[0].equals("550"))) {
            GetInfo(fileout, dpin);
        }

        dataserver.close();

        pout.println("quit");
        Loginfo = GetResponse(bin);

        sysout.append("\n" + "DONE!");

        server.close();
    }

    Splitz GetResponse(BufferedReader bn) throws IOException {
        String reply = bn.readLine();
        sysout.append("\n" + reply);

        Splitz rply = new Splitz(reply);

        return rply;
    }

    public static void GetInfo(String _filename, InputStream pread)
        throws IOException {
        FileOutputStream fl = new FileOutputStream(_filename);

        for (int q = 0; (q = pread.read()) != -1;)
            fl.write(q);

        fl.flush();
        fl.close();

        return;
    }

    public static void main(String[] args) throws Exception {
        new SGetFtp(args);
    }
}
