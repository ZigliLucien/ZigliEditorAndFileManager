<?xml version="1.0" encoding="utf-8"?>
<!--
  Title: Atom 0.3 XSL Template
  Author: Rich Manalang (http://manalang.com)
  Description: This sample XSLT will convert any valid Atom 0.3 feed to HTML.
-->
<xsl:stylesheet version="1.0"
  xmlns:atom="http://purl.org/atom/ns#"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  	<xsl:output method="html"/>
   <xsl:template match="/">
<html>
<head>
<link href="ServPak/css/rsshtml.css" type="text/css" rel="stylesheet"/>

<title>
				<xsl:value-of select="/atom:feed/atom:title"/>
</title>
</head><body>
			<h1>
				<xsl:value-of select="/atom:feed/atom:title"/>
			</h1>
			<h2>
				<xsl:value-of select="/atom:feed/atom:tagline"/>
			</h2>
<br/>

		<xsl:apply-templates select="/atom:feed"/>
	</body>
	</html>

	</xsl:template>
	<xsl:template match="/atom:feed">
<ul>
	<xsl:for-each select="atom:entry">
	<li>
		<a href="{atom:link/@href}" title="{atom:link/@href}">
		<img src='oball.png'
		         onmouseout="src='oball.png' " 
		         onmouseover="src='forward.png' "
		         style="border:none;padding-right:6px"/>
		</a>
	<a href="#{atom:link/@href}" title="See Description"><xsl:value-of select="atom:title"/></a>
	</li>
	</xsl:for-each>
</ul>
<p/><br/>
	
	<table align="center">
				<xsl:apply-templates select="atom:entry"/>
			</table>
	</xsl:template>
	<xsl:template match="atom:entry">
		<tr><td> <a name="{atom:link/@href}"></a></td></tr>

		<tr><td>
			<div class="date">
			<tt>		
				<xsl:value-of select="atom:issued"/>
			</tt>	
			</div>
		</td></tr>

		<tr><td>
<div>
<div style="float:left" class="link">
		<a href="{atom:link/@href}" title="{atom:link/@href}">
				<xsl:value-of select="atom:title"/>
			</a>
	</div>
		<div id="linkback" 
		onclick="history.back()"  onmouseout="this.className='off'" 
		onmouseover="this.className='active'">back</div>
</div>
		</td></tr>

		<tr><td>
			<div class="atom:entry">
		<blockquote><blockquote><blockquote>
				<xsl:value-of select="atom:summary"/>
		</blockquote></blockquote></blockquote>
			</div>
		</td></tr>


	</xsl:template>
</xsl:stylesheet>
