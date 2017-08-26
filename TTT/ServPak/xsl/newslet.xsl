<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>
 
  <xsl:template match="tpwm">
     <html>
<head>
<title>Math Dept Weekly News</title>
<style type="text/css">  
ul { list-style: circle}
th { background: #aaeeff}
th.a { background: #0000aa}
td { font-family: helvetica,arial}
td.a { background: #eeffff}
td.b { background: #ffffdd}
td.c { background: #eeffee}
</style>
</head>
<body bgcolor="#ffffff">

<center>
<h1> <font face="helvetica" size="-1"> Mathematics Department </font>
&#x00A0; Weekly News &#x00A0;
<font face="helvetica" size="-1"> 
<xsl:value-of select="date/calendar"/> (<xsl:value-of select="date/week"/>) </font>
</h1>
</center>
       <xsl:apply-templates/>
     </body>
     </html>
   </xsl:template>

<xsl:template match="start">
<table  align="center" width="90%">
<tr><th><em>IN THE NEWS</em></th>
<th>DID YOU KNOW ?</th>
</tr>
<tr><td class="a" width="45%">
<br/>
<ul>
<xsl:apply-templates select="news"/>
<br/>
&#x00A0; 
</ul>
</td>
<td class="a" width="45%">
<br/>
<ul style="list-style: square">
<xsl:apply-templates select="dyknow"/>
<br/>
&#x00A0; 
</ul>
</td>
</tr>
</table>

<p/>

<table width="90%" align="center" cellspacing="4">
<tr>
<th align="center" class="a">
 <b>
<font face="helvetica" color="#ffffff">\/\/\/\/\/\/\ &#x00A0;
Seminars THIS WEEK &#x00A0; /\/\/\/\/\/\/ 
</font>
</b></th>
</tr><tr><td><br/></td></tr>
<xsl:apply-templates select="seminars"/>
</table>

<p/>

<table width="90%" align="center">
<tr><td align="center" bgcolor="#ccffcc"> <em><b>ESSAY</b></em> </td></tr>
<tr><td><br/></td></tr>
<tr><td class="c">
<blockquote>
<xsl:apply-templates select="essay"/>
</blockquote>
</td></tr>
<tr><td><br/></td></tr>
<tr><td align="center" bgcolor="#ccffcc"><b>QUESTION of the WEEK</b></td></tr>
<tr><td><br/></td></tr>
<tr><td class="c">
<blockquote>
<xsl:apply-templates select="question"/>
</blockquote>
</td></tr>
<tr><td><br/></td></tr>
<tr><td align="center" bgcolor="#ccffcc"><b>REMINDER</b></td></tr>
<tr><td><br/></td></tr>
<tr><td class="c">
<ul>
<xsl:apply-templates select="reminder"/>
<br/>
&#x00A0; 
</ul>
</td></tr>
<tr><td><br/></td></tr>
<tr><td align="center" bgcolor="#aaffaa"> <b>
<a href="mailto:mdwn@chanoir.math.siu.edu">
* * *
Click here to CONTRIBUTE to MDWN
* * *
</a></b></td></tr>
</table>

</xsl:template>

<xsl:template match="day">
<tr>
<td>
<ul style="list-style:disc"><p/>
<li style="list-style:none"> <b><xsl:value-of select="@data"/></b></li>
<xsl:apply-templates/>
<br/>
&#x00A0; 
</ul>
</td></tr>
</xsl:template>

<xsl:template match="item">
<p/>
<li>
<xsl:apply-templates/>
</li>
</xsl:template>

<xsl:template match="date"/>

<xsl:template match="br|em|i|tt|a|@*|b|p|blockquote|sub|sup|font">
<xsl:copy>
<xsl:apply-templates select="node()|@*"/>
</xsl:copy>
</xsl:template>

<xsl:template match="it">
<i>
<xsl:apply-templates/>
</i>
</xsl:template>

<xsl:template match="bf">
<b>
<xsl:apply-templates/>
</b>
</xsl:template>

</xsl:stylesheet>
