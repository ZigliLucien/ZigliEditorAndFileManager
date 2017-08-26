package NetsManager;

import java.io.*;

import java.net.*;


class FileUpConnection extends Thread {
    static final String[] domains = ZConnection.domains;
    static final String[] addresses = ZConnection.addresses;
    Socket client;
    String replymsg;
    PrintWriter printWriter;

    FileUpConnection(Socket socket) throws SocketException {
        client = socket;

        this.replymsg = ZEFMServer.replymsg;
    }

    public void run() {
        InetAddress inetAddress = client.getInetAddress();
        String address = inetAddress.toString();

        System.out.println(new StringBuilder("Connected to").append(address)
                                                           .toString());

        try {
            InputStream inputStream = client.getInputStream();

            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(
                        inputStream));

            DataInputStream dataInputStream = new DataInputStream(inputStream);

            OutputStream outputStream = client.getOutputStream();
            printWriter = new PrintWriter(outputStream, true);
/*
            if (!check(inetAddress)) {
                System.out.println("Address unaccepted: upload.");
                printWriter.println("Not Available.");
                client.close();

                return;
            } else {
*/
                String dom = bufferedReader.readLine();

/*
                if (!dom.equals(replymsg)) {
                    System.out.println("Address check.");
                    printWriter.println("Not Available.");
                    client.close();

                    return;
                } else {
*/
                    printWriter.println("Ready");

                    String info = bufferedReader.readLine();

                    System.out.println("Uploading " + info);

                    String objectfile = bufferedReader.readLine();
                    int numbytes = Integer.parseInt(bufferedReader.readLine());

                    printWriter.println("Proceed");

                    FileOutputStream fileOutputStream = new FileOutputStream(objectfile);

                    byte[] datain = new byte[numbytes];

                    dataInputStream.readFully(datain);
                    fileOutputStream.write(datain);
                    fileOutputStream.flush();
                    fileOutputStream.close();

                    System.out.println(objectfile + " written");
                    printWriter.println(objectfile + " written");
 //               }
   //         }

            client.close();

            try {
                ZConnection.uplds.close();
            } catch (Exception eupl) {
                System.out.println(eupl.getMessage());

                return;
            }

            return;
        } catch (IOException e) {
            System.out.println("I/O Error");
            printWriter.println("Aborting");
            client.close();
        } finally {
            try {
                ZConnection.uplds.close();
            } catch (Exception eupl) {
                System.out.println(eupl.getMessage());
            }

            return;
        }
    }

    public boolean check(InetAddress addr) throws IOException {
        return (ZConnection.loggedin &&
        ZConnection.currentclient.equals(addr.getHostAddress()));
    }
}
