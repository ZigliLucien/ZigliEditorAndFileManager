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

<xsl:template match="*|@*">
	 <xsl:copy><xsl:apply-templates select="node()|@*">
	   <xsl:sort select="*[name()=$value1]" data-type="{$type1}"/>
	   <xsl:sort select="*[name()=$value2]" data-type="{$type2}"/>
     </xsl:apply-templates>
     </xsl:copy>
     </xsl:template>

</xsl:stylesheet>			
