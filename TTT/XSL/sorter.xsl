<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>

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
	   <xsl:sort select="*[name()=$value1]" data-type="{$type1}"/>
	   <xsl:sort select="*[name()=$value2]" data-type="{$type2}"/>
     </xsl:apply-templates>
         </xsl:copy>
       </xsl:template>


   <xsl:template name="runit">
     <table>
      <xsl:for-each select="*">
	<tr>     
	 <td bgcolor="#eeeeee">
	  <xsl:if test="starts-with(name(),'zz')">
           <xsl:value-of select="substring-after(name(),'zz')"/>
           </xsl:if>
	   <xsl:if test="not(starts-with(name(),'zz'))">
	   <xsl:value-of select="name()"/>
           </xsl:if>
         	</td>
	 <td bgcolor="#ffeedd"> <xsl:apply-templates select="."/></td>
       </tr>
   </xsl:for-each>
     </table>
     <p/>
  </xsl:template>

</xsl:stylesheet>			
