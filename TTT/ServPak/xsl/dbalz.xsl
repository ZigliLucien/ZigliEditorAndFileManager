<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

<xsl:param name="value"/>

<xsl:template match="/*" mode="one">
  <xsl:value-of select="translate(name(),'_',' ')"/>
</xsl:template>


  <xsl:template match="/">
    <html>
	<head><title><xsl:apply-templates select="/*" mode="one"/></title>
<style type="text/css">

	TD {
	    font-family: Arial, Helvetica, sans-serif;
	    font-size: 80%;
	    font-weight: normal;
	    color: "#000000"
	}

	TH {
            text-transform: capitalize;
            font-family: Times;
	    font-size: 16pt;
	    font-weight: bold;
	    color: "#0000ff"
	}
</style>
</head>
      <body bgcolor="ffffff">
<h1> <xsl:apply-templates select="/*" mode="one"/> </h1>
<table align="center" border="1" width="95%" cellpadding="1">
	  <xsl:apply-templates/>	
	</table>
<p/>
	  <table>
	    <tr><td width="30%">	
	    </td>
	    <td>
	      <br/>	    </td>
	      <td>	<a href="DBanalyze.jav?renew=yes"> To DB Ops </a>
      </td>
</tr>
	    <tr><td width="30%">	
	    </td>
	    <td> <br/> </td>
	      <td><br/> </td>
</tr></table>
      <p/>
<a href="DBgo.jav?"> -&gt; Back to Table  </a>
<p/><a href="home?home"> Back to <xsl:value-of select="$value"/> </a>
      </body>
    </html>
  </xsl:template>

<xsl:template match="/*/*">
	  <tr>
	  <xsl:apply-templates select="*"/>	
	</tr>	
</xsl:template>


	<xsl:template match="/*/*/*">
  <td align="center">
  <xsl:choose>
    <xsl:when test="(.)=''">
      <br/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
</xsl:otherwise>
</xsl:choose>
</td>
</xsl:template>

<xsl:template match="br|em|a|@href">
<xsl:copy>
<xsl:apply-templates select="@*"/>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>

    </xsl:stylesheet>
