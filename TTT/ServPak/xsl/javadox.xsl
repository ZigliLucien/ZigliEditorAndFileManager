<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html"/>

  <xsl:template match="/">
    <html><head><style>
	span.a{background-color: #ffddff;} td.b{background-color: #55ff55;}
	span.c{background-color: cyan;}span.b{background-color: #55ff55;}
	span.d{background-color: #ffffcc;}span.e{background-color: #ffeeee;}
	span.f{background-color: #ffffee;}
	</style>
	</head>
	<body bgcolor="#dddddf">
	<h2><xsl:value-of select="jdox/class/name"/></h2>
	<form action="MakDox.jav" method="get">
	<h3><span class="c">Class</span></h3>
		<xsl:apply-templates select="//class"/>
	<h3><span class="f">Constructors</span></h3>
		<xsl:apply-templates select="//constructor"/>
	<h3><span class="b">Fields</span></h3>	
	<table>
		<xsl:apply-templates select="//field"/>
	</table>
	<h3><span class="d">Methods</span></h3>		
		<xsl:apply-templates select="//method"/>
	<input type="submit" value="Enter Comments"/>
	<input type="reset"/>
	</form>
      </body>
    </html>
  </xsl:template>

<xsl:template match="class">
<xsl:param name="nomen">class!<xsl:value-of select="classname"/></xsl:param>
<span class="c"><xsl:value-of select="name"/></span>
<p/><textarea name="{$nomen}" value="{class}" rows="4" cols="50">
<xsl:value-of select="comment"/>
</textarea>
<input type="reset"/><p/>&#160;<p/>
<span class="e">author</span>&#160;<input name="author" size="40" value="{author}"/><p/>
<span class="e">version</span>&#160;<input name="version" size="40" value="{version}"/><p/>&#160;<p/>
</xsl:template>

<xsl:template match="constructor">
	<xsl:param name="nomen">constructor!<xsl:value-of select="name"/></xsl:param>
	<span class="c"><xsl:value-of select="name"/></span>
	<input name="{$nomen}" size="55" value="{comment}"/><p/>
</xsl:template>

<xsl:template match="field">
	<xsl:param name="nomen">field!<xsl:value-of select="name"/></xsl:param>
	<tr><td>
	<span class="e"><i><xsl:value-of select="type"/></i></span></td>
	<td align="left" class="b"><xsl:value-of select="name"/></td>
	<td><input name="{$nomen}" size="55" value="{comment}"/></td></tr>
	<tr><td><br/></td><td><br/></td></tr>
</xsl:template>

<xsl:template match="method">
<xsl:param name="nomen">method!<xsl:value-of select="name"/></xsl:param>
<span class="e"><i><xsl:value-of select="type"/></i></span>
	<span class="d"><xsl:value-of select="name"/></span>
	&#160;<textarea name="{$nomen}"  rows="4" cols="50" class="a">
	<xsl:value-of select="comment"/>
	</textarea><p/>
</xsl:template>

<xsl:template match="import|importpkg">
</xsl:template>


    </xsl:stylesheet>
