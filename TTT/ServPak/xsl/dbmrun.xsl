<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:template match="/">
      <xsl:apply-templates/>
      </xsl:template>

      <xsl:template match="/*/*">
      </xsl:template>

      <xsl:template match="/*">
     <xsl:text>
     </xsl:text>
       <xsl:for-each select="/*/*/*[@key]">
    	<xsl:sort select="@key"/>
<option><xsl:attribute name="value"><xsl:value-of select="@key"/></xsl:attribute><xsl:value-of select="."/></option>
	<xsl:text>
	</xsl:text>
    </xsl:for-each>
     </xsl:template>

</xsl:stylesheet>			
