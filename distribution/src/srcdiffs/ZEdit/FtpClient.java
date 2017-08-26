package ZEdit;

import java.io.*;

import java.net.*;

import java.util.*;


class FtpClient {
    private static Splitz Loginfo;
    private static Splitz PortInfo;
    private static Splitz User;

    public FtpClient(String[] argv) {
        if (argv.length != 4) {
            System.out.println("Invalid arguments.");

            return;
        }

        User = new Splitz(argv[0], "@");

        String prehost = User.Id[1];
        String to = User.Id[0];
        String pwd = argv[3];

        try {
            int cut = prehost.indexOf(":");

            String host;
            int port;

            if (cut < 0) {
                host = prehost;
                port = 21;
            } else {
                host = prehost.substring(0, cut);
                port = Integer.parseInt(prehost.substring(cut + 1));
            }

            Socket server = new Socket(host, port);
            InputStream in = server.getInputStream();
            OutputStream out = server.getOutputStream();
            BufferedReader bin = new BufferedReader(new InputStreamReader(in));
            PrintWriter pout = new PrintWriter(out, true);

            server.setSoTimeout(3000);

            StringWriter swi = new StringWriter();

            pout.println("user " + to);

            swi.write(GetResponse(bin).text);

            pout.println("pass " + pwd);

            while (true) {
                Loginfo = GetResponse(bin);

                if ((Loginfo.Id[0].equals("230")) &&
                        (Loginfo.Id[1].equals("User"))) {
                    break;
                }

                swi.write(Loginfo.text + "\n");
            }

            pout.println("type I");

            swi.write(GetResponse(bin).text + "\n");

            pout.println("pasv");

            while (true) {
                Loginfo = GetResponse(bin);

                if (Loginfo.Id[0].equals("227")) {
                    break;
                }

                swi.write(Loginfo.text);
            }

            String portinfo = Loginfo.text;

            swi.write(portinfo + "\n");

            PortInfo = new Splitz(portinfo, ",");

            PortInfo.DropParen();

            int pp1 = Integer.parseInt(PortInfo.Id[4]);
            int p1 = pp1 << 8;
            int p2 = Integer.parseInt(PortInfo.Id[5]);

            int prt = p1 + p2;

            Socket dataserver = new Socket(host, prt);

            OutputStream dout = dataserver.getOutputStream();
            DataOutputStream dpout = new DataOutputStream(dout);

            pout.println("stor " + argv[2]);

            PutInfo(argv[1], dpout);

            swi.write(GetResponse(bin).text);

            dataserver.close();

            server.close();
            swi.flush();
            swi.close();
            System.out.println(swi.toString());
        } catch (IOException e) {
            System.out.println(e);
        }
    }

    static Splitz GetResponse(BufferedReader bn) throws IOException {
        String reply = bn.readLine();
        Splitz rply = new Splitz(reply);

        return rply;
    }

    public static void PutInfo(String filename, DataOutputStream pwrite)
        throws IOException {
        FileInputStream fl = new FileInputStream(filename);

        try {
            byte[] data = new byte[fl.available()];
            fl.read(data);
            pwrite.write(data);
            pwrite.flush();
            pwrite.close();
        } catch (Exception e) {
        }
    }
}
