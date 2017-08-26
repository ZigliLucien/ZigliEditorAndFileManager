#!/usr/bin/perl

@args = split(/\//,$ARGV[0]);

$pretitle = $args[$#args];

($title = $pretitle) =~ s/\./ /;

($title1,$title2) = split(/\s/,$title);

$title2 = ucfirst($title2);

$title = "$title1 $title2";

$outfile = Help.$title1.$title2.".xml";

open OUT,">:utf8", $outfile;

print OUT '<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="/usr/local/ZigliFM/ServPak/html/helper.xsl"?>
<!DOCTYPE tpwm [<!ENTITY % tpwsymbols SYSTEM "file:/usr/local/ZigliFM/TPW"> %tpwsymbols;]>
<tpwm>';
print OUT "
<title>$title</title>
";
print OUT '
<body>
<display>
<bordermatrix width="40%">
<ams/><bf>Key</bf><amcx/><bf>Symbol</bf><cr/>
';

while(<>){

chomp;

($x,$y)=split(/=/);

$xx = chr($x);
if($x=~/S/){ chop($x); $xx ="Shift-".chr($x);}
if($x=~/C/){ chop($x); $xx ="Meta-".chr($x);}

if(length($y) >4) { 
$y1 = substr $y,0,4; $y2 = substr $y,4,4; print STDOUT $y1," ",$y2,"\n";
$y1 = sprintf "0x%lx",$y1;
$y2 = sprintf "0x%lx",$y2;
$z1 = chr(eval($y1));
$z2= chr(eval($y2));
$z = "$z1$z2";
} else {

$y = sprintf "0x%lx",$y;
$z = chr(eval($y));

}
print OUT "<ams/>Alt-$xx<amcx/>$z<cr/>\n";

}

print OUT '
</bordermatrix>
</display>
<skip/>
<a href="HelpContents.html"> Back: Help Contents </a>
</body>
</tpwm>
';

close OUT;
