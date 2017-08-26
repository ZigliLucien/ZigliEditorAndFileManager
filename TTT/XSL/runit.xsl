<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

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