
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:param name="value"/>


  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>


  <xsl:template match="/*/*/*[position()=last()]">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
    <xsl:text>
    </xsl:text>
    <xsl:element name="{$value}"> - </xsl:element>
       </xsl:template>


  <xsl:template match="*|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
       </xsl:template>


    </xsl:stylesheet>
