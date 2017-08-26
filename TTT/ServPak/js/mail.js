  document.captureEvents(Event.KEYDOWN);      
    document.onkeydown = goKey; 

	function goKey(e) {

	 var y = String.fromCharCode(e.which);

	 if( e.which==0x70) {
			e.stopPropagation();
			e.preventDefault();
			getText(document.forms[0]);
	}
     }


	var wl = window.location.toString();
	wl = wl.substring(0,wl.indexOf("SendEmail.jav?"));

	function getText (f1) {
	    var x1 = f1.toWhom.value;	
	    var x2 = f1.towhom.value;	
	    var x3 = f1.subject.value;	
	    var x4 = f1.mlxx.value;	
	    var x5 = f1.attachment.value;	
	    window.location= wl+"SendEmail.jav?"
   	 +"toWhom="+escape(x1)+"&towhom="+escape(x2)+"&subject="+escape(x3)
	 +"&mlxx="+escape(x4)+"&attachment="+escape(x5)+;
	}

