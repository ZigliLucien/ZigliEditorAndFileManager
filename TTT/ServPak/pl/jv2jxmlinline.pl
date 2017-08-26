#!/usr/bin/perl

$prefilename = shift;

open IN,$prefilename;

($filename,$ext) = split(/\./,$prefilename);

print '<?xml version="1.0"?>
<?xml-stylesheet type="text/plain" href="ServPak/xsl/javahtml.xsl"?>
<!DOCTYPE java [<!ENTITY % javawords SYSTEM "file:ServPak/xsl/javawords"> %javawords;]>
<java>
';

while(<IN>){

chomp;

s/\s*(.*)/$1/;

unless(/^for|^while|^try|^if|^else/){
s/</&lt;/g;
s/>/&gt;/g;
s/\"/&#x22\;/g;
}

s/\;\"/XXX/g;


if(/^new/){
s/new\s*(\w+)\b/<ff>new<\/ff> <b>$1<\/b>/g;
print;
print "<br/>\n";
next;

}

if(/^package\s+(.*)\;/){

print "<package> $1 </package><br/>\n";
next;
}

if(/:\s*$/) { print "<p/>";print; print "<br/>\n";next;}

if(/catch/){
s/\s*catch\s*\((.*?)\)\s*\{(.*)\}/<catch exc=\"$1\">$2<\/catch>/;
print; print "<br/>\n";next;
}

# COMMENTING

##### comments
if(/^\/\*\*\s*(.*)/) { 
$doccommentflag = 1; $commentflag=1;
if($classflag){
print "\n<br/><doccomment>\n<commentline>$1</commentline>\n"; 
} else {
print "\n<br/><doccomment auth=\"y\">\n<commentline>$1</commentline>\n"; 
}
next;}

if(/^\/\*\s*(.*)/) { 
$commentflag = 1;
print "\n<br/><comment>\n<commentline>$1</commentline>\n"; 
next;}

if($commentflag && /^\*\//) {
if($doccommentflag){ print "</doccomment>\n"; $doccommentflag=0;
}else{
print "</comment>\n"; 
}
$commentflag=0;
next;
} 

if($commentflag && /^\*\s*(.*)/) {print "<commentline>$1</commentline>\n";next;} 

######

unless(/\/\// || $typeflag || $parenflag || $commentflag ||/^\*/){
 $_ = &methodcall($_);

print "\n";
print;

next;
}


# DECLARATIONS

if(/^\/\/\//){ print "<p><pre>\n";print;print "</pre></p>\n";next;}

if(/(.*)\/\/-/){

$_ = "\n".$1."<br/>";

}

if(/(.*)\/\/c/){

$_ = " ".$1;

}




if(/^\/\/=-\s*(.*)\s*/){

print "\n<",$1,">"; next;

}


# TAG MODE

if(/^\}\s*\/\/\s*end/){

$tag = pop @tagstack;

print "</$tag>\n";

$tag = pop @tagstack;

print "</$tag>\n<p/>"; next;
}

if(/^\}\s*\/\//){

$parenflag = 0;

$tag = pop @tagstack;

print "</$tag><br/>"; next;
}


# END TAG MODE
#################

# TYPE DECLARE

if(/^\/\/\s*(.*)\s*\/\//){

$typeflag = 1;
$type = $1;

next;
}

