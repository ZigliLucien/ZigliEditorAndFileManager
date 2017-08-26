package ZEdit;

import java.io.*;

import java.net.Socket;

	public class RemoteClient {
    //Class
 	public   static String reply;
    static Socket server;

	public    RemoteClient(String[] argv) throws Exception {
        String host = argv[0];

        int port = Integer.parseInt(argv[1]);

        String pwtext = argv[4];
        int cut = pwtext.indexOf(",");

        String filename = argv[2];
        String objectfile = argv[3];
        String message = pwtext.substring(0, cut);
        String replymsg = pwtext.substring(cut + 1);	

        reply = "uploading " + filename;

        try {
            server = new Socket(host, port);

            InputStream in1 = server.getInputStream();
            BufferedReader bin1 = new BufferedReader(new InputStreamReader(in1));

            OutputStream out1 = server.getOutputStream();
            PrintWriter pout1 = new PrintWriter(out1, true);

            server.setSoTimeout(8000);

            FileInputStream filein = new FileInputStream(filename);

            pout1.println(message + " " + NetsManager.ZEFMServer.port);
            System.out.println("Sending " + message);

            int servport = Integer.parseInt(bin1.readLine());

            pout1.close();
            server.close();

            System.out.println("Uploading");

            server = new Socket(host, servport);

            InputStream in = server.getInputStream();
            BufferedReader bin = new BufferedReader(new InputStreamReader(in));

            OutputStream out = server.getOutputStream();
            DataOutputStream dout = new DataOutputStream(out);
            PrintWriter pout = new PrintWriter(out, true);

            pout.println(replymsg);

            reply = bin.readLine();

/*
            if (!reply.equals("Ready")) {
                System.out.println("Check again!!");
                server.close();

                return;
           } else {
*/
                System.out.println(reply);
 //           }

            pout.println(filename);
            pout.println(objectfile);

            int numbytes = filein.available();

            pout.println(numbytes);
            reply = bin.readLine();

  //          if (reply.equals("Proceed")) {
                byte[] data = new byte[numbytes];
                filein.read(data);
                dout.write(data);
                dout.flush();
    //        }

            reply = bin.readLine();
            System.out.println(reply);

            server.close();
        } catch (IOException e) {
            System.out.println(e.getMessage());

            try {
                server.close();
            } catch (Exception exc) {
                System.out.println(exc.getMessage());
            }
        }
    }
}
