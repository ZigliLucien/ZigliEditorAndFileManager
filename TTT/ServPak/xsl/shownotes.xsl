<?xml version="1.0"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>

   <xsl:param name="value"/>

	<xsl:template match="notesml">
	<html>
		<body>
			<xsl:apply-templates/>
		</body>
	</html>
	</xsl:template>

     <xsl:template match="word">
	<xsl:if test="@link=$value">
	<xsl:apply-templates/>
	</xsl:if>
       </xsl:template>

	<xsl:template match="*|@*">
	       <xsl:copy>
		 <xsl:apply-templates select="node()|@*"/>
	       </xsl:copy>
	     </xsl:template>

  </xsl:stylesheet>			
