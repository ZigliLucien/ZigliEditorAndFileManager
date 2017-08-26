package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;


public class MailRun extends TPEditorX implements ActionListener {
    static String user;
    static String usertext;
    static String mailserver;
    static String password;
    static Properties mailinfo;
    public String results;
    JTextField userfield;
    JTextField mailserverfield;
    JTextField passwordfield;
    JFrame jff;
    JTextArea jat;
    int locx;
    int locy;
    boolean isWeb;

    public MailRun(String incmd) throws Exception {
        this(incmd, false);
    }

    public MailRun(String incmd, boolean _isWeb) throws Exception {
        results = "";
        isWeb = _isWeb;

        if (!isWeb) {
            jff = new JFrame("Mail Results");
            jat = new JTextArea(10, 45);
            jff.getContentPane().add(jat);
            jff.pack();

            Dimension scrsize = Toolkit.getDefaultToolkit().getScreenSize();

            locx = (scrsize.width) / 5;
            locy = (scrsize.height) / 2;
            jff.setLocation(locx, locy);
        }

        mailinfo = new Properties();

        InputStream fin = new FileInputStream("GetMail.properties");
        mailinfo.load(fin);

        if (!new File("INBOXES").isDirectory()) {
            new File("INBOXES").mkdir();
        }

        if (!isWeb && incmd.equals("Get Mail")) {
            userfield = new JTextField(usertext, 12);
            mailserverfield = new JTextField(mailserver, 15);
            passwordfield = new JPasswordField(password, 10);

            JPanel info = new JPanel();
            info.setLayout(new GridLayout(2, 3));
            info.add(new JLabel("User:"));
            info.add(new JLabel("MailServer:"));
            info.add(new JLabel("Password:"));
            info.add(userfield);
            info.add(mailserverfield);
            info.add(passwordfield);

            dialog = new QuickDialog(this, "Mail Run", info, "Get Mail");

            userfield.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent e) {
                        getMail(userfield.getText(), mailserverfield.getText(),
                            passwordfield.getText());
                    }
                });
        } else {
            try {
                user = incmd;

                String data = mailinfo.getProperty(user);
                String data2 = data.substring(data.indexOf(",") + 1);
                usertext = data.substring(0, data.indexOf(","));
                mailserver = data2.substring(0, data2.indexOf(","));
                password = data2.substring(data2.indexOf(",") + 1);

                if (!new File("INBOXES/" + user).isDirectory()) {
                    new File("INBOXES/" + user).mkdir();
                }

                new File("INBOXES/" + user + "/" + user + ".mail").delete();

                Thread t = new Thread() {
                        public void run() {
                            try {
                                new MClient(new String[] {
                                        usertext, mailserver, password
                                    });
                            } catch (Exception e) {
                            } finally {
                                try {
                                    results = MailRun.cleanup();
                                } catch (Exception e) {
                                }
                            }
                        }

                        //run
                    };

                //thread
                t.start();
                t.join();

                if (!isWeb) {
                    jat.setText(results);
                }
            } catch (Exception exc) {
                System.out.println(exc.getMessage());
            } finally {
                if (!isWeb) {
                    jff.setVisible(true);
                }
            }

            return;
        }
    }

    public void actionPerformed(ActionEvent e) {
        String cmd = e.getActionCommand();

        if (cmd.equals("Get Mail")) {
            getMail(userfield.getText(), mailserverfield.getText(),
                passwordfield.getText());
        }
    }

    ////////////////////////////////////////////////////////
    ////////////////// GET MAIL ////////////////////////////
    ////////////////////////////////////////////////////////
    void getMail(String usertxt, String mailsrvr, String passwd) {
        JFrame jmail = null;

        dialog.dispose();
        jmail = new JFrame("Getting mail ...");

        JLabel jl = new JLabel("Getting mail. Please wait.");
        JPanel jpl = new JPanel();
        jpl.add(jl);
        jmail.getContentPane().add(jpl);
        jmail.pack();
        jmail.setLocation(locx, locy);
        jmail.setVisible(true);

        usertext = usertxt;
        mailserver = mailsrvr;
        password = passwd;
        user = usertext;

        if (user.indexOf("@") >= 0) {
            user = user.substring(0, user.indexOf("@"));
        }

        if (!new File("INBOXES/" + user).isDirectory()) {
            new File("INBOXES/" + user).mkdir();
        }

        new File("INBOXES/" + user + "/" + user + ".mail").delete();

        try {
            Thread t = new Thread() {
                    public void run() {
                        try {
                            new MClient(new String[] {
                                    usertext, mailserver, password
                                });
                        } catch (Exception e) {
                        } finally {
                            try {
                                results = MailRun.cleanup();
                            } catch (Exception e) {
                            }
                        }
                    }

                    //run
                };

            //thread
            t.start();
            t.join();

            jat.setText(results);
        } catch (Exception exc) {
            System.out.println(exc.getMessage());
        } finally {
            dialog.dispose();
            jmail.dispose();
            jff.setVisible(true);
        }
    }

    public static String cleanup() throws Exception {
        String result = "";

        if (new File(MClient.logfile).exists() || password.equals("local")) {
            if (!password.equals("local")) {
                result = MClient.logfile + " shows " + MClient.nummessages +
                    " available.\n";
            }

            if (!mailinfo.containsKey(user)) {
                mailinfo.setProperty(user,
                    usertext + "," + mailserver + "," + password);

                FileOutputStream flt = new FileOutputStream(
                        "GetMail.properties");
                mailinfo.store(flt, "Mail Info");
                flt.close();
            }
        }

        File outfile = new File(MClient.fileout);

        if (outfile.exists() && (outfile.length() > 4)) {
            new MailFiles(MClient.fileout, user);

            String localhost = InetAddress.getLocalHost().getHostName();

            if (localhost.indexOf(".") >= 0) {
                localhost = localhost.substring(0, localhost.indexOf("."));
            }

            result += ("Check the INBOXES/" + user +
            " directory \n for your messages.");
        } else {
            if (MClient.nummessages == 0) {
                if (outfile.delete()) {
                    result += " Looks like no new mail.";
                }
            } else {
                result += " Check your mail file.";
            }
        }

        return result;
    }
}
