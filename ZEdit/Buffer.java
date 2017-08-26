package ZEdit;

import java.awt.*;
import java.awt.event.*;

import java.io.*;

import java.net.*;

import java.util.*;

import javax.swing.*;
import javax.swing.event.*;


public class Buffer extends TPEditorX {
    // Class 
    String filename;
    public static boolean empty;

    public Buffer() throws Exception {
        //Constructor	

	super("New Buffer");

        ZEditor.initializing = false;

        outname = "";

        empty = false;

	chooseFile(this.dir, true);
	
	outname = filechosen;

        if (outname.equals("No File Selected")) {
            empty = true;
        }

        this.currentfile = outname;

        this.filename = outname;
        this.cmd = "Open";
        this.callPage(outname);
    }
}
