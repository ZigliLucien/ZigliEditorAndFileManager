declare variable $value external;

let $k:=name(/*)

let $h:=
if($value="timekey") then

for $i in //filedata
order by xs:integer($i/timekey/node()) descending
return $i

else

for $i in //filedata
order by $i/*[name()=$value]
return $i

let $j:=<comment>EOF<filename>~~</filename><filetype>~~</filetype><key1>~~</key1><key2>~~</key2><timekey/></comment>

return   element {$k} { ($h,$j) }
