<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:strip-space elements="*"/>

   <xsl:template match="/*/*">
     <xsl:text>
     </xsl:text>
     <xsl:for-each select="*">
       <xsl:if test="not(position()=last())">
       <xsl:apply-templates/>,</xsl:if>
       <xsl:if test="position()=last()">
       <xsl:apply-templates/></xsl:if>
       </xsl:for-each>
   </xsl:template>

   <xsl:template match="/">
     <xsl:apply-templates/>
     <xsl:text>
     </xsl:text>
   </xsl:template>

   <xsl:template match="br|em|i|b|p">
     <xsl:copy><xsl:apply-templates/></xsl:copy>
   </xsl:template>

 </xsl:stylesheet>