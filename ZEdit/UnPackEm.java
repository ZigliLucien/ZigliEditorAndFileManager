package ZEdit;

import com.sun.mail.util.*;
import java.io.*;

     public class UnPackEm{

	byte[] result;

	public UnPackEm(String filein, String fileout) {
try{
		BASE64DecoderStream bsd = new BASE64DecoderStream(new FileInputStream(filein));
		result  = new byte[bsd.available()];
		bsd.read(result);

		System.out.println("Unpacking "+filein);

		FileOutputStream fout = new FileOutputStream(fileout);
		fout.write(result);
		fout.flush();
		fout.close();

	}catch(Exception ee){
			System.out.println(ee.getMessage());
		}
	}
     }
