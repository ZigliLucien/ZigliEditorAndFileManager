<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:strip-space elements="*"/>

   <xsl:template match="/*/*">
<xsl:for-each select="*[not(position()=last())]">
 <xsl:if test="not(node())">-</xsl:if>
<xsl:apply-templates/>,</xsl:for-each>
<xsl:for-each select="*[position()=last()]"> <xsl:if test="not(node())">-</xsl:if><xsl:apply-templates/>
</xsl:for-each><xsl:text>
</xsl:text>
   </xsl:template>

   <xsl:template match="/*">
<xsl:text>
</xsl:text>
   <xsl:apply-templates/>
   </xsl:template>

   <xsl:template match="*|@*">
     <xsl:copy><xsl:apply-templates select="node()|@*"/></xsl:copy>
   </xsl:template>

 </xsl:stylesheet>