<?xml version="1.0"?>
<xsl:stylesheet  version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html"/>

  <xsl:param name="value"/>

<xsl:param name="valueLine" select="tokenize($value,'!')"/>

<xsl:param name="userdir" select="$valueLine[1]"/>
<xsl:param name="direcout" select="$valueLine[3]"/>
<xsl:param name="direc" select="$valueLine[4]"/>
<xsl:param name="processcall" select="$valueLine[5]"/>

<xsl:template match="/*" mode="one">
 <xsl:value-of select="$direcout"/>
 </xsl:template>


  <xsl:template match="/">
    <html>
	<head><title><xsl:apply-templates select="/*" mode="one"/></title>
<link rel="stylesheet" type="text/css">
<xsl:attribute name="href"><xsl:value-of select="$userdir"/>/ServPak/css/listing.css</xsl:attribute>
</link>
	<script type="text/javascript"> 
<xsl:attribute name="src"><xsl:value-of select="$userdir"/>/ServPak/js/listing.js</xsl:attribute>
</script>
</head>
<body bgcolor="ffffff" oncontextmenu="return false" onload="setup()">

<form action="FileOps.jav" method="GET" name="overall" id="{$direc}">
<input type="radio" name="fileops" value="VVV">  
<xsl:if test="$processcall='VVV'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="v"> view</span>
<input type="radio" name="fileops" value="CCC">
<xsl:if test="$processcall='CCC'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="c">copy</span>
<input type="radio" name="fileops" value="MMM">
<xsl:if test="$processcall='MMM'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="m">move</span>
<input type="radio" name="fileops" value="XXX">
<xsl:if test="$processcall='XXX'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="d"> dele </span>
<input type="radio" name="fileops" value="EEE">
<xsl:if test="$processcall='EEE'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="e">  edit </span>
<input type="radio" name="fileops" value="QQQ"> 
<xsl:if test="$processcall='QQQ'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="q">  quik </span>
<input type="radio" name="fileops" value="AAA">
<xsl:if test="$processcall='AAA'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="a"> note </span>
<p/>
<table align="center" width="98%" cellpadding="0" cellspacing="0">
	  <tr>
<th width="30%">Filename</th>
<th width="25%">Size &#160;&#160;&#160; Date &#160;&#160;&#160; Time</th> 
<th width="35%">Notes</th>
          </tr>
          <xsl:apply-templates/>

	</table>
</form>
       </body>
     </html>
  </xsl:template>

 <xsl:template match="/*/filedata">

   <tr>
<xsl:attribute name="class">
<xsl:if test="number(@parity)=1">a</xsl:if>
<xsl:if test="number(@parity)=0">b</xsl:if>
</xsl:attribute>
	    <xsl:apply-templates select="filename"/>	
	    <xsl:apply-templates select="sdt"/>	
	    <xsl:apply-templates select="annotation"/>	
	</tr>
</xsl:template>

<xsl:template match="/*/*/sdt">

  <td class="w"> 
<xsl:value-of select="@size"/> &#160;<xsl:value-of select="."/>&#160; <xsl:value-of select="@time"/>
 </td>
	</xsl:template>

<xsl:template match="/*/*/annotation">
  <td><xsl:apply-templates/></td>
	</xsl:template>

<xsl:template match="/*/*/filename">

  <xsl:param name="file"><xsl:value-of select="node()"/> </xsl:param>
  <xsl:param name="parity"><xsl:value-of select="number(../@parity)"/></xsl:param>

<td>
<input type="button">
<xsl:attribute name="value"><xsl:value-of select="$file"/></xsl:attribute>
 </input>
  </td>
	</xsl:template>

<xsl:template match="br|em|a|font|tt">
<xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="comment">
	<comment id="EOF"/>
</xsl:template>

<xsl:template match="timekey|filetype|key1|key2|plainname"/>

    </xsl:stylesheet>
