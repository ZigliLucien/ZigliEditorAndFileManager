<?xml version="1.0" encoding="UTF-8"?>
 <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
   <xsl:output method="html"/>
 
  <xsl:template match="tpwm">
     <html>
       <xsl:apply-templates/>
     </html>
   </xsl:template>

<xsl:template match="title">
       <head>
	 <title> <xsl:value-of select="(.)"/> </title>
<xsl:text>
</xsl:text>
<xsl:apply-templates select="../style" mode="one"/>
<xsl:text>
</xsl:text>
       </head>
	 <h1> <xsl:value-of select="(.)"/>  </h1>
   </xsl:template>

   <xsl:template name="dotd">
<xsl:text disable-output-escaping="yes">&lt;td align="center"&gt;</xsl:text>
   </xsl:template>

 <xsl:template name="closetd">
     <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; 
   </xsl:text>
 </xsl:template>

 <xsl:template match="itemize">
   <ul>   <xsl:apply-templates/> </ul>
 </xsl:template>

 <xsl:template match="enumerate">
   <ol>   <xsl:apply-templates/> </ol>
 </xsl:template>

 <xsl:template match="list">
   <dl>   <xsl:apply-templates/> </dl>
 </xsl:template>

 <xsl:template match="description">
   <dl>   <xsl:apply-templates/> </dl>
 </xsl:template>

 <xsl:template match="item">
   <li>   <xsl:apply-templates/> </li>
 </xsl:template>

 <xsl:template match="ditem">
   <dt><xsl:apply-templates/> </dt>
 </xsl:template>

 <xsl:template match="dterm">
   <dd><xsl:apply-templates/> </dd>
 </xsl:template>

 <xsl:template match="xmth">
   <table><tr>
<xsl:apply-templates/> 
<xsl:call-template name="closetd"/>
</tr></table>
 </xsl:template>

 <xsl:template match="display">
   <p></p><table align="center"><tr>
   <xsl:apply-templates/> 
<xsl:call-template name="closetd"/>
 </tr></table><p></p>
 </xsl:template>

 <xsl:template match="bordermatrix[@width]">
   <p></p><table align="center" border="1" cellpadding="2" cellspacing="0" width="{@width}"><tr>
   <xsl:apply-templates/> 
<xsl:call-template name="closetd"/>
 </tr></table><p></p>
 </xsl:template>

 <xsl:template match="bordermatrix">
   <p></p><table border="1" align="center" cellpadding="2" cellspacing="0"><tr>
   <xsl:apply-templates/> 
<xsl:call-template name="closetd"/>
 </tr></table><p></p>
 </xsl:template>

<xsl:template match="frac">
<td align="center">
 <xsl:apply-templates/>
 </td><xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="numer">
<xsl:apply-templates/> <br/>
<hr noshade="noshade" align="center" width="{../@width}"/> 
 </xsl:template>

<xsl:template match="denom">
 <xsl:apply-templates/>
 </xsl:template>

 <xsl:template match="prod">
<td align="center"><xsl:apply-templates select="uu"/>  
<br/><font size="+3"> &#x220F; </font> <br/>
  <xsl:apply-templates select="ll"/>  </td><xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="int">
   <td align="center">&#x00A0; &#x00A0;<xsl:apply-templates select="uu"/>  
<br/><font size="+3"> &#x222B; </font> <br/>
  <xsl:apply-templates select="ll"/>  </td><xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="sum">
<td align="center"><xsl:apply-templates select="uu"/>  
<br/><font size="+3"> &#x2211; </font> <br/>
  <xsl:apply-templates select="ll"/>  </td><xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="choose">
<td><font size="+2">(</font></td><td align="center"> 
  <xsl:apply-templates select="uu"/> <br/><xsl:apply-templates select="ll"/>
</td><td><font size="+2">)</font></td><xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="sumtype">
   <td align="center">
   <font size="{@limsize}"><xsl:apply-templates select="uu"/></font> 
   <br/><xsl:apply-templates select="symbol"/><br/>
   <font size="{@limsize}"><xsl:apply-templates select="ll"/></font> </td>
 <xsl:call-template name="dotd"/>
 </xsl:template>

 <xsl:template match="symbol">
   <font size="+{@symsize}"><xsl:apply-templates/></font>
 </xsl:template>

 <xsl:template match="cr">
   <br/>
 </xsl:template>

 <xsl:template match="display/ams"> 
