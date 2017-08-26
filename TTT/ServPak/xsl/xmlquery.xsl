<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">


   <xsl:output method="xml"/>


   <xsl:param name="value"/>

   <xsl:template match="/">
     <xsl:copy>
       <xsl:apply-templates/>
     </xsl:copy>
     </xsl:template>

     <xsl:template match="/*">
       <xsl:copy>
          <xsl:choose>
	<xsl:when test="$value !='timekey'">
	  <xsl:apply-templates>	
           <xsl:sort select="*[name()=$value]"/>
	 </xsl:apply-templates>
	 </xsl:when>
	 <xsl:otherwise>
	   <xsl:apply-templates>
	   <xsl:sort select="*[name()=$value]" order="descending" data-type="number"/>
	 </xsl:apply-templates>
	 </xsl:otherwise>
       </xsl:choose>
     </xsl:copy>
       </xsl:template>



       <xsl:template match="*|@*">
       <xsl:copy>
	 <xsl:apply-templates select="node()|@*"/>
       </xsl:copy>
     </xsl:template>

  </xsl:stylesheet>			
