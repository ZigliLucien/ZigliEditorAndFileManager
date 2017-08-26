<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:param name="value"/>

<xsl:param name="value1" select="substring-before($value,'-')"/>
<xsl:param name="value2" select="substring-after($value,'-')"/>

<xsl:param name="type1">
  <xsl:if test="starts-with($value1,'zz')">number</xsl:if>
  <xsl:if test="not(starts-with($value1,'zz'))">text</xsl:if>
</xsl:param>

<xsl:param name="type2">
  <xsl:if test="starts-with($value2,'zz')">number</xsl:if>
  <xsl:if test="not(starts-with($value2,'zz'))">text</xsl:if>
</xsl:param>


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
  <xsl:for-each select="/*/*[position()=1]">
	  <tr>
	  <xsl:for-each select="*">
		    <th>
<xsl:if test="starts-with(name(),'zz')">
<xsl:value-of select="substring-after(name(),'zz')"/></xsl:if>

<xsl:if test="not(starts-with(name(),'zz'))">
<xsl:value-of select="name()"/></xsl:if>
	            </th>
          </xsl:for-each>
          </tr>
</xsl:for-each>
	  <xsl:apply-templates/>	
	</table>
      </body>
    </html>
  </xsl:template>

<xsl:template match="/*/*">
	  <tr>
	  <xsl:apply-templates/>	
	</tr>	
</xsl:template>


 <xsl:template match="*|@*">
	 <xsl:copy><xsl:apply-templates select="node()|@*">
	   <xsl:sort select="*[name()=$value1]" data-type="{$type1}"/>
	   <xsl:sort select="*[name()=$value2]" data-type="{$type2}"/>
     </xsl:apply-templates>
         </xsl:copy>
       </xsl:template>


	<xsl:template match="/*/*/*">
	  <xsl:call-template name="runit"/>
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

</xsl:stylesheet>			