<xsl:text disable-output-escaping="yes">
&lt;td align="center" width="5%"&gt;&lt;br/&gt;&lt;/td&gt;&lt;td&gt;
</xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/ams[position()=1]"> 
<xsl:text disable-output-escaping="yes">
&lt;td align="center" width="5%" bgcolor="#ffcc00"&gt;
</xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/ams[not(position()=1)]"> 
<xsl:text disable-output-escaping="yes">
&lt;td align="center" width="5%" bgcolor="lightgreen"&gt;
</xsl:text>
 </xsl:template>

 <xsl:template match="amd">
<xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="5%"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amcx[not(position()=1)]">
    &#x00A0;&#x00A0; <xsl:text disable-output-escaping="yes"> 
    &lt;/td&gt; &lt;td align="center" width="5%" bgcolor="cyan" class="a"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amcx[position()=1]">
    &#x00A0;&#x00A0;  <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="5%" bgcolor="lightblue"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amcf[not(position()=1)]">
    &#x00A0;&#x00A0; <xsl:text disable-output-escaping="yes"> 
    &lt;/td&gt; &lt;td align="center" width="15%" bgcolor="cyan" class="a"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amcf[position()=1]">
    &#x00A0;&#x00A0;  <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="15%" bgcolor="lightblue"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amc[position()=1]">
    &#x00A0;&#x00A0;  <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="15%" bgcolor="lightblue"&gt;
   </xsl:text>
 </xsl:template>

<xsl:template match="bordermatrix/amc[not(position()=1)]">
   &#x00A0;&#x00A0;   <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="15%" bgcolor="cyan" class="a"&gt;
   </xsl:text>
 </xsl:template>

 <xsl:template match="display/amc">
     <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="center" width="5%" &gt;&lt;br/&gt;&lt;/td&gt; &lt;td
   </xsl:text>
 </xsl:template>

 <xsl:template match="amr">
     <xsl:text disable-output-escaping="yes"> 
     &lt;/td&gt; &lt;td align="right"&gt;
   </xsl:text>
 </xsl:template>

 <xsl:template match="bordermatrix/cr|display/cr|xmth/cr">
   <xsl:text disable-output-escaping="yes">
     &lt;/td&gt; &lt;/tr&gt; &lt;tr&gt;
</xsl:text>
 </xsl:template>

  <xsl:template match="sub|sup">
   <xsl:copy>
     <xsl:apply-templates/>
   </xsl:copy>
 </xsl:template>

 <xsl:template match="hisup">
   <td align="left"><sup><xsl:apply-templates/></sup><br/></td> <td>&#x00A0;</td>
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

 <xsl:template match="ff">
   <font face="symbol">  <xsl:apply-templates/> </font>
 </xsl:template>

 <xsl:template match="label">
   <a name="{@id}"></a>
 </xsl:template>

 <xsl:template match="bibitem">
   <li>   <a name="{@id}"></a>
   <xsl:apply-templates/></li>
 </xsl:template>

 <xsl:template match="ref|cite">
   <a href="#{@id}"><xsl:value-of select="@id"/> </a>
 </xsl:template>

 <xsl:template match="comment">
	   <xsl:comment> 
   <xsl:apply-templates/> 
	 </xsl:comment>	
 </xsl:template>

 <xsl:template match="skip">
   <p/> &#x00A0;<br/>
 </xsl:template>

 <xsl:template match="abstract">
 <br/>   <b><xsl:value-of select="name()"/> </b>&#x00A0;&#x00A0; 
   <blockquote><tt>
<xsl:apply-templates/>
   </tt></blockquote>
 </xsl:template>

 <xsl:template match="section">
   <p>   <h2><xsl:value-of select="@id"/> </h2></p>
<blockquote>
   <xsl:apply-templates/> 
</blockquote>
 </xsl:template>

 <xsl:template match="subsection|subsubsection|paragraph|subparagraph">
   <p>   <h3><xsl:value-of select="@id"/> </h3></p>
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

<xsl:template match="style" mode="one">
	<style>
<xsl:apply-templates/>
	</style>
</xsl:template>

<xsl:template match="style"/>

 <xsl:template match="*|@*">
   <xsl:copy> 
   <xsl:apply-templates select="node()|@*"/>
   </xsl:copy>
 </xsl:template>
</xsl:stylesheet>
