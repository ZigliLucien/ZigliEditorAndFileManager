declare variable $value external;

    <html>
	<head>	<title>{name(/*)}</title>
<style type="text/css">

	TD {{
	    font-family: Arial, Helvetica, sans-serif;
	    font-size: 75%;
	    font-weight: normal;
	    color: "#000000"
	}}

	TH {{
            text-transform: capitalize;
            font-family: Times;
	    font-size: 16pt;
	    font-weight: bold;
	    color: "#0000ff"
	}}
</style>
</head>
      <body bgcolor="ffffff">
<h1>{name(/*)}</h1>
<table align="center" border="1" width="95%" cellpadding="1">
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
<p/>
	  <table>
	    <tr><td width="30%">	
	      <a href="DBgo.jav?change=yes"> Edit table </a>&#160;&#160;
	    </td>
	    <td>
	      <br/>	    </td><td>
	  <a href="DBgo.jav?addrow=yes"> Add a new row </a>
	</td><td width="25%"><br/></td>
	<td>	
<form action="DBgo.jav" method="get">
  Add a field <br/>(lowercase, start with 'zz' if numerical, like zzcat for cat) 
<input name="addfield" size="10"/>
</form>
      </td></tr></table>
<br/>
<a href="DBgo.jav?formentry=yes"> Enter new row via form </a>
<p/>

Click	<a href="DBgo.jav?"> 
     --&gt; here &lt;-- </a> when finished adding rows/fields or editing is complete. 

	<p/>&#160;<br/>
 <ul>
<li>
-&gt; <a href="DBgo.jav?searchsort=yes"> Search/Sort Views </a>
</li><li>	
-&gt;-&gt;  <a href="DBgo.jav?analyze=yes"> DB operations  </a>
</li><li>
-&gt;-&gt;-&gt;  <a href="DBgo.jav?rcops=yes"> Row &amp; Column operations  </a>
</li><li>
-&gt;-&gt;-&gt;-&gt;  <a href="DBgo.jav?goquery=yes"> Run a Query </a>
</li>
</ul>

<p/>&#160;<br/>
&#160;&#160;&#160;&#160;&lt;- Back to: <a href="home?home"> {$value} </a>
      </body>
    </html>

