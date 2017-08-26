<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:include href="runitBank.xsl"/>

   <xsl:output method="html"/>


   <xsl:param name="value"/>
   

      <xsl:template match="/">

     <html><body bgcolor="white">

       <h1> DataBase List </h1>

       <xsl:apply-templates/>

   </body> </html>
   </xsl:template>

       <xsl:template match="/*/*">
	 <xsl:call-template name="runit"/>
       </xsl:template>

       <xsl:template match="*|@*">
	 <xsl:copy><xsl:apply-templates select="node()|@*">
	   <xsl:sort select="*[name()=substring-before($value,'-')]"/>
	   <xsl:sort select="*[name()=substring-after($value,'-')]"/>
     </xsl:apply-templates>
         </xsl:copy>
       </xsl:template>

</xsl:stylesheet>			
