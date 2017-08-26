<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="xml"/>

<xsl:template match="/">
<xsl:text disable-output-escaping="yes">
&lt;?xml-stylesheet type="text/plain" href="ServPak/xsl/generic.xsl"?&gt;
</xsl:text>
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="command">
<command key="{.}"><xsl:value-of select="."/></command>
</xsl:template>


<xsl:template match="*|@*">
   <xsl:copy> 
   <xsl:apply-templates select="node()|@*"/>
   </xsl:copy>
 </xsl:template>


    </xsl:stylesheet>
