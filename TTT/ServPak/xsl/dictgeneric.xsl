<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

  <xsl:template match="/">
    <html>
	<head><title>Dictionary Results </title>
<style type="text/css">

	td.a {
	    font-family: Arial, Helvetica, sans-serif;
	    font-weight: bold;
	    color: "#000000"
	}

	td.b {
	    font-family: Arial, Helvetica, sans-serif;
	    font-weight: normal;
	    color: "#000000"
	}

	th {
            text-transform: capitalize;
            font-family: Times;
	    font-weight: bold;
	    color: "#0000ff"
	}
</style>
</head>
      <body bgcolor="ffffff">
<h1> Dictionary Results </h1>
<table align="center" border="1" width="95%" cellpadding="1">
<tr><th>Word</th><th>Translation</th></tr>
	  <xsl:apply-templates select="//entry"/>	
	</table>
      </body>
    </html>
  </xsl:template>

<xsl:template match="entry">
<tr>
<td align="center" class="a">
<xsl:value-of select="word"/>
</td>
<td align="center" class="b">
<xsl:value-of select="translation"/>
</td>
</tr>
</xsl:template>

    </xsl:stylesheet>
