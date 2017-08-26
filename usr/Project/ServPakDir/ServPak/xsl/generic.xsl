<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

<xsl:template match="/*" mode="one">
  <xsl:value-of select="translate(name(),'_',' ')"/>
</xsl:template>


  <xsl:template match="/">
    <html>
	<head><title><xsl:apply-templates select="/*" mode="one"/></title>
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
<h1> <xsl:apply-templates select="/*" mode="one"/> </h1>
<table align="center" border="1" width="95%" cellpadding="1">
	  <xsl:apply-templates/>	
	</table>
      </body>
    </html>
  </xsl:template>

<xsl:template match="/*/*[position()!=1]">
	  <tr>
	  <xsl:apply-templates/>	
	</tr>	
</xsl:template>


	<xsl:template match="/*/*/*">
	  <xsl:call-template name="runit"/>
	</xsl:template>

	<xsl:template match="/*/*[position()=1]">
	  <tr>
	  <xsl:for-each select="*">
<th><xsl:value-of select="translate(name(),'_',' ')"/></th>
          </xsl:for-each>
          </tr>
<tr>
	  <xsl:for-each select="*">
<xsl:call-template name="runit"/>
          </xsl:for-each>
</tr>
         </xsl:template>


<xsl:template name="runit">
<td align="center">
  <xsl:choose>
    <xsl:when test="(.)=''">
      <br/>
    </xsl:when>
    <xsl:otherwise>
<!-- xsl:value-of select="(.)"/ -->
<xsl:apply-templates/>
</xsl:otherwise>
</xsl:choose>
</td>
</xsl:template>


<xsl:template match="tt|br|em|a|@href">
<xsl:copy>
<xsl:apply-templates select="@*"/>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>

<xsl:template match="bem">
<b><em>
<xsl:apply-templates/>
</em></b>
</xsl:template>

    </xsl:stylesheet>
