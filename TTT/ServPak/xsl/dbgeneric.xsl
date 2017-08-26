<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

<xsl:param name="value"/>

<xsl:template match="/*" mode="one">
  <xsl:value-of select="translate(name(),'_',' ')"/>
</xsl:template>


  <xsl:template match="/">
    <html>
	<head><title><xsl:apply-templates select="/*" mode="one"/></title>
<style type="text/css">

	TD {
	    font-family: Arial, Helvetica, sans-serif;
	    font-size: 75%;
	    font-weight: normal;
	    color: "#000000"
	}

	TH {
            text-transform: capitalize;
            font-family: Times;
	    font-size: 16pt;
	    font-weight: bold;
	    color: "#0000ff"
	}
</style>
</head>
      <body bgcolor="ffffff">
<h1> <xsl:apply-templates select="/*" mode="one"/> </h1>
<table align="center" border="1" width="95%" cellpadding="1">
	  <xsl:apply-templates/>	
	</table>
<p/>
	  <table>
	    <tr><td width="30%">	
	      <a href="DBgo.jav?change=yes"> Edit table </a>&#160;&#160;
	    </td>
	    <td>
	      <br/>	    </td><td>
	  <a href="DBgo.jav?addrow=yes"> Add a new row </a>
	</td><td width="25%"><br/></td>
	<td>	
<form action="DBgo.jav" method="get">
  Add a field <br/>(lowercase, start with 'zz' if numerical, like zzcat for cat) 
<input name="addfield" size="10"/>
</form>
      </td></tr></table>
<br/>
<a href="DBgo.jav?formentry=yes"> Enter new row via form </a>
<p/>

Click	<a href="DBgo.jav?"> 
     --&gt; here &lt;-- </a> when finished adding rows/fields or editing is complete. 

	<p/>&#160;<br/>
 &#160;&#160;&#160;&#160; -&gt; Go to: <a href="DBgo.jav?searchsort=yes"> Search/Sort Views </a>
	  	  &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
-&gt;-&gt; Go to: <a href="DBgo.jav?analyze=yes"> DB operations  </a>
&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
-&gt;-&gt; -&gt; Go to: <a href="DBgo.jav?rcops=yes"> Row &amp; Column operations  </a>
<p/>&#160;<br/>
&#160;&#160;&#160;&#160;&lt;- Back to: <a href="home?home"> <xsl:value-of select="$value"/> </a>
      </body>
    </html>
  </xsl:template>

<xsl:template match="/*/*[position()!=1]">
	  <tr>
	  <xsl:apply-templates/>	
	</tr>	
</xsl:template>


	<xsl:template match="/*/*/*">
	  <xsl:call-template name="runit"/>
	</xsl:template>

	<xsl:template match="/*/*[position()=1]">
	  <tr>
	  <xsl:for-each select="*">
<th>
      <xsl:choose>
	<xsl:when test="starts-with(name(),'zz')">
	<xsl:value-of select="substring-after(name(),'zz')"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="name()"/>
      </xsl:otherwise>
    </xsl:choose>
</th>
          </xsl:for-each>
          </tr>
<tr>
	  <xsl:for-each select="*">
<xsl:call-template name="runit"/>
          </xsl:for-each>
</tr>
         </xsl:template>


<xsl:template name="runit">
<td align="center">
  <xsl:choose>
    <xsl:when test="(.)=''">
      <br/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
</xsl:otherwise>
</xsl:choose>
</td>
</xsl:template>

<xsl:template match="br|em|a|@href">
<xsl:copy>
<xsl:apply-templates select="@*"/>
<xsl:apply-templates/>
</xsl:copy>
</xsl:template>

    </xsl:stylesheet>
