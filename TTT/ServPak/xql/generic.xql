<html>
<head>
	  <title>{name(/*)}</title>
              <style>th.x{{text-transform:capitalize; color: #00a8af}} </style>
</head>
<body>
<h1>{name(/*)}</h1> 
<table border='yes'>
<tr>
{
for $k in /*/*[position()=1]/* 
let $l:=name($k) 
 return 
<th class="x">
{if (starts-with($l,'zz')) then
translate(substring-after($l,'zz'),'_',' ') else translate($l,'_',' ')} 
</th> 
}
</tr>
{
for $i in /*/*  
return <tr> 
{
for $j in $i/* 
 return 
	<td align="center">{$j/node()}</td>
 }    
	</tr>
}
</table>

</body></html>
