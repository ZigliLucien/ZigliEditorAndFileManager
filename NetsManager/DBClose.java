package NetsManager;

import java.io.*;
import com.mysql.management.*;
import ZEdit.*;

 class DBClose{

	public static void main(String[] args){

  	   System.out.println("Exiting");
	   File baseDir = new File(System.getProperty("user.dir"),"mysql");
	   MysqldResource msR = new MysqldResource(baseDir);
  	   String threadName = "ZEFM-MySQL";
	if(msR.isRunning()) msR.shutdown();	   

		}
	}