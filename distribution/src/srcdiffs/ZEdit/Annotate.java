package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.text.html.*;

import java.sql.*;


public class Annotate {

    String link;
    String fileName;
    boolean ifold;

     Connection conn;

    public Annotate(String word, String _fileName) throws EmptyStackException {

        try {

       	conn = DOps.goMysql;

            this.fileName = _fileName;

	link = NetsManager.XCommands.hexml(word);

	ifold = testKey(fileName, word.trim().replaceAll("'","\\\\'"));

            QuickEditor qed = 
		new QuickEditor(fileName, "Annotating " + word + " in " + _fileName, ifold, word, link);

        } catch (Exception exaux) {
		System.out.println("ANNOTATING "+exaux.getMessage());
        } finally {
            return;
        }
    }

  /////////////// TEST IF KEY EXISTS /////////////////////

	boolean testKey(String _name, String _word){

   try{ 
              String sql =
		"SELECT filename FROM notes WHERE filename=? AND word like ?";

		PreparedStatement ps = conn.prepareStatement(sql);
		ps.setString(1,_name);
		ps.setString(2,_word);
		ResultSet rs = ps.executeQuery();

	return rs.next();

    }catch( Exception e ) {
		System.out.println(e.getMessage());
	}
	
	return false;

	}
}
