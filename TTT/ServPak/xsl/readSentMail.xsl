<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>
 
  <xsl:template match="/">
     <html>
      <xsl:apply-templates select="//filename"/>
     </html>
   </xsl:template>

<xsl:template match="filename">
       <head>
	 <title> Mail </title>
<style type="text/css">

	TD {
	    font-family: Arial, Helvetica, sans-serif;
	    font-size: 115%;
	    color: "#000000"
	}
	
	a:hover{ color: #bb88ff; }      
</style>
     
</head>
<body bgcolor="dddddd">
	 <h2> <font color="cc4444"> Sent Mail </font> </h2>	 
       <xsl:apply-templates select="//subject|//towhom|//date"/>
       <xsl:apply-templates select="//data"/>
<p/><a href="javascript: history.back()"> Back </a>
</body>
   </xsl:template>

<xsl:template match="subject|towhom|date">
  <b><xsl:value-of select="name()"/>: </b> <em><xsl:value-of select="."/></em>
  <br/>
</xsl:template>

<xsl:template match="br|pre">
  <xsl:copy><xsl:apply-templates/></xsl:copy>
</xsl:template>

<xsl:template match="a">
<a href="{@href}"><xsl:apply-templates/></a>
</xsl:template>


<xsl:template match="data">
<xsl:param name="dt"><xsl:value-of select="."/></xsl:param>
  <p>  
    <table align="center" width="75%"><tr><td bgcolor="ffffee">
<pre>
	<xsl:value-of select="substring-after($dt,'Subject:')"/>
</pre>
</td></tr></table>
  </p>
</xsl:template>


</xsl:stylesheet>			
