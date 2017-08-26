#!/usr/bin/perl

($x,$y)= split(/\./,$ARGV[0]);

$debug=1 if($ARGV[1] eq "d");
$debug2=1 if($ARGV[2]);
$debugifs=1 if ($ARGV[1] eq "f");

$outfile = $x.".jv";

open OUT,"> $outfile";

select OUT;

$classname = 0;
$classup = 0;

$infile = $ARGV[0];

open IN,$infile;

while(<IN>){
print "<-lp$lpcount"," ","mc$methodcount"," ","lpmc$lpmc"," ","lpm$lpmethod-> " if $debug;
chomp;

if(/:\s*$/){print;next;}

s/\s*(.*)/$1/;


if(/^\}\s*catch(.*)/) {
$lpcount--;
if($lpmethod) {$lpmc--;}
print "}//\n";
print "catch$1\n";
next;
}

if (/^$/) { print "\n"; next; }
if (/setActionCommand/ &&/\*\*/){print "$_ //ff\n";next;}
if ($debug2 && (/^for|^while|^try|^if|^else|^finally|^switch/) && (!/\{\s*$/)){print "CCHHEECCKK TTHHIIISS\n";}

### if-type statements on one line - short form without braces.

if($debugifs) {

if ( (/^for|^while|^try|^if|^else|^finally|^switch/) && (!/\{\s*$/)){

@line = split(/\)\s+/);
print "$line[0])",'{//',"\n";
$lnn = join ") ",@line[1..$#line];
print "$lnn \n";
print '}//',"\n";
next;
}

}

if ((/^for|^while|^try|^if|^else|^finally|^switch/) && (/\{\s*$/)) { s/\{/\{\/\//;print; print "\n";
$lpcount++;
if($lpmethod) {$lpmc++;}
next;}

if (/^for|^while|^try|^if|^else|^finally|^switch/)  { print; print "////\n";
next;}

if(/^\}\}\)\;/){print "}//end\n});\n"; $lpmethod=0;$lpmc=0; $methodcount--; next;}

if( ( /^\}\s*$/ ) && ( $lpcount==0 || ($lpmethod && ($lpmc==0)) )  ) { 
print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" if $debug;
if($methodcount>0) { 
$methodcount--;
$lpmethod=0;
s/\}/\}\/\/end/;
print; print "\n";
next;
            	   }
	}

if($lpcount>0 || ($lpmethod && $lpmc>0)  ) { 
if(/^\}\s*$/) {
$lpcount--; 
if($lpmethod) {$lpmc--;}
s/\}/\}\/\//;print; print "\n"; next;
}
if(/^\}\s*(else\s*\{)/) {print "}//\n"; print $1; print "//\n"; next;}
}

if (/class\s+(.*?)\s/) { print "// class //\n"; $classname = $1; print; print "\n"; $classup = 1;next;}
if(/$classname/ && $classup && /\w+\(.*\).*\{\s*$/ && !/\./) {print "// constructor //\n"; print; print "\n"; $methodcount++; next;}

if(/\w+\S*\s+\w+\(.*\).*\{\s*$/ && !/\./) {
print "// method //\n"; print; print "\n"; $methodcount++; 
$lpmethod=1;$lpmc=0;
next;}

if($lpcount==0 && $methodcount==0 && /^\}\s*$/) { 
s/\}/\}\/\//;
}

if(/^System\.out\.print/)  { print $_,"//-\n"; next;}

if(/^\/\*\*/ || /^\*/ || /^\/\*/ || /\/\// || /^catch/ || /^new/ || /\{\s*$/) { 
	print;print "\n";next;
	}


	if(/=/){
		print $_,"//ff\n";
	next;
	} else {
s/\;.*//;
 @y = split;
if($#y>0) {
	if($#y>1) {print $_,";/////\n" ;}
	else {print $_,";////\n" ; }
} else { print;print ";\n";
	next;
} }

}
