/* Diary - Decompiled by JODE
 * Visit http://jode.sourceforge.net/
 */
package ServPak.jv;

public class Diary {
    public String printout;

    public Diary(String string) {
        String _in = string;
        String _rhs = _in.substring(_in.indexOf("=") + 1);
        String _lhs = _in.substring(0, _in.indexOf("="));
        int i = _lhs.indexOf("+");
        String _day = _lhs.substring(0, i);
        String _user = _lhs.substring(i + 1);
        StringBuilder stringbuffer = new StringBuilder();

        stringbuffer.append("<html>\n");
        stringbuffer.append("  <head>\n");
        stringbuffer.append("    <title> DIARY ENTRY</title>\n");
        stringbuffer.append("  </head>\n");
        stringbuffer.append("\n");
        stringbuffer.append("  <body>  \n");
        stringbuffer.append("\n");
        stringbuffer.append(" <H1>Diary Entry</H1>\n");
        stringbuffer.append(" <P>\n");
        stringbuffer.append("\n");
        stringbuffer.append("     <form action=\"DiaryOut.jav\" method=post>\n");
        stringbuffer.append("\n");
        stringbuffer.append("<b>" + _user +
            ", enter the appointment information for " + _day + " " +
            _rhs + ". </b>  <p>\n");
        stringbuffer.append("<input  name=\"" + _day + " " + _rhs +
            " " + _user + "\" size=50> \n");
        stringbuffer.append("      <P>\n");
        stringbuffer.append(
            "  <input type=submit name=Entry value=\"Add This Data to a Diary File\">\n");
        stringbuffer.append("\n");
        stringbuffer.append("<P>\n");
        stringbuffer.append("\n");
        stringbuffer.append("</form>\n");
        stringbuffer.append("\n");
        stringbuffer.append("</BODY>\n");
        stringbuffer.append("</HTML>\n");
        printout = stringbuffer.toString();
    }
}
