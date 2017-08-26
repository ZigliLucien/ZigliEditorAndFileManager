import com.sun.javadoc.*;

import java.io.*;


public class Jvmaker {
    static FileOutputStream fout;

    public static boolean start(RootDoc root) throws Exception {
        ClassDoc[] classes = root.classes();

        for (int i = 0; i < classes.length; ++i) {
            ClassDoc cd = classes[i];

            StringBuffer bufi = new StringBuffer(
                    "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/plain\" href=\"ServPak/xsl/javadox.xsl\"?>");

            bufi.append("\n\n<jdox>\n\n");

            bufi.append("<package>" + cd.containingPackage() + "</package>\n");

            PackageDoc[] pkg = cd.importedPackages();

            for (int j = 0; j < pkg.length; j++) {
                bufi.append("<importpkg>" + pkg[j] + "</importpkg>\n");
            }

            ClassDoc[] cls = cd.importedClasses();

            for (int j = 0; j < cls.length; j++) {
                bufi.append("<import>" + cls[j] + "</import>\n");
            }

            bufi.append("<class>\n");
            bufi.append("<modifiers>" + cd.modifiers() + " </modifiers>");
            bufi.append("<name>" + cd.name() + "</name>\n");
            bufi.append("<superclass>" + cd.superclass() + "</superclass>\n");

            ClassDoc[] ifs = cd.interfaces();

            bufi.append("\n<interfaces>");

            if (ifs.length > 0) {
                bufi.append(" implements " + ifs[0]);
            }

            if (ifs.length > 1) {
                for (int j = 1; j < ifs.length; j++) {
                    bufi.append(", " + ifs[j]);
                }
            }

            bufi.append("</interfaces>\n");

            bufi.append("<classname>" + cd + "</classname>\n");
            bufi.append("<author></author>\n");
            bufi.append("<version></version>\n");
            bufi.append("<comment></comment>\n");
            bufi.append("</class>\n");

            ConstructorDoc[] cstrs = cd.constructors();

            for (int j = 0; j < cstrs.length; j++) {
                Parameter[] peri = cstrs[j].parameters();
                String arglist = "";

                if (peri.length > 0) {
                    arglist = peri[0].toString();

                    for (int q = 1; q < peri.length; q++) {
                        arglist += (", " + peri[q].toString());
                    }
                }

                bufi.append("<constructor>");
                bufi.append("<modifiers>" + cstrs[j].modifiers() +
                    " </modifiers>");
                bufi.append("<name>" + cstrs[j].name() + "(" + arglist +
                    ")</name>");
                bufi.append("<comment></comment>\n");
                bufi.append("</constructor>\n");
            }

            FieldDoc[] flds = cd.fields();

            for (int j = 0; j < flds.length; j++) {
                bufi.append("<field>");
                bufi.append("<modifiers>" + flds[j].modifiers() +
                    " </modifiers>");
                bufi.append("<type>" + flds[j].type().toString() + " </type>");
                bufi.append("<name>" + flds[j].name() + "</name>");
                bufi.append("<comment></comment>\n");
                bufi.append("</field>\n");
            }

            MethodDoc[] mds = cd.methods();

            for (int j = 0; j < mds.length; j++) {
                Parameter[] peri = mds[j].parameters();
                String arglist = "";

                if (peri.length > 0) {
                    arglist = peri[0].toString();

                    for (int q = 1; q < peri.length; q++) {
                        arglist += (", " + peri[q].toString());
                    }
                }

                bufi.append("<method>");
                bufi.append("<modifiers>" + mds[j].modifiers() +
                    " </modifiers>");
                bufi.append("<type>" + mds[j].returnType().toString() +
                    " </type>");
                bufi.append(" <name>" + mds[j].name() + "(" + arglist +
                    ")</name>\n");
                bufi.append("<comment></comment>\n");
                bufi.append("</method>\n\n");
            }

            bufi.append("</jdox>");

            fout = new FileOutputStream(classes[i] + ".xml");
            fout.write(bufi.toString().getBytes());
            fout.flush();
            fout.close();
        }

        return true;
    }
}
