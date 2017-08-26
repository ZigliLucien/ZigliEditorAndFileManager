package ZEdit;

import NetsManager.ZEFMServer;
import java.io.*;
import java.sql.*;
import java.util.*;

import com.mysql.management.*;

public class DBStart {

            Connection con;
            Statement stmt;
            public static MysqldResource msR;
	public static int dataport;

            public static boolean DBChecked;

public static void main(String[] qubits) { 
try{
		new DBStart(); 

}catch (Exception edb){}
	}

  	public DBStart(){ 

    try {

 	dataport = 60000 + (int) Math.round(5000 * Math.random());

	String zefmDir = System.getProperty("user.dir");

       File baseDir = new File(zefmDir,"mysql");
	    msR = new MysqldResource(baseDir);

	if(msR.isRunning()) msR.shutdown();

	if(!msR.isRunning()){
   	      Map options = new HashMap();
		options.put("port", new Integer(dataport).toString());
		String threadName = "ZEFM-MySQL";
		msR.start(threadName, options);
}
         Class.forName("com.mysql.jdbc.Driver");

        con = DriverManager.getConnection("jdbc:mysql://localhost:"+dataport+"/","root", "");

      System.out.println("Connection: " + con+" successful");

       stmt = con.createStatement();

       stmt.executeUpdate("CREATE DATABASE IF NOT EXISTS ZEFMdb default character set utf8");

       stmt.executeUpdate("use ZEFMdb");

      stmt.executeUpdate(
     "CREATE TABLE IF NOT EXISTS annotations(filename varchar(255) NOT NULL,"+
     "data text NOT NULL,"+
     "PRIMARY KEY (filename))"
			);
      stmt.executeUpdate(
     "CREATE TABLE IF NOT EXISTS tmpZefm(filename varchar(255) NOT NULL,"+
     "data mediumblob NOT NULL,"+
     "PRIMARY KEY (filename))"
			);

      stmt.executeUpdate(
     "CREATE TABLE IF NOT EXISTS sentMail(filename varchar(255) NOT NULL,"+
     "data text NOT NULL,"+
     "towhom tinytext NOT NULL,"+
     "subject tinytext NOT NULL,"+
     "date tinytext NOT NULL,"+
     "time bigint NOT NULL,"+
     "PRIMARY KEY (filename))"
			);

      stmt.executeUpdate(
     "CREATE TABLE IF NOT EXISTS listings(filename varchar(255) NOT NULL,"+
     "data mediumtext NOT NULL,"+
     "PRIMARY KEY (filename))"
			);

     stmt.executeUpdate(
     "CREATE TABLE IF NOT EXISTS xml(filename varchar(255) NOT NULL,"+
     "time bigint NOT NULL,"+
     "data mediumblob NOT NULL,"+
     "PRIMARY KEY (filename))"
			);

   stmt.executeUpdate(
"CREATE TABLE IF NOT EXISTS notes(filename varchar(255) NOT NULL,"+
"word varchar(80) NOT NULL,"+
"link varchar(80) NOT NULL,"+
"data blob, KEY(filename), KEY(word))"
			);

   stmt.executeUpdate(
"CREATE TABLE IF NOT EXISTS dictionaries(lang varchar(255) NOT NULL,"+ 
"word varchar(80) NOT NULL,"+
"data blob, KEY(lang), KEY(word))"
			);

   stmt.executeUpdate(
"CREATE TABLE IF NOT EXISTS main(filename varchar(255) NOT NULL,"+
"time bigint NOT NULL,"+
"data mediumblob NOT NULL,"+
"PRIMARY KEY (filename))"
			);

   stmt.executeUpdate(
"CREATE TABLE IF NOT EXISTS texts(filename varchar(255) NOT NULL,"+
"data mediumtext NOT NULL,"+
"PRIMARY KEY (filename))"
			);


               con.close();
	 DBChecked = true;	
               System.out.println("Connection: " + con+" concluded: "+DBChecked);

	new DOps();

      }catch( Exception e ) {
      System.out.println(e.getMessage());
    }
  }
}
