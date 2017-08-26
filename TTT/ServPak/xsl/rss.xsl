<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">


   <xsl:output method="html"/>



   <xsl:template match="/">
<html>
<head>
		<link href="ServPak/css/rsshtml.css" type="text/css" rel="stylesheet"/>
<title>
				<xsl:value-of select="/rss/channel/title"/>
</title>
</head><body>
			<h1>
				<xsl:value-of select="/rss/channel/title"/>
			</h1>
			<h2>
				<xsl:value-of select="/rss/channel/description"/>
			</h2>
<br/>
		<xsl:apply-templates select="/rss/channel"/>
	</body>
	</html>
   </xsl:template>

	<xsl:template match="/rss/channel">

<ul>
	<xsl:for-each select="/rss/channel/item">
	<li>
		<a href="{link}" title="{link}">
		<img src='oball.png'
		         onmouseout="src='oball.png' " 
		         onmouseover="src='forward.png' "
		         style="border:none;padding-right:6px"/>
		</a>
		<a href="#{link}" title="See Description"><xsl:value-of select="title"/></a>
	</li>
	</xsl:for-each>
</ul>

<p/><br/>
			<table align="center">
				<xsl:apply-templates select="item"/>
			</table>
	</xsl:template>

	<xsl:template match="/rss/channel/item">
		<tr><td> <a name="{link}"></a></td></tr>
<xsl:if test="pubDate">
		<tr><td>
			<div class="date">
			<tt>		
				<xsl:value-of select="pubDate"/>
			</tt>	
			</div>
		</td></tr>
</xsl:if>
		<tr><td>
<div>
 	<div style="float:left" class="link"><a href="{link}" title="{link}">
				<xsl:value-of select="title"/>
			</a>
	</div>
		<div id="linkback" 
		onclick="history.back()"  onmouseout="this.className='off'" 
		onmouseover="this.className='active'">back</div>
</div>
		</td></tr>

		<tr><td>
			<div class="item">
		<blockquote><blockquote>
				<xsl:value-of select="description"/>
		</blockquote></blockquote>
			</div>
		</td></tr>
	</xsl:template>




</xsl:stylesheet>			
