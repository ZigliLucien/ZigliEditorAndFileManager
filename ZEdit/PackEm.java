package ZEdit;

import com.sun.mail.util.*;
import java.io.*;

     public class PackEm{

	byte[] result;

	public PackEm(String filein, String fileout) {
try{
		FileInputStream fins = new FileInputStream(filein);
		result  = new byte[fins.available()];
		fins.read(result);

		System.out.println("Packing "+filein);

		FileOutputStream fout = new FileOutputStream(fileout);
		BASE64EncoderStream bsd = new BASE64EncoderStream(fout);
		bsd.write(result);
		bsd.flush();
		bsd.close();

	}catch(Exception ee){}
	}
     }
