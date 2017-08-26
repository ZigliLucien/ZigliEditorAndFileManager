<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

<xsl:template match="project">
	<html>
		<head>
			<title> <xsl:value-of select="@name"/> </title>
		</head>
	<body bgcolor="lightgray">
		<h1> <xsl:value-of select="@name"/> </h1>
			&#160;<p/>
	<table border="1"><caption><h3> Property Table</h3><br/></caption>
		<tr><th>Name</th><th>Value</th></tr>
	<xsl:for-each select="property">
<tr><td align="center" bgcolor="white">&#160;<xsl:value-of select="@name"/>&#160;</td>
<td align="center" bgcolor="white">&#160;<xsl:value-of select="@value"/>&#160;</td></tr>
	</xsl:for-each>
	</table>
	<p/>&#160;<p/>
	<h2> Targets and Actions </h2>
<xsl:apply-templates/>

		</body>
		</html>
</xsl:template>

<xsl:template match="target">
	<p/>&#160;<br/>
	<h3 style="background:#ffff88"><xsl:value-of select="@name"/></h3>
	<xsl:apply-templates select="@*[not(name()='name')]"/>
	<ul>
	<xsl:apply-templates/>
	</ul>
</xsl:template>

<xsl:template match="target//*">
	<p/>
	<ul style="list-style:none"><font style="font-size:120%;background:#ddffdd">
		<xsl:value-of select="name()"/></font>
	<br/>
	<xsl:apply-templates select="@*"/>
	<xsl:apply-templates/>
	</ul>
</xsl:template>

<xsl:template match="@*">
	<li style="background:white"> 
	<xsl:value-of select="name()"/> : &#160; <xsl:value-of select="."/> 
	</li>
</xsl:template>

<xsl:template match="br|em|a|@href">
	<xsl:copy>
	<xsl:apply-templates select="@*"/>
	<xsl:apply-templates/>
	</xsl:copy>
</xsl:template>

</xsl:stylesheet>