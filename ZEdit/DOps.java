package ZEdit;

import java.sql.*;
import java.io.*;
import java.util.zip.*;
import java.util.*;

public class DOps {

static ResultSet res;

public static Connection goMysql;

public DOps(){

try{

    Class.forName("com.mysql.jdbc.Driver");

  goMysql = DriverManager.getConnection(
	"jdbc:mysql://localhost:"+DBStart.dataport+"/ZEFMdb?characterEncoding=utf8","root", "");

}catch(Exception en){
		System.out.println(en.getMessage());
	}

	}
 
/////////////////// DOSAVE ///////////////////
	public static void doSave(Connection cnct, String filename, byte[] bits, String db) {
   try{

	ByteArrayOutputStream bout = new ByteArrayOutputStream();
	GZIPOutputStream gzout = new GZIPOutputStream(bout);

	gzout.write(bits);
	gzout.flush();
	gzout.close();

	byte[] jj = bout.toByteArray();

	goSave(cnct, filename, jj, db);

	}catch(Exception esave){
		System.out.println(esave.getMessage());
		new DOps();
	}

     }

////////////// GETFILE /////////////////
public static byte[] getFile(Connection cnct, String filename, String db) throws Exception {

	ResultSet rs = null;

   try{

	 String sql =    
		       "SELECT filename, data " + "FROM "+db+" WHERE filename=?";

          	            PreparedStatement stmt = cnct.prepareStatement(sql); 
		stmt.setString(1,filename);

	            rs = stmt.executeQuery();
		rs.next();	

           System.out.println("Retrieved "+rs.getString("filename")+" from db "+db);

    }catch( Exception e ) {      
		System.out.println(e.getMessage()); 
		new DOps();
	}

	return rs.getBytes("data");
  }

////////////// GOSAVE ///////////////
	public static void goSave(Connection cnct, String name, byte[] jj, String db) {

   try{

	 String sql =    (db.equals("main")) ?
			 "INSERT INTO "+db+"(filename,data,time) " +
			"VALUES(?,?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data), time=VALUES(time)" :
			 "INSERT INTO "+db+"(filename,data) " +
			"VALUES(?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data)";

 		PreparedStatement stmt = cnct.prepareStatement(sql); 
	               stmt.setString(1,name);
	               stmt.setBytes(2,jj);
		if(db.equals("main")) stmt.setLong(3,new File(name).lastModified());

		System.out.println("SAVING BYTES "+name+" to db "+db);

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){
		System.out.println(esave.getMessage());
		new DOps();
	}

     }

////////////// GOSAVETEXT ///////////////
	public static void goSaveText(Connection cnct, String name, String jj, String db) {

   try{

	 String sql =     "INSERT INTO "+db+"(filename,data) " +
			"VALUES(?,?)"+
			" ON DUPLICATE KEY UPDATE data=VALUES(data)";

          	            PreparedStatement stmt = cnct.prepareStatement(sql); 
		stmt.setString(1,name);
	            stmt.setString(2,jj);

		System.out.println("SAVING "+name+" to db "+db);

	            stmt.executeUpdate();
	            stmt.close();

	}catch(Exception esave){
		System.out.println(esave.getMessage());
		new DOps();
	}

     }

 /////////////// TEST IF KEY EXISTS /////////////////////

	static boolean testKey(Connection cnct, String name, String db){

   try{ 


	 String sql =    
		       "SELECT * FROM "+db+" WHERE filename=? ";

          	            PreparedStatement stmt = cnct.prepareStatement(sql); 
		stmt.setString(1, name);

	            res = stmt.executeQuery();

		return res.next();

    }catch( Exception e ) {
		System.out.println(e.getMessage());
		new DOps();
	}
	
	return false;

	}

   public static void stopMySQL() {
        if (DBStart.msR != null) {
            DBStart.msR.shutdown();
        }
        DBStart.msR = null;
    }
}
