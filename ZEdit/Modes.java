package ZEdit;

import java.awt.Color;

import java.io.*;

import java.util.*;


public class Modes {
	public    String startup;
	public    String modename;
	public    String runcommand;
 	public   String menufile;
	public    String datafile;
	public    String modestring;
	public    String keywordfile;
	public    Color color;
    public Stack <Integer> attgaps = new Stack<Integer>();
	public    int rows;
	public    int columns;
	public    int backshift;

    public Modes(String mode, Properties info) {
        modename = mode;

        String start = mode + "Start";
        startup = info.getProperty(start);
        backshift = 23;
        runcommand = info.getProperty(mode);

        modestring = info.getProperty(mode + "commentstring");
        datafile = "Strings.data." + mode.toLowerCase();
        menufile = mode + ".data";
        keywordfile = mode + ".keywords";

        String size = info.getProperty(mode + "Size");
        int cut = size.indexOf(",");
        rows = Integer.parseInt(size.substring(0, cut));
        columns = Integer.parseInt(size.substring(cut + 1));
    }

    public String ktv(String cmd) {
        this.attgaps.removeAllElements();

        this.backshift = 0;
        this.color = new Color(0x00bc00);

        if ((!modename.equals("Xml") && !modename.endsWith("xml") &&
                !modename.equals("Ant") && !modename.equals("LaTex")) ||
                (cmd.indexOf("*") > 0) || (cmd.indexOf(";") > 0)) {
            this.color = new Color(0x000000);

            if (cmd.indexOf("*") > 0) {
                return cmd.substring(0, cmd.indexOf("*"));
            }

            return cmd;
        }

        if (cmd.indexOf("[") > 0) {
            cmd = cmd.substring(0, cmd.indexOf("[")) +
                cmd.substring(cmd.indexOf("]") + 1);
        }

        if (cmd.indexOf("|") < 0) {
            String out = "<" + cmd + "></" + cmd + ">";
            this.attgaps.push(out.length() - 2 - cmd.length());
            this.backshift = cmd.length() + 3;

            return out;
        }

        int cut = cmd.indexOf("|");
        String preout = cmd.substring(0, cut);
        String mods = cmd.substring(cut + 1);
        String out = "<" + preout;
        StringTokenizer modifs = new StringTokenizer(mods, ",");
        String key = modifs.nextToken();
        String gap = "";
        String attribute = "";
        Stack <Integer> pregaps = new Stack<Integer>();
        int attrcount = 0;
        int attrslength = 0;
        int attreffectivelength = 0;
        boolean noatts = false;

        if (key.equals("G") || key.equals("S")) {
            gap = "\n\n";
        }

        if (key.equals("S")) {
            key = "A";
            noatts = true;
        }

        if (key.equals("A") || key.equals("G")) {
            if (key.equals("A")) {
                this.attgaps.push(preout.length() + 4);
                this.attgaps.push(2);
            } else {
                this.attgaps.push(3);
            }

            this.color = new Color(0x0000ee);

            while (modifs.hasMoreTokens()) {
                attribute = modifs.nextToken();
                attrcount++;

                if (attrcount > 1) {
                    attreffectivelength = attribute.length() + 4;
                    pregaps.push(attreffectivelength);
                    attrslength += attreffectivelength;
                }

                out += (" " + attribute + "=" + "\"\"");
            }

            out += (">" + gap + "</" + preout + ">");

            while (!pregaps.empty()) {
                int temp = pregaps.pop();
                this.attgaps.push(temp);
            }

            if (key.equals("G")) {
                this.backshift = preout.length() + attrslength + gap.length() +
                    5;
            } else if (key.equals("A") && noatts) {
                this.backshift = preout.length() + gap.length() + 2;
            } else {
                this.backshift = preout.length() + attrslength + 5;
            }
        }

        if (key.equals("AE") || key.equals("E")) {
            if (key.equals("AE")) {
                this.attgaps.push(4);
            }

            if (key.equals("E")) {
                this.attgaps.push(1);
            }

            this.color = new Color(0x880088);

            while (modifs.hasMoreTokens()) {
                attribute = modifs.nextToken();
                attrcount++;

                if (attrcount > 1) {
                    attreffectivelength = attribute.length() + 4;
                    pregaps.push(new Integer(attreffectivelength));
                    attrslength += attreffectivelength;
                }

                out += (" " + attribute + "=" + "\"\"");
            }

            while (!pregaps.empty()) {
                int temp = pregaps.pop();
                this.attgaps.push(temp);
            }

            out += "/>";

            if (key.equals("AE")) {
                this.backshift = attrslength + 3;
            } else {
                this.backshift = 0;
            }
        }

        if (key.equals("UL")) {
            this.color = new Color(0xaa5500);

            out = "\\" + preout + "{}{}{}";

            this.attgaps.push(1);
            this.attgaps.push(2);
            this.attgaps.push(2);

            this.backshift = 5;
        }

        if (key.equals("SS")) {

            gap = "\n\n";

            out = "<::"+gap+"::>";

            this.attgaps.push(5);
            this.backshift = 4;
        }

      if (key.equals("X")) {

            out = "<::>";

            this.attgaps.push(2);
            this.backshift = 2;
        }

      if (key.equals("R")) {

            out = "<||>";

            this.attgaps.push(2);
            this.backshift = 2;
        }

        if (key.equals("BR")) {

            this.color = new Color(0x00aa55);

            gap = "\n\n";
            out = "\\begin{" + preout + "}{}" + gap + "\\end{" + preout + "}";

            this.backshift = preout.length() + gap.length() + 7;

            this.attgaps.push(1);
        }


        if (key.equals("SY") || key.equals("F")) {

	if(key.equals("SY")) preout = "sym";

            this.color = new Color(0x00aa55);

            out = "\\" + preout +"{}{}";

            this.attgaps.push(1);
            this.attgaps.push(2);
            this.backshift = 3;
        }

        if (key.equals("SU")) {
            this.color = new Color(0x00aaaa);

            out = "\\" + preout+"{}{}{}{}";
             this.attgaps.push(1);
            this.attgaps.push(2);
            this.attgaps.push(2);
            this.attgaps.push(2);
            this.backshift = 7;
        }

        if (key.equals("T")|key.equals("TSTR")) {
	if(key.equals("TSTR")) preout = preout.substring(0,preout.length()-1)+"*";
            gap = "\n\n";
            out = "\\begin{" + preout + "}" + gap + "\\end{" + preout + "}";

            this.backshift = preout.length() + gap.length() + 6;
        }
	        return out;
    }
}
