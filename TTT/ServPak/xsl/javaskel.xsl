<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="text"/>

  <xsl:template match="/">
	<xsl:apply-templates/>
    }
  </xsl:template>

<xsl:template match="package">package <xsl:value-of select="."/>;
</xsl:template>

<xsl:template match="importpkg">import <xsl:value-of select="."/>.*;</xsl:template>

<xsl:template match="import">import <xsl:value-of select="."/>;</xsl:template>

<xsl:template match="class">
/**
<xsl:value-of select="comment"/>
@author <xsl:value-of select="author"/>
@version <xsl:value-of select="version"/>
*/

<xsl:value-of select="modifiers"/> class <xsl:value-of select="name"/>  extends <xsl:value-of select="superclass"/> <xsl:value-of select="interfaces"/> {
</xsl:template>

<xsl:template match="constructor">
/**
<xsl:value-of select="comment"/>
*/

<xsl:value-of select="modifiers"/><xsl:value-of select="name"/> {}
</xsl:template>

<xsl:template match="field">
/**
<xsl:value-of select="comment"/>
*/

<xsl:value-of select="modifiers"/><xsl:value-of select="type"/><xsl:value-of select="name"/>;
</xsl:template>

<xsl:template match="method">
/**
<xsl:value-of select="comment"/>
*/

<xsl:value-of select="modifiers"/><xsl:value-of select="type"/><xsl:value-of select="name"/>{}
</xsl:template>

    </xsl:stylesheet>
