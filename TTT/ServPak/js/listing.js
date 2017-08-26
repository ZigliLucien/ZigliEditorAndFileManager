var counter;
	var globl;

	indices = new Array("V","C","M","D","E","Q","N");
	procs   = new Array("VVV","CCC","MMM","XXX","EEE","QQQ","AAA");	

function setup(){ 

startTime();

for (i=7;i<document.overall.elements.length;i++){
	local = document.overall.elements[i];

	local.addEventListener("mousedown", goMouse,true);
	local.addEventListener("keyup", bKey,true);
	}

	document.getElementById("W")
	.addEventListener("mousedown", W, true);

	document.getElementById("F")
	.addEventListener("mousedown", F, true);

	document.getElementById("S")
	.addEventListener("mousedown", S, true);

	document.getElementById("DB")
	.addEventListener("mousedown", DB, true);
    }

    document.captureEvents(Event.KEYDOWN);      
    document.onkeydown = goKey; 


	function W(){ x=prompt('New File Name'); newFile(x);  }
	function F(){ x=prompt('Enter string in filename to search'); findFile(x); }
	function DB(){ 
		var y = document.cookie;
		if(document.cookie.indexOf(";")>0)  y = y.substring(0,y.indexOf(";"));
		x=prompt('Enter string to search in texts', y); 
		document.cookie = x;
		searchDB(x); 
	}

	function S(){ 
		var y = document.cookie;
		if(document.cookie.indexOf(";")>0)  y = y.substring(0,y.indexOf(";"));
		x=prompt('Enter string to search', y); 
		document.cookie = x;
		searchString(x); 
	}

	function loc(x) { 
		window.location = x; 
	}

	function goMouse(e){

		var  x = document.overall.id+"/"+ this.value;
		var y = e.button;

	         if(y==0) loc(x); 
	         if(y==2) loc2(x,y); 

	}

		function loc2(x,y){
var which;
var local;

for (i=0;i<7;i++){
	local = document.overall.elements[i];
	if(local.type.indexOf("radio")>-1 && local.checked){
	which = local.value;
		}
	}

	 window.location = "FileOps.jav?fileops="+which+"&"+x+"@!!@x="+y;
	}

	function goKey(e) {
	
		var act;
		var len = document.overall.elements.length;
		var y = String.fromCharCode(e.which);


	if(counter==null) counter = 6;	
                       
	 if(e.which==0x28){
		if(counter<len-1) {
		counter += 1;
	} else {
		counter = 7;
	}
		document.overall.elements[counter].focus();
	}
	 if(e.which==0x26){
		 if(counter>7) {
		counter -=1;
	} else {
		counter = len-1;
	}
		document.overall.elements[counter].focus();
	}

	 if( e.which==0x70) {
			e.stopPropagation();
			e.preventDefault();
			window.location = document.overall.id+"?update";
			return;
		}

	if( y=="U") {
			e.stopPropagation();
			e.preventDefault();
			var wl = window.location.toString();
			var dirout = wl.substring(0,wl.lastIndexOf("/"));
			window.location = dirout;	
	}


	 if( e.which==0x73) {
			e.stopPropagation();
			e.preventDefault();
			history.back();
			return;
		}
	 if( e.which==0x74) {
			e.stopPropagation();
			e.preventDefault();
			document.forms[0].submit();
			return;
		}

	 if( e.which==0x71) {
			e.stopPropagation();
			e.preventDefault();
 	 if(window.location.toString().indexOf("?")>-1 ){ 
		var cut = window.location.toString().indexOf("?");
		window.location =   window.location.toString().slice(0,cut)+"?home";
		return;
	          }
	 	window.location = window.location+"?home";
		return;
	}

		
	if(e.which==0x47) window.location="http://www.google.com";

	if(y=="W") {  W(); globl = true; return; }
	if(y=="S") {  S();  globl = true; return; }
	if(y=="F") {  F();  globl = true; return; }
	if(y=="T") { DB();  globl = true; return; }

	for (i=0;i<7;i++){
		 if( y==indices[i]) act = procs[i];
	}

	for (i=0;i<7;i++){
		local = document.overall.elements[i];
	if(local.type.indexOf("radio")>-1 && local.value==act){
		local.checked = true;
		}
	}
     }

	function bKey(e) { 

		var x = this.value;
		var y = e.which;

		x = document.overall.id+"/"+x;

		if(y==0x27 || y==0x0d) loc(x); 
		if( (y==0xc0 || y==0xbe || y==0x0) && !globl) loc2(x,2); 

		globl = false;
	}


           function searchString(x) {
	if(x==null || x.length==0) { return; }
	loc("Webgrep.jav?webgrep="+x+"&"+document.overall.id+"=SearchString");
	}
           function searchDB(x) {
	if(x==null || x.length==0) { return; }
	loc("Search.jav?words="+x+"&SEARCH=GO");
	}
           function findFile(x) {
	if(x==null || x.length==0) { return; }
	loc("Webgrep.jav?webgrep="+x+"&"+document.overall.id+"=FindFile");
	}
           function newFile(x) {
	if(x==null || x.length==0) { return; }
	loc(document.overall.id+"?NNN="+x);
	}

function startTime()
{

var d = new Date();
var mth = new Array(12);
mth[0]="January";
mth[1]="February";
mth[2]="March";
mth[3]="April";
mth[4]="May";
mth[5]="June";
mth[6]="July";
mth[7]="August";
mth[8]="September";
mth[9]="October";
mth[10]="November";
mth[11]="December";
var dd = mth[d.getMonth()]+" "+d.getDate().toString();

var h=d.getHours()
var m=d.getMinutes()
var s = d.getSeconds()
// add a zero in front of numbers<10
m=checkTime(m)
s=checkTime(s)
if(h==0) h='00';

document.getElementById('time').innerHTML='<i>'+dd+'</i><br/><i>'+h+':'+m+':'+s+'</i>'
t=setTimeout('startTime()',500)
}

function checkTime(i)
{
if (i<10) 
  {i="0" + i}
  return i
}