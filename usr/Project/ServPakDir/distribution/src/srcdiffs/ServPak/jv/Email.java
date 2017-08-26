package ServPak.jv;

import ZEdit.*;


public class Email {
    public String printout;
    ZEdit.MailRun morri;

    public Email(String yuser) throws Exception {
        try {
            morri = new ZEdit.MailRun(yuser, true);
        } catch (Exception e) {
        } finally {
            String directory = NetsManager.ZEFMServer.userdir + "/INBOXES/" +
                yuser;

            StringBuilder bufi = new StringBuilder("<html><body><p><p><a href=\"" +
                    directory + "\"> To MAIL </a>");

            if (morri.results != null) {
                bufi.append("<p/>" + morri.results +
                    "The link above will take you there.<p/>");
            } else {
                bufi.append("<p/> Check your mail. <p/>");
            }

            bufi.append(
                "<p/> <a href=mail.html> Back to Mail List </a>\n</body></html>");
            printout = bufi.toString();
        }
    }
}
