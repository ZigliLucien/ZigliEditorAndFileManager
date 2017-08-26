<?xml version="1.0" encoding="utf-8"?>
<!--
  Title: RSS 1.0 XSL Template
  Author: Rich Manalang (http://manalang.com)
  Description: This sample XSLT will convert any valid RSS 1.0 feed to HTML.
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:foo="http://purl.org/rss/1.0/">
  	<xsl:output method="html"/>
	<xsl:template match="/">
<html>
<head>
		<link href="ServPak/css/rsshtml.css" type="text/css" rel="stylesheet"/>
<title>
				<xsl:value-of select="/rdf:RDF/foo:channel/foo:title"/>
</title>
</head><body>
			<h1>
				<xsl:value-of select="/rdf:RDF/foo:channel/foo:title"/>
			</h1>
			<h2>
				<xsl:value-of select="/rdf:RDF/foo:channel/foo:description"/>
			</h2>
<br/>
		<xsl:apply-templates select="/rdf:RDF/foo:channel"/>
	</body>
	</html>
	</xsl:template>
	<xsl:template match="/rdf:RDF/foo:channel">
<ul>
	<xsl:for-each select="/rdf:RDF/foo:item">
	<li>
		<a href="{foo:link}" title="{foo:link}">
		<img src='oball.png'
		         onmouseout="src='oball.png' " 
		         onmouseover="src='forward.png' "
		         style="border:none;padding-right:6px"/>
		</a>
		<a href="#{foo:link}" title="See Description"><xsl:value-of select="foo:title"/></a>
	</li>
	</xsl:for-each>
</ul>
<p/><br/>
			<table align="center">
				<xsl:apply-templates select="/rdf:RDF/foo:item"/>
			</table>
	</xsl:template>
	<xsl:template match="/rdf:RDF/foo:item">
		<tr><td> <a name="{foo:link}"></a></td></tr>
		<tr><td>
			<div class="date">
			<tt>		
				<xsl:value-of select="dc:date"/>
			</tt>	
			</div>
		</td></tr>

		<tr><td>
<div>
<div style="float:left" class="link">
			<a href="{foo:link}" title="{foo:link}">
				<xsl:value-of select="foo:title"/>
			</a>
	</div>
		<div id="linkback" 
		onclick="history.back()"  onmouseout="this.className='off'" 
		onmouseover="this.className='active'">back</div>
</div>
		</td></tr>

		<tr><td>
			<div class="item">
		<blockquote><blockquote><blockquote>
				<xsl:value-of select="foo:description"/>
		</blockquote></blockquote></blockquote>
			</div>
		</td></tr>
	</xsl:template>
</xsl:stylesheet>
