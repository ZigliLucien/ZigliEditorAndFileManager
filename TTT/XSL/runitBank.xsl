<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:template name="runit">
     <table>
      <xsl:for-each select="*[not(name()='month')]">
       <tr>     
	 <td bgcolor="#eeeeee"><xsl:value-of select="name()"/></td>
	 <td bgcolor="#ffeedd"> <xsl:value-of select="."/></td>
       </tr>
   </xsl:for-each>
     </table>
     <p/>
  </xsl:template>

</xsl:stylesheet>			