package ServPak.jv;

import NetsManager.*;


public class FileOps {
    public static String processcall;
    static String whichproc;
    public String printout;
    String request;

    public FileOps(String string) throws Exception {
        if (string.endsWith("C=GO") || string.endsWith("X=GO") ||
                string.endsWith("M=GO")) {
            request = processcall + string;
            ZConnection.whichproc = whichproc;
        } else {
            int cut = string.lastIndexOf("@!!@x=");

            string = string.replace('&', '?');
            request = string.substring(0, cut);

            for (int q = 0; q < ZConnection.processes.length; q++) {
                if (request.indexOf(ZConnection.processes[q]) > 0) {
                    ZConnection.whichproc = ZConnection.processrun[q];
                    processcall = ZConnection.processes[q];
                }
            }
        }

        XCommands cary = new XCommands(request);

        if (cary.returns != null) { 
            printout = cary.returns;
        }
            whichproc = ZConnection.whichproc;
    }
}
