<?xml version="1.0" encoding="UTF-8"?>

 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

   <xsl:output method="html"/>

    <xsl:param name="value"/>

  <xsl:template match="tpwm">
     <html>
       <xsl:apply-templates/>
     </html>
   </xsl:template>

<xsl:template match="title">
       <head>
  	<title> <xsl:value-of select="translate(node(),'_',' ')"/> </title>
<xsl:text>
</xsl:text>
<xsl:apply-templates select="../style" mode="one"/>
<xsl:text>
</xsl:text>
       </head>
	 <h1> <xsl:value-of select="translate(node(),'_',' ')"/> </h1>
   </xsl:template>

  <xsl:template match="itemize">
   <ul>   <xsl:apply-templates/> </ul>
 </xsl:template>

 <xsl:template match="enumerate">
   <ol>   <xsl:apply-templates/> </ol>
 </xsl:template>

 <xsl:template match="dlist">
   <dl>   <xsl:apply-templates/> </dl>
 </xsl:template>

 <xsl:template match="item">
   <li>   <xsl:apply-templates/> </li>
 </xsl:template>

 <xsl:template match="itemitem">
   <br/> &#x00A0; &#x00A0;&#x00A0;
 </xsl:template>

 <xsl:template match="ditem">
   <dt><xsl:apply-templates/> </dt>
 </xsl:template>

 <xsl:template match="dterm">
   <dd><xsl:apply-templates/> </dd>
 </xsl:template>

 <xsl:template match="xmth">
   <table><tr><xsl:apply-templates/></tr></table>
 </xsl:template>

 <xsl:template match="display">
   <p></p><table align="center">
   <xsl:apply-templates/> 
 </table><p></p>
 </xsl:template>

 <xsl:template match="bordermatrix">
   <p></p><table border="1" align="center" cellpadding="2" cellspacing="0">
   <xsl:apply-templates/> 
 </table><p></p>
 </xsl:template>

<xsl:template match="frac">

<xsl:param name="numstring"><xsl:value-of select="numer"/></xsl:param>
<xsl:param name="numsize"><xsl:value-of select="5*string-length($numstring)"/></xsl:param>

<xsl:param name="denstring"><xsl:value-of select="denom"/></xsl:param>
<xsl:param name="densize"><xsl:value-of select="5*string-length($denstring)"/></xsl:param>

<xsl:param name="fracdiff"><xsl:value-of select="number($densize)-number($numsize)"/></xsl:param>

<xsl:param name="numshift">
<xsl:choose><xsl:when test="number($fracdiff)=0">
	<xsl:value-of select="0"/>
</xsl:when> <xsl:otherwise>
	<xsl:value-of select="number($fracdiff)-5"/>
</xsl:otherwise>
</xsl:choose>
</xsl:param>
<xsl:param name="denshift"><xsl:value-of select="-number($fracdiff)-5"/></xsl:param>

<xsl:param name="fracwidth">
<xsl:choose><xsl:when test="number($fracdiff)&lt;0">
	<xsl:value-of select="2*number($numsize)-2"/>
</xsl:when> <xsl:otherwise>
	<xsl:value-of select="2*number($densize)-2"/>
</xsl:otherwise>
</xsl:choose>
</xsl:param>

<xsl:choose><xsl:when test="number($fracdiff)&lt;0">
 <td>
<xsl:apply-templates select="numer"/>
<hr noshade="noshade" align="center" width="{$fracwidth}"/> 
<img width="{$denshift}" height="0"/><xsl:apply-templates select="denom"/>
</td>

</xsl:when> <xsl:otherwise>

 <td>
<img width="{$numshift}" height="0"/><xsl:apply-templates select="numer"/>
<hr noshade="noshade" align="center" width="{$fracwidth}"/> 
<xsl:apply-templates select="denom"/>
</td>

</xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="frac[@width]">

 <td>
<xsl:apply-templates select="numer"/>
<hr noshade="noshade" align="center" width="{@width}"/> 
<xsl:apply-templates select="denom"/>
</td>
 </xsl:template>

 <xsl:template match="numer">
&#x00a0;<xsl:apply-templates/> <br/>
 </xsl:template>

<xsl:template match="denom">
 &#x00a0;<xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="prod">
<td><xsl:apply-templates select="uu" mode="one"/>  
<br/><font size="+3"> &#x220F; </font> <br/>
  <xsl:apply-templates select="ll" mode="one"/> </td>
<td><xsl:apply-templates/></td>
 </xsl:template>

 <xsl:template match="int">
  <td> &#x00A0; &#x00A0;<xsl:apply-templates select="uu" mode="one"/>  
<br/><font size="+3"> &#x222B; </font> <br/>
  <xsl:apply-templates select="ll" mode="one"/> </td>
<td><xsl:apply-templates/></td>
 </xsl:template>

 <xsl:template match="sum">
<td><xsl:apply-templates select="uu" mode="one"/>  
<br/><font size="+3"> &#x2211; </font> <br/>
  <xsl:apply-templates select="ll" mode="one"/> </td> 
<td><xsl:apply-templates/></td>
 </xsl:template>

 <xsl:template match="choose">
<td><font size="+3">(</font></td>
 <td> <xsl:apply-templates select="uu" mode="one"/> <br/>
<xsl:apply-templates select="ll" mode="one"/></td>
<td><font size="+3">)</font></td>
 </xsl:template>

 <xsl:template match="sumtype">   
  <td> <font size="{@limsize}"><xsl:apply-templates select="uu" mode="one"/></font> 
   <br/><xsl:apply-templates select="symbol" mode="one"/><br/>
             <font size="{@limsize}"><xsl:apply-templates select="ll" mode="one"/></font> </td>
	<td><xsl:apply-templates/></td>
  </xsl:template>

 <xsl:template match="symbol">
   <font size="+{@symsize}"><xsl:apply-templates/></font>
 </xsl:template>

 <xsl:template match="symbol" mode="one">
   <font size="+{@symsize}"><xsl:apply-templates/></font>
 </xsl:template>

 <xsl:template match="cr">
   <br/>
 </xsl:template>

 <xsl:template match="row">
