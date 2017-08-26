
    document.captureEvents(Event.KEYDOWN);      
    document.onkeydown = goKey; 

	function goKey(e) {

	 var y = String.fromCharCode(e.which);

	if( y=="N") { 
			e.stopPropagation();
			e.preventDefault();
		wh = 	document.forms[0].elements['NEXT'].name;
		window.location= 'MKcal.jav?'+escape(wh)+'=NEXT';
	}

	if( y=="B") { 
			e.stopPropagation();
			e.preventDefault();
		wh = 	document.forms[0].elements['BACK'].name;
		window.location= 'MKcal.jav?'+escape(wh)+'=BACK';
	}

	 if( e.which==0x73) {
			e.stopPropagation();
			e.preventDefault();
		 history.back();
	}

	 if( e.which==0x74) {
			e.stopPropagation();
			e.preventDefault();
		document.forms[0].submit();
	}


	 if( e.which==0x71) {
			e.stopPropagation();
			e.preventDefault();
	 if(window.location.toString().slice(-7) == "?update" ) {
	  window.location =   window.location.toString().slice(0,-7)+"?home";
	  return;
	}

	 if(window.location.toString().slice(-5) == "?home" ) { 
			window.location.reload();
		} else {
		 	window.location = window.location+"?home";
		}
	}
     }
