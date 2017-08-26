package ServPak.jv;

import java.io.FileWriter;
import java.io.PrintWriter;


public class DiaryOut {
    public String printout;

    public DiaryOut(String string) throws Exception {

        String A = string.substring(0, string.indexOf("&"));
        int i = A.indexOf("=");
        String B = A.substring(0, i);
        String info = A.substring(i + 1);

        String[] st = B.split("\\+");

        String out = MKcal.ldir + "/diary-" + st[2] + ".txt";
        PrintWriter printwriter = new PrintWriter(new FileWriter(out, true), true);

        info = info.replace('+', ' ');
        info = DBM.converter(info);

        printwriter.println(st[0] + " " + st[1] + " | " + info);

        MKcal calUpdated = new MKcal(MKcal.inputString);

        printout = calUpdated.printout;
    }
}
