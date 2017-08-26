<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>

<xsl:template match="properties">
<xsl:param name="title"><xsl:value-of select="//comment"/></xsl:param>
<html>
<head> 

<title><xsl:value-of select="$title"/></title>

<style type="text/css">
	TD {
	    font-family: Arial, Helvetica, sans-serif;
	    font-weight: normal;
	    color: "#000000"
	}

	TH {
            text-transform: capitalize;
            font-family: Times;
	    font-weight: bold;
	    color: "#0000ff"
	}
</style>

</head>
<body bgcolor="ffffff">
<h1><xsl:value-of select="$title"/></h1>
<table align="center" border="1" width="95%" cellpadding="1">
<tr><th>Key</th><th>Value</th></tr>
	  <xsl:apply-templates/>	
	</table>
</body>
</html>
</xsl:template>

<xsl:template match="entry">
<tr>
<td align="center"> <tt><xsl:value-of select="@key"/></tt></td>
<td align="center"> <xsl:value-of select="."/></td>
</tr>
</xsl:template>

<xsl:template match="comment"/>

</xsl:stylesheet>



