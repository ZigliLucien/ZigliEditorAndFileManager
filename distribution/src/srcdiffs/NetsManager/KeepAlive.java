package NetsManager;

import ZEdit.*;
import java.util.*;

import com.mysql.management.*;

    public class KeepAlive {
        java.util.Timer timer;
        

        public KeepAlive() {

	System.out.println("Starting MySQL KeepAlive");

            timer = new java.util.Timer();
            timer.scheduleAtFixedRate(new RemindTask(),
                           5400000,        //initial delay
                           5400000);  //subsequent rate
        }//constructor

        class RemindTask extends TimerTask {

            public void run() {
                if (ZEdit.DBStart.msR.isRunning()) {
                    System.out.println("KeepAlive MySQL at "+new Date().toString());
	        new ZEdit.DOps();
                } //end if
            }//end run
        }//RemindTask
    }
