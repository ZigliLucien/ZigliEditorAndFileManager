<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html"/>

<xsl:template match="/">
<xsl:param name="cmd"><xsl:value-of select="//command"/></xsl:param>

<html>
<head>
<style>
body{ font-family: Arial, Lucida Typewriter;
font-size: 18pt;
font-weight:bold;
}
</style>
<title> Zigli's Editor Help </title>
</head>

<body>
<h1> <xsl:value-of select="$cmd"/></h1>
<xsl:apply-templates select="//command"/>
<xsl:apply-templates select="//shortkey"/>
<xsl:apply-templates select="//description"/>
<p/>&#xa0;<p/>&#xa0;<p/>
<hr/>
<a href="file:ServPak/html/HelpContents.html">
To Help Contents
</a>
<hr/>
</body>
</html>
</xsl:template>

<xsl:template match="command">
<xsl:param name="menu"><xsl:value-of select="//menu"/></xsl:param>
This command is found on the <b><xsl:value-of select="$menu"/>.</b> <p/>
</xsl:template>

<xsl:template match="shortkey">
It is activated by: <b><xsl:value-of select="."/> </b>.<p/>
</xsl:template>

<xsl:template match="description">
<b>Description:</b>
<blockquote>
<!-- xsl:value-of select="."/ -->
<xsl:apply-templates/>
</blockquote>
</xsl:template>

<xsl:template match="//description/*">
<xsl:copy-of select="."/>
</xsl:template>

    </xsl:stylesheet>
