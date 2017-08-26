package ZEdit;

import NetsManager.*;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.text.*;
import javax.swing.text.html.*;

import calpa.html.*;

public class CHOLocal extends calpa.html.DefaultCalHTMLObserver{

	JTextField jtf;
	WebCP wcp;
	CalHTMLPane pane;

      public CHOLocal(JTextField _jtf, WebCP _wcp) {
         	super();
         	this.jtf = _jtf;
	this.wcp = _wcp;
	this.pane = wcp.viewer;
         }

  
 public   void  linkActivatedUpdate(CalHTMLPane p, URL url, String tf, String jn) { 

                        String proto = url.getProtocol();

                        if (proto.equals("http") || proto.equals("file")) {
             try { 
		           wcp.displayURL(url);	

	                } catch (Exception edu) {} 			           
                        } else {
                            WebCP.mm = wcp.Download(url);                     

		     return;
                    }
	}



      public void linkFocusedUpdate(CalHTMLPane p, URL url) {

	        WebCP.tempURL = url;

 	        jtf.setText((url == null) ? "" : url.toExternalForm());
      }

     public void formSubmitUpdate(CalHTMLPane p, URL url, int methd, String act, String dat){
	
		String urly = url.toString();
		String urly1 = urly.substring(urly.indexOf("http://")+7);
		           urly = "http://"+urly1.substring(0,urly1.indexOf("/"));		

		String localdat = ZEFMServer.converter(dat);

		String ldat = localdat.substring(localdat.indexOf("&")+1);
		           localdat = ldat.substring(0,ldat.indexOf("@!!@x="));

	        jtf.setText((dat == null) ? "" : urly+localdat);
	try{
		WebCP.currentURL = new URL(urly+localdat);
	     }catch(Exception urle){}

      }
 
  } // end CHOLocal