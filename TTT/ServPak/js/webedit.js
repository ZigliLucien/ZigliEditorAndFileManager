  document.captureEvents(Event.KEYDOWN);      
    document.onkeydown = goKey; 

	function goKey(e) {

	 var y = String.fromCharCode(e.which);

	 if( e.which==0x73) {
			e.stopPropagation();
			e.preventDefault();
			history.back();
	}

	 if( e.which==0x70) {
			e.stopPropagation();
			e.preventDefault();
			getText(document.forms[0],'q');
	}
	 if( e.which==0x71) {
			e.stopPropagation();
			e.preventDefault();
			getText(document.forms[0],'p');
	}
	 if( e.which==0x72) {
			e.stopPropagation();
			e.preventDefault();
			getText(document.forms[0],'t');
	}

	if( y=="S" && e.ctrlKey) { 
			e.stopPropagation();
			e.preventDefault();
			window.location = "EdWeb.jav?GO";
	}

	if( y=="R" && e.ctrlKey) { 
			e.stopPropagation();
			e.preventDefault();
			window.location.reload(true);
	}

	if( y=="N" && e.ctrlKey) {
			e.stopPropagation();
			e.preventDefault();
			var newloc = pcd+"/";
			x=prompt('New File',newloc); 
	if(x!=null)    	window.location= wl+"TextWriter.jav?wr@t@r="+escape(x);
	}

	if( y=="D" && e.ctrlKey) {
			e.stopPropagation();
			e.preventDefault();
			window.location = "idx.htm";
	}

	if( y=="I" && e.ctrlKey) {
			e.preventDefault();
			e.stopPropagation();
			x=prompt('Wikipedia Search'); 
	if(x!=null) window.location= "http://en.wikipedia.org/wiki/"+escape(x) ;
	}
	if( y=="W" && e.ctrlKey) {
			e.preventDefault();
			e.stopPropagation();
			x=prompt('Wiktionary Search'); 
	if(x!=null) window.location= "http://en.wikipedia.org/wiki/"+escape(x) ;
	}

     }
	
function setup(){ 
	document.getElementById("T")
	.addEventListener("mousedown", T, true);

	document.getElementById("M")
	.addEventListener("mousedown", M, true);

	document.getElementById("AM")
	.addEventListener("mousedown", AM, true);
    }

	var path = document.location.pathname;
	var cwd = path.substring(0,path.indexOf("WEB-XML"));
	var pcd = path.substring(path.indexOf("WEB-XML/")+8,path.indexOf("TextWriter.jav")-1);
	var wl = window.location.toString();
	wl = wl.substring(0,wl.indexOf("TextWriter.jav?"));
	var postcd = pcd;
	while(postcd.indexOf("/")>=0) postcd=postcd.replace("/",">");

	function T(e){ 
			var z = e.button; 


		if(z==2) {
	t = window.open(cwd+"WEB-XML/Symbols.html", 'Symbols', 
	     'height=600,width=200,status=no,menubar=no,scrollbars=yes');
	t.moveTo(735,67);
	t.focus();
		}
	}


	function M(e){ 
			var z = e.button;

		if(z==0) {
	t = window.open(cwd+"WEB-XML/TPMLShortMarkup.html", 'ShortMarkup', 
	     'height=500,width=700,status=no,menubar=no,scrollbars=yes');
	t.moveBy(50,50);
	t.focus();
		}
	}

	function AM(e){ 
			var z = e.button;

		if(z==0) {
	t = window.open(cwd+"WEB-XML/ASCIIMath.html", 'ASCIIMath', 
	     'height=380,width=700,status=no,menubar=no,scrollbars=no');
	t.moveBy(700,10);
	t.focus();
		}
	}
 
	function goWP (form,str) {

	if(str='w') {
	  	  var x = form.inputbox.value;
	  	  window.location= "http://en.wikipedia.org/wiki/"+escape(x) ;
	}
	if(str=='d') {
	           	            var x = form.wordbox.value;
			window.location= "http://en.wiktionary.org/wiki/"+escape(x) ;
		}
	}

	function getText (form, str) {
	    var x = form.pxgx.value;	
	var modifier = "";
	if(str=="t") modifier = "&t@xt@l";
	if(str=="q") modifier = "&q@ks@v"; 
	window.location= wl+"TextWriter.jav?n@m@="+pcd+"&p@g@="+escape(x)+modifier;
	}

	function newFile (form) {
	    var x = form.wrxtxr.value;	
  	    window.location= wl+"TextWriter.jav?wr@t@r="+x;
	}
