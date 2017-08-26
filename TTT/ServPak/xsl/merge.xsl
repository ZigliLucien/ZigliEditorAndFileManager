<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

 <xsl:param name="value"/>

<xsl:template match="jdox">
<xsl:text disable-output-escaping="yes">
&lt;?xml-stylesheet type="text/plain" href="ServPak/xsl/javadox.xsl"?&gt;
</xsl:text>
<jdox>
<xsl:apply-templates/>
</jdox>
</xsl:template>

<xsl:template match="class">
<xsl:copy>
<xsl:apply-templates/>
<xsl:for-each select="document($value)">
<xsl:apply-templates select="//author" mode="one"/>
<xsl:apply-templates select="//version" mode="one"/>
<xsl:apply-templates select="//class/comment" mode="one"/>
</xsl:for-each>
</xsl:copy>
</xsl:template>

<xsl:template match="constructor">
<xsl:param name="nomen"><xsl:value-of select="name"/></xsl:param>
<xsl:copy>
<xsl:apply-templates/>
<xsl:for-each select="document($value)">
<xsl:apply-templates select="//constructor[name=$nomen]/comment" mode="one"/>
</xsl:for-each>
</xsl:copy>
</xsl:template>

<xsl:template match="field">
<xsl:param name="nomen"><xsl:value-of select="name"/></xsl:param>
<xsl:copy>
<xsl:apply-templates/>
<xsl:for-each select="document($value)">
<xsl:apply-templates select="//field[name=$nomen]/comment" mode="one"/>
</xsl:for-each>
</xsl:copy>
</xsl:template>

<xsl:template match="method">
<xsl:param name="nomen"><xsl:value-of select="name"/></xsl:param>
<xsl:copy>
<xsl:apply-templates/>
<xsl:for-each select="document($value)">
<xsl:apply-templates select="//method[name=$nomen]/comment" mode="one"/>
</xsl:for-each>
</xsl:copy>
</xsl:template>

<xsl:template match="comment|author|version" mode="one">
<xsl:copy>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>

<xsl:template match="comment|author|version"/>

<xsl:template match="interfaces|superclass|classname|name|type|modifiers|package|import|importpkg">
<xsl:copy-of select="."/>
</xsl:template>

</xsl:stylesheet>