/* MKcal - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

import NetsManager.ZEFMServer;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.StringReader;

import java.util.*;

public class MKcal {
    static String ldir;
    static String[] dateinfo = new String[6];
    static int monthindex;
    static int dayindex;
    static String currentTime;
    static String inputString;
    static final String[] daynames = {
        "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"
    };
    static final String[] DAYNAMES = {
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday"
    };
    static final String[] MONTHNAMES = {
        "January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December"
    };
    static final String[] monthnames = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
        "Nov", "Dec"
    };
    static int[] lastday = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    public String printout;

    public MKcal(String string) throws Exception {

        int i = 0;
        int indx = 0;
        String[] strings = new String[7];
        String[] monmon = new String[35];
        String[] wkwk = new String[6];
        HashMap <String,String>hashmap = new HashMap<String,String>();

        cal();
        inputString = string;

        boolean bool;
        String username;
        int weekday;
        int month;
        int year;

        if ((inputString.indexOf("NEXT") > -1) ||
                (inputString.indexOf("BACK") > -1)) {

            int cut = inputString.indexOf("=");
            String pre = inputString.substring(0, cut);
            String[] tox = {};

	if(pre.contains("+")){
		tox = pre.split("\\+");
	} else {
		tox = pre.split("\\s");
	}

            username = tox[0];
            monthindex = Integer.parseInt(tox[1]);
            year = Integer.parseInt(tox[2]);
            month = Integer.parseInt(tox[3]);
            weekday = Integer.parseInt(tox[4]);
            bool = true;
	leapYearCheck(year);

        } else {
            bool = false;

            int locali = inputString.indexOf("=");

            username = inputString.substring(locali + 1);

            if (username.length() == 0) {
                username = ZEFMServer.username;
            }

            weekday = dayindex;
            month = Integer.parseInt(dateinfo[2]);
            year = Integer.parseInt(dateinfo[5]);
	leapYearCheck(year);
        }

        String mName = MONTHNAMES[monthindex];
        String _mname = monthnames[monthindex];
        int lday = lastday[monthindex];
        int _wday = weekday - (month % 7);
        int _day = (_wday < -1) ? (7 + _wday) : _wday;

        Arrays.fill(wkwk, "");
        Arrays.fill(strings, "");
        Arrays.fill(monmon, "");

        for (int q = 0; q <= _day; q++) {
            wkwk[0] += (String.valueOf(-1) + " ");
        }

        for (int q = _day + 1; q < 7; q++) {
            wkwk[0] += (String.valueOf(++indx) + "  ");
        }

        for (int q = 1; q < 6; q++) {
            for (int qq = 0; qq < 7; qq++) {
                if ((indx >= lday) || (indx == -1)) {
                    indx = -1;
                }

                if (indx == (lday - 1)) {
                    i = qq + 1;
                }

                if (indx != -1) {
                    indx++;
                }

                wkwk[q] += (String.valueOf(indx) + " ");
            }
        }

        for (int q = 0; q < 7; q++) {
            strings[q] = "<th>" + daynames[q] + "</th>";
        }

        StringBuilder stringbuffer = new StringBuilder();

        if (!bool) {
            stringbuffer.append(dateinfo[1] + " " + dateinfo[2] +
                " | <font color=red>&nbsp;&nbsp;&nbsp;&nbsp;&laquo;<b>TODAY</b>&raquo;</font>\n");
        }

        ldir = ZEFMServer.userdir;

        File file = new File(ldir + "/diary-" + username + ".txt");

        if (!file.exists()) {
            file.createNewFile();
        }

        BufferedReader bufferedreader = new BufferedReader(new FileReader(ldir +
                    "/diary-" + username + ".txt"));
        String v;

        while ((v = bufferedreader.readLine()) != null) {
            stringbuffer.append(v + "\n");
        }
        BufferedReader bfrder = new BufferedReader(new StringReader(
                    stringbuffer.toString()));

        String _v_;

        while ((_v_ = bfrder.readLine()) != null) {
            if (!_v_.startsWith("#") &&((_v_.indexOf(_mname) > -1) ||(_v_.indexOf("All") > -1))) {

                String pre_v = _v_.substring(0, _v_.indexOf("|"));
                String post_v = _v_.substring(_v_.indexOf("|") + 1);

                pre_v = pre_v.replace(" ","");

                String preprev = pre_v.substring(0, 3);
                String postprev = pre_v.substring(3);

                if (!hashmap.containsKey(postprev)) {
                    hashmap.put(postprev, "");
                }

                if ((preprev.indexOf(_mname) > -1) ||
                        (_v_.indexOf("All") > -1)) {
                    hashmap.put(postprev, hashmap.get(postprev) + post_v);
                }
            }
        }

        for (int q = 0; q < wkwk.length; q++) {
            String[] st = wkwk[q].split("\\s+");

            monmon[q] = "<tr>";

            String w = "";

	for( String vx : st ) {

                if (vx.equals("-1")) {
                    w = "<br>";
                } else {
	         w = ("<a href=Diary.jav?" + _mname + "+" + username + "=" + vx + ">" + vx +"</a>");
                }

                String _line;

                if (hashmap.containsKey(vx)) {
                    String data = hashmap.get(vx);

                    _line = "<font size=-1>" + data + "</font>";
                } else {
                    _line = "";
                }
     monmon[q] += ("<td valign=top width=9% height=15%>" + (String) w + (String) _line + "</td>\n");
	}
	       monmon[q] += "</tr>\n";
        }

        int shiftidx = (monthindex < 11) ? (monthindex + 1) : 0;
        int shftmonth = (shiftidx == 0) ? (year + 1) : year;
        int _idx_ = 1;

        _v_ = "";
        _v_ += "<form action=MKcal.jav method=get>";

        _v_ += ("<input type=submit value=NEXT id=NEXT name=\"" +
        (String) username + " " + shiftidx + " " + shftmonth + " " + _idx_ + " " + i + "\">");

        int _shiftidx = (monthindex > 0) ? (monthindex - 1) : 11;
        int _shftmonth = (_shiftidx == 11) ? (year - 1) : year;
        int _lday = lastday[_shiftidx];
        int _day_ = _day;
        String vvv = "";

        vvv += "<form action=MKcal.jav method=post>";
        vvv += ("<input type=submit value=BACK id=BACK name=\"" +
        (String) username + " " + _shiftidx + " " + _shftmonth + " " + _lday + " " +
        _day_ + "\">");
        vvv += "</form>";

        StringBuilder buffy = new StringBuilder();

        buffy.append("<html>\n");
        buffy.append("  <head>\n");
        buffy.append(
	"<title> Diary Calendar for " + username + " </title>\n");
        buffy.append(
	"<script type='text/javascript' src='"
	+ZEFMServer.userdir+"/ServPak/js/calnav.js'></script>\n");
        buffy.append("  </head>\n");
        buffy.append("  <body> \n");
        buffy.append(
            "  <table align=center cellspacing=0 border=1 width=100% height=98%> \n");
        buffy.append(
	"    <caption>" + mName + " " + year +" </caption>\n");
        buffy.append("<tr>");

        for (int q = 0; q < strings.length; q++) {
            buffy.append(strings[q]);
        }

        buffy.append(" </tr>\n");

        for (int q = 0; q < monmon.length; q++) {
            buffy.append(monmon[q] + "\n");
        }

        buffy.append("  </table>\n");
        buffy.append("<hr>\n");
        buffy.append(currentTime + " " + _v_ + " " +
            vvv + "\n");
        buffy.append("</font>\n");
        buffy.append("</body>\n");
        buffy.append("</html>\n");
        printout = buffy.toString();
    }

    public static void cal() {

        dateinfo = new Date().toString().split("\\s+");

        for (int i = 0; i < monthnames.length; i++) {
            if (monthnames[i].equals(dateinfo[1])) {
                monthindex = i;
                break;
            }
        }

        for (int i = 0; i < daynames.length; i++) {
            if (daynames[i].equals(dateinfo[0])) {
                dayindex = i;

                break;
            }
        }

        if (dateinfo[2].startsWith("0")) {
            dateinfo[2] = dateinfo[2].substring(1);
        }

        currentTime = ("It is now " + dateinfo[3] + " on " +
            DAYNAMES[dayindex] + ", " + MONTHNAMES[monthindex] + " " +
            dateinfo[2] + ", " + dateinfo[5]);
    }

public static void leapYearCheck(int yr){

	lastday[1] = 28;

	int mod4 = yr % 4;
	int modcent = yr % 100;
	int mod4cent = yr % 400;

	if(modcent==0){
		if(mod4cent==0) lastday[1] = 29;
		  } else {
	if(mod4==0) lastday[1] = 29;
		  }
	}
}