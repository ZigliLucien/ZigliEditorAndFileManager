<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

  <xsl:param name="value"/>


<xsl:param name="value1" select="substring-before($value,'!')"/>

<xsl:param name="direx" select="substring-after($value,'!')"/>
<xsl:param name="direcout" select="substring-before($direx,'!')"/>
<xsl:param name="predirec" select="substring-after($direx,'!')"/>

<xsl:param name="direc" select="substring-before($predirec,'!')"/>
<xsl:param name="precall" select="substring-after($predirec,'!')"/>

<xsl:param name="processcall" select="substring-before($precall,'!')"/>
<xsl:param name="prebasedir" select="substring-after($precall,'!')"/>

<xsl:param name="basedir" select="substring-before($prebasedir,'!')"/>
<xsl:param name="isLocal" select="substring-after($prebasedir,'!')"/>

<xsl:template match="/*" mode="one">
 <xsl:value-of select="$direcout"/>
 </xsl:template>


  <xsl:template match="/">
    <html>
	<head><title><xsl:apply-templates select="/*" mode="one"/></title>
<style type="text/css">

	         span.s{font-variant: small-caps; color: gray;
		      font-weight: lighter}
	         span.v{font-variant: small-caps; 
		      font-weight: lighter}
	         span.c{font-variant: small-caps; color: red;
		      font-weight: lighter}
	         span.m{font-variant: small-caps; color: darkred;
		      font-weight: lighter}
	         span.d{font-variant: small-caps; color: orange;
		      font-weight: lighter}
	         span.e{font-variant: small-caps; color: blue;
		      font-weight: lighter}
	         span.q{font-variant: small-caps; color: green;
		      font-weight: lighter}
	         span.a{font-variant: small-caps; color: magenta;
		      font-weight: lighter}
		
		input.x{background: #ffffff; color: #5555ff; 
		font-size: 80%; border: 0 }
                        input.x:hover{color: #ee9909; text-decoration: underline}

		input.y{background: #eeeeee; color: #5555ff; font-size: 80%; border: 0}
                        input.y:hover{color: #cc9908; text-decoration: underline}

		a.x:link{color: #888888; font-size: 90%}
		a.x:visited{color: #888888}
		a.x:hover{ color: #cc9908; text-decoration: underline}
		a.y:link{color: #44bbbb; font-size: 90%}
		a.y:visited{color: #44bbbb}
		a.y:hover{ color: #cc9908; text-decoration: underline}
		a.d:link{ color: #5588ff; font-size: 90%; background: white;}
		a.d:visited{ color: #5588ff; font-size: 90%;}
		a.d:hover{ color: #cc9908; text-decoration: underline;}
		a.z:hover{ color: #cc9908; text-decoration: underline;}
		a.u:hover{ color: #bb88ff;}

		a.w:link{color: #4444ee}
		a.w:visited{color: #4444ee}
		a.w:hover{ color: #cc9908;}

	        tr.a{background: #ffffee;}     
	        tr.b{background: #eeffff;}
	        th{font-family: helvetica,sans-serif,arial;
			font-variant: small-caps;
			font-weight: lighter}
</style>

</head>
      <body bgcolor="ffffff">
<form action="FileOps.jav" method="GET">
<input type="radio" name="fileops" value="SSS">  
<xsl:if test="$processcall='SSS'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="s"> see </span>
<input type="radio" name="fileops" value="VVV">  
<xsl:if test="$processcall='VVV'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="v"> view</span>
<input type="radio" name="fileops" value="CCC">
<xsl:if test="$processcall='CCC'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="c">copy</span>
<input type="radio" name="fileops" value="MMM">
<xsl:if test="$processcall='MMM'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="m">move</span>
<input type="radio" name="fileops" value="XXX">
<xsl:if test="$processcall='XXX'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="d"> dele </span>
<input type="radio" name="fileops" value="EEE">
<xsl:if test="$processcall='EEE'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="e">  edit </span>
<input type="radio" name="fileops" value="QQQ"> 
<xsl:if test="$processcall='QQQ'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="q">  quik </span>
<input type="radio" name="fileops" value="AAA">
<xsl:if test="$processcall='AAA'"><xsl:attribute name="checked">yes</xsl:attribute></xsl:if>
</input><span class="a"> note </span>

<p/>
<table align="center" width="98%" cellpadding="0" cellspacing="0">
	  <tr>
<!-- th width="8%"> <br/></th -->
<th width="30%">Filename</th>
<th width="25%">Size &#160;&#160;&#160; Date &#160;&#160;&#160; Time</th> 
<th width="35%">Notes</th>
          </tr>
          <xsl:apply-templates/>

	</table>
</form>
       </body>
     </html>
  </xsl:template>


  <xsl:template match="/*">
          <xsl:choose>
	<xsl:when test="$value1 !='timekey'">
	  <xsl:apply-templates>	
           <xsl:sort select="*[name()=$value1]"/>
	 </xsl:apply-templates>
	 </xsl:when>
	 <xsl:otherwise>
	   <xsl:apply-templates>
	   <xsl:sort select="*[name()=$value1]" order="descending" data-type="number"/>
	 </xsl:apply-templates>
	 </xsl:otherwise>
       </xsl:choose>
       </xsl:template>


<xsl:template match="/*/filedata">

   <tr>

<xsl:attribute name="class">
<xsl:if test="number(@parity)=1">a</xsl:if>
<xsl:if test="number(@parity)=0">b</xsl:if>
  </xsl:attribute>
	  <xsl:apply-templates select="filename"/>	
	  <xsl:apply-templates select="sdt"/>	
	  <xsl:apply-templates select="annotation"/>	
	</tr>
</xsl:template>

<xsl:template match="/*/*/sdt">

  <td align="center" width="25%" class="z"> 
<font color="#888888"><xsl:value-of select="@size"/></font> &#160;
<font color="#888888"><xsl:value-of select="."/></font> &#160;
<font color="#888888"><xsl:value-of select="@time"/></font>
 </td>
	</xsl:template>

<xsl:template match="/*/*/annotation">
  <td align="center" width="35%" class="z"><xsl:apply-templates/></td>
	</xsl:template>

<xsl:template match="/*/*/filename">

  <xsl:param name="file"><xsl:value-of select="../@entry"/> </xsl:param>
  <xsl:param name="name"><xsl:value-of select="node()"/> </xsl:param>
  <xsl:param name="isDir"><xsl:value-of select="@type"/> </xsl:param>

<!-- td align="center">
   <xsl:choose>

	<xsl:when test="$isDir='dir'">
	
		-x-x-

	 </xsl:when>

	 <xsl:otherwise>

<xsl:choose>
	<xsl:when test="$isLocal='true'">
<font size="-1">
<input type="submit" class="x" value="Ops"  name="{concat(concat($direc,$name),'.x')}"/> 
</font>
	</xsl:when>
	 <xsl:otherwise>
	<input type="submit" class="y" name="{concat(concat($direc,$name),'.x')}" value="Ops"/> 
	 </xsl:otherwise>
       </xsl:choose>

	 </xsl:otherwise>
       </xsl:choose>
</td -->

<td align="center" width="30%">
<xsl:choose>

	<xsl:when test="$isDir='dir'">
		 <a class="d" href="{concat($direc,$name)}">
		<tt> /<xsl:value-of select="$name"/> </tt></a>
	</xsl:when>

	 <xsl:otherwise>
<input type="submit" class="x" 
	name="{concat(concat($direc,$name),'@!!@x')}" value="{$file}"/> 
  <!-- a class="z" href="{concat($direc,$name)}"> <xsl:value-of select="$file"/> </a -->
	 </xsl:otherwise>
       </xsl:choose>

  </td>
	</xsl:template>

<xsl:template match="br|em|a|font|tt">
<xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="comment">
	<comment id="EOF"/>
</xsl:template>

<xsl:template match="timekey|filetype|key1|key2|plainname"/>

    </xsl:stylesheet>