<tr> <xsl:apply-templates/> </tr>
 </xsl:template>

  <xsl:template match="amc|_">
  <td align="center"><xsl:apply-templates/></td>
 </xsl:template>

 <xsl:template match="aml|_l">
<td><xsl:apply-templates/>&#x00A0;&#x00A0;</td>
 </xsl:template>

 <xsl:template match="amr|_r">
<td>&#x00A0;&#x00A0;<xsl:apply-templates/></td>
  </xsl:template>

  <xsl:template match="sub|sup">
   <xsl:copy>
     <xsl:apply-templates/>
   </xsl:copy>
 </xsl:template>

 <xsl:template match="hisup">
   <td align="left"><sup><xsl:apply-templates/></sup><br/><br/></td> <td>&#x00A0;</td>
 </xsl:template>

 <xsl:template match="thm|theorem">
   <br/>   <b>Theorem.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="lemma">
   <br/>   <b>Lemma.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="example">
   <br/>   <b>Example.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="definition">
   <br/>   <b>Definition.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="proposition">
   <br/>   <b>Proposition.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="notation">
   <br/>   <b>Notation.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="corollary">
   <br/>   <b>Corollary.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="proof">
   <br/>   <b><em>Proof.</em></b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

<xsl:template match="remark">
   <br/>   <b>Remark.</b>&#x00A0;&#x00A0; <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="bf|b">
     <b>   <xsl:apply-templates/> </b>
 </xsl:template>

 <xsl:template match="it|i">
     <i>   <xsl:apply-templates/> </i>
 </xsl:template>

 <xsl:template match="sf|tt">
     <tt>   <xsl:apply-templates/> </tt>
 </xsl:template>

 <xsl:template match="sl|em">
   <em>   <xsl:apply-templates/> </em>
 </xsl:template>

 <xsl:template match="label">
   <a name="{@id}"></a>
 </xsl:template>

  <xsl:template match="ref|cite">
   <a href="#{@id}"><xsl:value-of select="@id"/> </a>
 </xsl:template>

 <xsl:template match="aref">
   <a href="{@id}"><xsl:apply-templates/> </a>
 </xsl:template>

 <xsl:template match="comment">
	   <xsl:comment> 
   <xsl:apply-templates/> 
	 </xsl:comment>	
 </xsl:template>

 <xsl:template match="skip">
   <p/> &#x00A0;<br/>
 </xsl:template>

 <xsl:template match="quad">
    &#x00A0; &#x00A0;&#x00A0;
 </xsl:template>

<xsl:template match="nbsp">
    &#x00A0; 
 </xsl:template>

 <xsl:template match="qquad">
    &#x00A0; &#x00A0;&#x00A0; &#x00A0; &#x00A0;
 </xsl:template>

 <xsl:template match="abstract">
 <br/>   <b><xsl:value-of select="name()"/> </b>&#x00A0;&#x00A0; 
   <blockquote><tt>
	<xsl:apply-templates/>
   </tt></blockquote>
 </xsl:template>

 <xsl:template match="section">
   <p/>  
<blockquote>
 <h2><xsl:value-of select="@id"/> </h2>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

 <xsl:template match="subsection">
   <p/> 
<blockquote>
  <h3><xsl:value-of select="@id"/> </h3>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

<xsl:template match="subsubsection">
   <p/>   
<blockquote>
<h4><xsl:value-of select="@id"/> </h4>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

<xsl:template match="paragraph">
   <p/>  
<blockquote>
 <h5><xsl:value-of select="@id"/> </h5>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

<xsl:template match="subparagraph">
   <p/>   
<blockquote>
<h6><xsl:value-of select="@id"/> </h6>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

<xsl:template match="notes"><a>
<xsl:attribute name="href">ShowNotes.jav?file=<xsl:value-of select="$value"/>&amp;link=<xsl:value-of select="@link"/></xsl:attribute>
<xsl:value-of select="."/></a>
</xsl:template>

 <xsl:template match="appendix">
   <h3> Appendix</h3><br/>
 </xsl:template>

 <xsl:template match="footnote">
   <xsl:copy> 
   <xsl:apply-templates/> 
 </xsl:copy>
 </xsl:template>

 <xsl:template match="idx">
   <a href="index.html"> <xsl:apply-templates/> </a>
 </xsl:template>

 <xsl:template match="thebibliography">
   <h3> References </h3>
   <ol>   
	<xsl:apply-templates/> 
   </ol>
</xsl:template>

<xsl:template match="bibitem">
   <li>   <a name="{@id}"></a>
   <xsl:apply-templates/></li>
	<p/>
 </xsl:template>

<xsl:template match="uu|ll" mode="one">
<xsl:apply-templates/>
</xsl:template>

 <xsl:template match="style" mode="one">
   <xsl:copy> 
   <xsl:apply-templates/>
   </xsl:copy>
 </xsl:template>

<xsl:template match="style|uu|ll|sumtype/symbol"/>

<xsl:template match="hh">
</xsl:template>

<xsl:template match="hah">
</xsl:template>




<xsl:template match="*|@*">
<xsl:copy>
   <xsl:apply-templates select="node()|@*"/> 
</xsl:copy>
 </xsl:template>

</xsl:stylesheet>