if( $typeflag && $type =~/class/) {
$classflag = 1;
s/\bclass\b/=/;

$typeflag = 0;

($presc,@rest)=split(/\s+|{/);

if($presc eq "=") {
$presc="";
} else {
shift @rest;
}

$name =  shift @rest; 

$desc = join " ",@rest;

push @tagstack,"class";

%declare = ("presc",$presc,"name",$name,"desc",$desc);

$out = "\n\n<class";

&attributes;

print "$out>";

next;
}

if( $typeflag && $type =~/constructor/) {

$typeflag = 0;

($pre,$args,@rest)=split(/\(|\)|{/);
@pres = split(/\s+/,$pre);
$name = pop @pres;

$presc = join " ",@pres;

push @tagstack,"constructor";

$desc = join " ",@rest;

%declare = ("presc",$presc,"desc",$desc);

$out = "\n\n<constructor";

&attributes;

print "$out>
<args>$args</args>
<exec>
";

push @tagstack,"exec";

next;
}

if( $typeflag && $type =~/method/) {

$typeflag = 0;

($pre,$args,@rest)=split(/\(|\)|{/);
@pres = split(/\s+/,$pre);
$name = pop @pres;

$presc = join " ",@pres;

push @tagstack,"method";

$desc = join " ",@rest;

%declare = ("presc",$presc,"name",$name,"desc",$desc);

$out = "\n\n<p/><method";

&attributes;

print "$out>
<args>$args</args>
<exec>
";

push @tagstack,"exec";

next;

}


# END TYPE DECLARE
#####################################

##########
##########      if(/^for|^while|^try|^if|^else|^finally|^switch/){
##########


if(/{\s*\/\/\s*$/) {

s/}\s*\/\/(.*)$|{\s*\/\/(.*)$|\s*\/\/(.*)$//;

s/\((.*)\)/ $1 / unless /try/;

$parenflag=1;


if(/^(\w+)\b/) { $element = $1;}

push @tagstack,$element;

@line = split(/\s+/);

shift @line;

$preline = join " ",@line;

$splitter = ";" ;

@line = split(/$splitter/,$preline);

if(/^for/) { @attrs = qw(initial test increment);}
if(/^while|^if/) { @attrs = qw(condition);}
if(/^switch/) { @attrs = qw(variable);}
if(/^try/) { @attrs = "";}
if(/^else/) { @attrs = ""; $elseflag = 1;}

$out = "\n\n<".$element;

for(@attrs) {

($content = shift @line) =~ s/\s*(.*)\b\s*/$1/;

for ($content) {
s/\&/&amp\;/g;

s/</&lt;/g;
s/>/&gt;/g;

s/\"/&#x22\;/g;
s/\./&#x2e\;/g;
s/XXX/\;&#x22\;/g;
}

if(!$elseflag && ($element ne  "try") && ($element ne "finally")){

$out .= " ".$_."=".'"'.$content.'"';

} else {

$elseflag=0;
}

}
print "$out>\n";

next;
}

###########################################################
###########################################################

s/System\.out\.println\((.*)\)\s*\;/\n<print>$1<\/print>\n/;

if(/^\/\/\s*\%/) { print "\n<p/>"; next;}

######### blue declarations ##########
if(/\/\/ff\s*/) {
  s/\/\/ff//;
($A,@B) = split(/=/);
@y = split(/\s/,$A);
$B = join "=",@B;
$check = ($#y>0);
$x0 = pop @y;
$x1 = join " ",@y;
for($B){ 
s/new\s*(\w+)\b/<ff>new<\/ff> <b>$1<\/b>/g;
}
$outstring = "";
if($check){$outstring = "<b>".$x1."</b>";}
$outstring =~ s/XXX/\;"/;
$B =~ s/XXX/\;"/;
print "\n $outstring $x0 = $B <br/>\n";
next;
}

if(/\/\/\/\/\/\s*/) {
s/\/\/\/\/\///;
($x1,$x2,@y) = split;
print "\n<b>$x1</b> <fg>$x2<\/fg> @y<br/>\n";
next;
}

if(/\/\/\/\/\s*/) {
s/\/\/\/\///;
@y = split;
$x = pop @y;
$xx = join " ",@y;
print "\n<fg>$xx<\/fg> $x<br/>\n";
next;
}
#######################################

### QUICK ELEMENT
if(/\/\/\s*(.*?)\|\s*$/) {

s/(.*)\/\/\s*(.*?)\s*\|/<$2>$1<\/$2>/;

print $_."\n<p/>";
next;
}

if(/^\/\//) { print "<p>$_</p>\n"; next;}

$_ = &methodcall($_);

if(/\/\/(.*)$/){

$_ .="<br/>";

}

print;

}

print '
</java>
';

close IN;

sub attributes{

for(keys %declare){

($content = $declare{$_}) =~ s/\s*(.*)\b\s*/$1/;

$out .= " ".$_."=".'"'.$content.'"';
                  }
}

sub methodcall{
 $line = shift;

	if($line=~/=/){
	($lhs,@rhs) = split(/=/,$line);
$_ = join "=",@rhs;
while(/(\w+?)\.(\w+?)\((.*?)\)/g){
$x=$1;$y=$2;$z=$3;
for($x,$y){
s/\&/&amp\;/g;

s/</&lt;/g;
s/>/&gt;/g;

s/\"/&#x22\;/g;
s/\./&#x2e\;/g;
}
if($z=~/\)|\(/){
	$_ = $lhs."= ".$_;
	s/\;\s*$/\;<br\/>\n/;
return $_;
} else {
 s/$x\.$y\($z\)/<function variable=\"$x\" name=\"$y\">$z<\/function>/;
}}
	$_ = $lhs."= ".$_;
	s/\;\s*$/\;<br\/>\n/;
} else {
$_ = $line;
while(/(\w+?)\.(\w+?)\((.*?)\)/g){
$x=$1;$y=$2;$z=$3;
for($x,$y){
s/\&/&amp\;/g;

s/</&lt;/g;
s/>/&gt;/g;

s/\"/&#x22\;/g;
s/\./&#x2e\;/g;
}
if($z=~/\)|\(/){
	s/\;\s*$/\;<br\/>\n/;
return $_;
} else {
 s/$x\.$y\($z\)/<function variable=\"$x\" name=\"$y\">$z<\/function>/;
}}
 s/\;\s*$/\;<br\/>\n/;
	}
return $_ ;
}
