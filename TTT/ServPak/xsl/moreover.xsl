<?xml version="1.0" encoding="ISO-8859-1"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

      <xsl:template match="/">

  <HTML>
  <HEAD>
    <style>
A.one {color: #00aa00}
    </style>
  <TITLE>moreover...</TITLE>
  </HEAD>
  <BODY BGCOLOR="eeeeee">
<h5> NewsFeed courtesy of MoreOver.com </h5>
  <DIV ALIGN="center">
  <TABLE BGCOLOR="eeeeee" BORDER="0" CELLPADDING="4" CELLSPACING="0" WIDTH="100%">

        <xsl:for-each select="moreovernews/article">
               <TR VALIGN="middle">
                 <TD ALIGN="left" BGCOLOR="eeeeee">
		   <xsl:number/>. &#160;
  <A>
		     
                     <xsl:attribute name="HREF">
                       <xsl:value-of select="url"/>
                     </xsl:attribute>
                         <xsl:value-of select="headline_text"/>
		   		       </A>
		   &#160; &#64; &#160;	   
		       <A class="one">
                     <xsl:attribute name="HREF">
                       <xsl:value-of select="document_url"/>
                     </xsl:attribute>
                      <xsl:value-of select="source"/>
		    		   </A>
		   <tt>                  
                  &#160; (<xsl:value-of select="harvest_time"/> GMT)
		   </tt>
                 </TD>
	       </TR>
		</xsl:for-each>
	   </TABLE>
  </DIV>
  </BODY>
  </HTML>
      </xsl:template>
    </xsl:stylesheet>
