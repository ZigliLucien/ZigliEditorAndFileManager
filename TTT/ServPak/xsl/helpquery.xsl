<?xml version="1.0"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">


   <xsl:output method="xml"/>


   <xsl:param name="value"/>

   <xsl:template match="/*">
<xsl:copy>
 <xsl:for-each select="/*/*[child::node()/@key=$value]">
   <xsl:apply-templates/>
       </xsl:for-each>
</xsl:copy>
   </xsl:template>

<xsl:template match="/">
<xsl:copy>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>



   <xsl:template match="*|@*">
     <xsl:copy>
       <xsl:apply-templates select="node()|@*"/>
     </xsl:copy>
   </xsl:template>

</xsl:stylesheet>			
