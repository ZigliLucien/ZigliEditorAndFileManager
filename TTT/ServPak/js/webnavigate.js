	document.captureEvents(Event.KEYDOWN);
	document.onkeydown = goKey;

	var path = document.location.pathname;
	var cwd = path.substring(0,path.indexOf("WEB-XML"));
	var pcd = path.substring(path.indexOf("WEB-XML/")+8,path.indexOf("TextWriter.jav")-1);
	var wl = window.location.toString();
	wl = wl.substring(0,wl.indexOf("idx.htm"));
	var postcd = pcd;
	while(postcd.indexOf("/")>=0) postcd=postcd.replace("/",">");

	function goKey(e) {

	 var y = String.fromCharCode(e.which);

	if( y=="S") { 
			e.stopPropagation();
			e.preventDefault();
			window.location = "EdWeb.jav?GO";
	}

	if( y=="T") {
			e.stopPropagation();
			e.preventDefault();
	    	window.location = path.substring(0,path.indexOf("WEB-XML"))+"WEB-XML/idx.htm";
	}

	if( y=="U") {
			e.stopPropagation();
			e.preventDefault();
			cwd = path.substring(0,path.indexOf("idx.htm"));
			cwd = cwd.substring(0,cwd.lastIndexOf("/"));

	if(!cwd.match("WEB-XML$") && !path.match("jav$")) { 
			dirout = cwd.substring(0,cwd.lastIndexOf("/"))+"/idx.htm";
			window.location = dirout;	
		}
	}

	if( y=="B") {
			e.stopPropagation();
			e.preventDefault();
		    history.back();
	}

	if( y=="F") {
			e.stopPropagation();
			e.preventDefault();
		    history.forward();
	}
     }

	function toggle(e) {
	       if(e.style.display!="inline") show(e); else hide(e);
	}

	function show(e) {
	     e.style.display = "inline";
	}

	function hide(e) {
	     e.style.display = "none";
	}

	function newFile (form) {
	    var x = form.wrxtxr.value;	
  	    window.location= wl+"TextWriter.jav?wr@t@r="+x;
	}

	function updown(){}

	function getText(url, lbl){
		var req = new XMLHttpRequest();
try{
		req.onreadystatechange = 
	function(){
		if(req.readyState==4 && req.status==200)
			document.getElementById(lbl).innerHTML=req.responseText;
		}

		req.open("GET",url,true);
		req.send(null);
}catch(e){alert(e);}
	}

	function edit(url){
		window.location = url;
	}
