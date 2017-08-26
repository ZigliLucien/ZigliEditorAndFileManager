<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>
 
  <xsl:template match="/">
     <html>
       <xsl:apply-templates/>
<p/><a href="javascript: history.back()"> Back </a>
     </html>
   </xsl:template>

<xsl:template match="mail">
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
	 <h1> <font color="cc4444"> Mail  </font> </h1>
	 <body bgcolor="dddddd">
	   <xsl:apply-templates/>
	 </body>
   </xsl:template>

<xsl:template match="Subject|From|Date">
  <b><xsl:value-of select="name()"/>:</b> <em><xsl:value-of select="."/></em>
  <br/>
</xsl:template>

<xsl:template match="ReplyTo">
  <em>Reply-To:</em> 
<a href="mailto:{.}"> <xsl:value-of select="."/> </a>
</xsl:template>


<xsl:template match="br|pre">
  <xsl:copy><xsl:apply-templates/></xsl:copy>
</xsl:template>

<xsl:template match="a">
<a href="{@href}"><xsl:apply-templates/></a>
</xsl:template>


<xsl:template match="message">
  <p>  
    <table align="center" width="75%"><tr><td bgcolor="ffffee">
    <xsl:apply-templates/>
</td></tr></table>
  </p>
</xsl:template>

<xsl:template match="headers">
  <p>  
    <table border ="1"><tr><td bgcolor="dddddd"><font face="helvetica">
    <xsl:apply-templates/>
  </font>
</td></tr></table>
  </p>
</xsl:template>




</xsl:stylesheet>			
