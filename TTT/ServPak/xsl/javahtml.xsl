<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

  <xsl:template match="java">
    <html>
      <head><title><xsl:value-of select="//class/@name"/></title></head>
      <body bgcolor="ffffff">
	<h1><xsl:value-of select="//class/@name"/></h1>
<code>
    <xsl:apply-templates/>
</code>
  </body>
</html>
  </xsl:template>

  <xsl:template match="class">
<p/><font color="pink"><xsl:value-of select="concat(@presc,' ')"/></font>    
 <font color="green"> class </font><xsl:value-of select="concat(' ',@name,' ')"/> 
 <em><xsl:value-of select="@desc"/></em>{ <p>
   <blockquote>  <xsl:apply-templates/></blockquote>
 </p> 
}
  </xsl:template>

  <xsl:template match="constructor">
<p/>    <tt> <xsl:value-of select="concat(@presc,' ')"/> </tt>
<strong> <font color="red"><xsl:value-of select="../../class/@name"/></font></strong>
(<xsl:apply-templates select="args"/>)
 <em><xsl:value-of select="concat(' ',@desc)"/></em>{<p/>
   <blockquote><xsl:apply-templates select="exec"/></blockquote>
      <br/>}<p/>
    </xsl:template>

  <xsl:template match="package">
    <strong>  <font color="blue">package</font> </strong><xsl:value-of select="(.)"/>; <br/>
  </xsl:template>

  <xsl:template match="class/method">
    <font color="darkcyan"> <xsl:value-of select="concat(@presc,' ')"/> </font>
 <strong> <font color="red"><xsl:value-of select="@name"/></font> </strong>
(<xsl:apply-templates select="args"/>)
 <em><xsl:value-of select="concat(' ',@desc)"/></em>{<p/>
   <blockquote> <xsl:apply-templates select="exec"/></blockquote>
     <br/> }<p/>
    </xsl:template>

  <xsl:template match="*[not(name()='class')]/method">
    <font color="darkcyan"> <xsl:value-of select="concat(@presc,' ')"/> </font>
 <strong> <i><font color="#ff8888"><xsl:value-of select="@name"/></font></i></strong>
(<xsl:apply-templates select="args"/>)
 <em><xsl:value-of select="concat(' ',@desc)"/></em>{<p/>
   <blockquote> <xsl:apply-templates select="exec"/></blockquote>
     <br/> }<p/>
    </xsl:template>

    <xsl:template match="*[li]">
      <ul><xsl:apply-templates/></ul>
    </xsl:template>

    <xsl:template match="*//li[not(@*)]">
<li style="list-style:none">      
<strong> <tt><xsl:value-of select="translate(name(../..),'_',' ')"/></tt> </strong>
<font color="blue"><xsl:value-of select="concat(' ',translate(name(..),'_','.'))"/></font>
<xsl:apply-templates/>; </li>
    </xsl:template>

    <xsl:template match="li[@mod]">
  <xsl:choose>
    <xsl:when test="@mod=''">
<li style="list-style:none">
<font color="blue"><xsl:value-of select="name(..)"/></font>
<xsl:apply-templates/>; </li>	      
    </xsl:when>
    <xsl:otherwise>
<li style="{@mod}">
<font color="blue"><xsl:value-of select="name(..)"/></font>
<xsl:apply-templates/>; </li>	      
</xsl:otherwise>
</xsl:choose>

    </xsl:template>

    <xsl:template match="FileReader">
      <p> <strong> BufferedReader </strong>  <xsl:value-of select="@name"/> = 
<font color="blue"> new </font> 
<strong>BufferedReader</strong>(<font color="blue"> new </font> 
<strong>FileReader</strong>(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>));
      </p>
    </xsl:template>

    <xsl:template match="FileWriter">
      <p>      <strong> PrintWriter </strong> <xsl:value-of select="@name"/> = <font color="blue"> new </font> <strong>PrintWriter</strong>
      (<font color="blue"> new </font> 
<strong>FileWriter</strong>(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>),true);
    </p>
    </xsl:template>

    <xsl:template match="Reader">
      <p> <strong> BufferedReader </strong>  <xsl:value-of select="@name"/> = 
<font color="blue"> new </font> 
<strong>BufferedReader</strong>(<font color="blue"> new </font> 
<strong><xsl:value-of select="@input"/></strong>
(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>));
      </p>
    </xsl:template>

    <xsl:template match="Writer">
      <p>      <strong> PrintWriter </strong> <xsl:value-of select="@name"/> = <font color="blue"> new </font> <strong>PrintWriter</strong>
      (<font color="blue"> new </font> 
      <strong><xsl:value-of select="@output"/></strong>
(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>),true);
    </p>
    </xsl:template>

    <xsl:template match="DataIn">
      <p> <strong> DataInputStream </strong>  <xsl:value-of select="@name"/> = 
<font color="blue"> new </font> 
<strong>DataInputStream</strong>(<font color="blue"> new </font> 
<strong><xsl:value-of select="@input"/></strong>
(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>));
      </p>
    </xsl:template>

    <xsl:template match="DataOut">
      <p>      <strong> DataOutputStream </strong> 
      <xsl:value-of select="@name"/> = <font color="blue">new</font> <strong> DataOutputStream </strong>
      (<font color="blue"> new </font> 
      <strong><xsl:value-of select="@output"/></strong>
(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>));
    </p>
    </xsl:template>

    <xsl:template match="ReadSource">
      <p/>      <font color="orange"> for</font>(<font color="blue">String</font> v=null; 
	( v=<xsl:value-of select="@in"/>.readLine()) != null;) {<br/>
	<p/>      <xsl:apply-templates/> <br/>}<p/>
    </xsl:template>

    <xsl:template match="DataSourceIO">
<p/><font color="orange">for</font>(<font color="blue">int</font> data=0;(data=<xsl:value-of select="@in"/>.read()) != -1;) {<br/>
	  <xsl:value-of select="@out"/>.write(data); <br/>}<p/>
	<xsl:value-of select="@out"/>.flush();<xsl:value-of select="@out"/>.close();
    </xsl:template>

  <xsl:template match="ff">
    <font color="#0055dd"><xsl:apply-templates/></font>
  </xsl:template>

  <xsl:template match="fg">
    <font color="#5599dd"><tt><xsl:apply-templates/></tt></font>
  </xsl:template>

  <xsl:template match="doccomment">
    /** <br/>
<xsl:for-each select="commentline">
    * <xsl:apply-templates/><br/>
</xsl:for-each>
    */ <p/> 
  </xsl:template>

  <xsl:template match="comment">
    /* <br/>
<xsl:for-each select="commentline">
    * <xsl:apply-templates/><br/>
</xsl:for-each>
    */ <p/> 
  </xsl:template>

    <xsl:template match="gentype">
      <xsl:param name="data"><xsl:apply-templates/></xsl:param>
            <strong>      <xsl:value-of select="@object"/></strong>
      <xsl:value-of select="concat(' ',@name)"/> = 
      <xsl:value-of select="$data"/>;<p/>
    </xsl:template>	

    <xsl:template match="quicktype">
      <xsl:param name="data"><xsl:apply-templates/></xsl:param>
      <strong><xsl:value-of select="@object"/></strong>
      <xsl:value-of select="concat(' ',@name)"/> = <font color="blue"> new </font>
      <strong><xsl:value-of select="@object"/></strong>	
      (<xsl:value-of select="$data"/>);<p/>
    </xsl:template>

    <xsl:template match="shorttype">
      <xsl:param name="data"><xsl:apply-templates/></xsl:param>
  <xsl:value-of select="concat(' ',@name)"/> = <font color="blue"> new </font>
      <strong><xsl:value-of select="@object"/></strong>	
      (<xsl:value-of select="$data"/>);<p/>
    </xsl:template>

    <xsl:template match="new">
      <xsl:param name="data"><xsl:apply-templates/></xsl:param>
      <font color="blue"> new </font>
      <xsl:value-of select="@name"/>
      (<xsl:value-of select="$data"/>)
    </xsl:template>

  <xsl:template match="try|finally">
    <p/>    <font color="magenta"><xsl:value-of select="name()"/></font>{<p/>
    <xsl:apply-templates/>
   <p/>  }   </xsl:template>

  <xsl:template match="switch">
    <p/>    <font color="orange"><b><xsl:value-of select="name()"/></b></font>
(<font color="#707000"><xsl:value-of select="@variable"/></font>) {<p/>
    <xsl:apply-templates/>
   <p/>  }   </xsl:template>

<xsl:template match="catch">
<font color="magenta">catch</font>(<xsl:value-of select="@exc"/>){<br/>
<xsl:apply-templates/>
<br/> } </xsl:template>

<xsl:template match="for">
<p/><font color="orange">for</font> (<font color="#707000"><xsl:value-of select="concat(@initial,'; ',@test,'; ',@increment)"/></font>) {<p/>
  <blockquote><xsl:apply-templates/></blockquote>
<br/>}<p/>
</xsl:template>

<xsl:template match="while|if[not(.//li)]">
<p/><font color="orange"><xsl:value-of select="name()"/></font> (<font color="#707000"><xsl:value-of select="@condition"/></font>) {<p/>
  <blockquote><xsl:apply-templates/></blockquote>
<br/>}<p/>
</xsl:template>

<xsl:template match="else">
<p/><font color="#00aa00"><xsl:value-of select="name()"/></font> {<p/>
  <blockquote><xsl:apply-templates/></blockquote>
<br/>}<p/>
</xsl:template>

  <xsl:template match="b"><b>
<font color="#999999"><xsl:apply-templates/></font></b>
</xsl:template>

<xsl:template match="p|br|tt">
<xsl:copy><xsl:apply-templates/></xsl:copy>
</xsl:template>

<xsl:template match="*[@isadapter='yes']">
<xsl:param name="eventtype" select="concat(substring-before(name(.),'L'),'Event')"/>add<em><strong><xsl:value-of select="name(.)"/></strong></em>(new 
<xsl:value-of select="concat(substring-before(name(.),'L'),'Adapter')"/>(){<br/>
public void 
<font color="red"><xsl:value-of select="@event"/></font>(<xsl:value-of select="$eventtype"/> e)
{<p/>
<xsl:apply-templates/>
<br/>}});<p/>
</xsl:template>

<xsl:template match="*[@isadapter !='yes']">
<xsl:param name="eventtype" select="concat(substring-before(name(.),'L'),'Event')"/>add<em><strong><xsl:value-of select="name(.)"/></strong></em>(new 
<xsl:value-of select="name(.)"/>(){<br/>
public void 
<font color="red"><xsl:value-of select="@event"/></font>(<xsl:value-of select="$eventtype"/> e)
{<p/>
<xsl:apply-templates/>
<br/>}});<p/>
</xsl:template>

<xsl:template match="paint">
<font color="darkcyan">public void </font>
<font color="red">paint</font>(<font color="blue">Graphics</font> g){<p/>
<xsl:apply-templates/>
<br/> }<p/>
</xsl:template>

<xsl:template match="print">
<br/>
<font color="darkred"><strong>System.out.println</strong></font>(<xsl:apply-templates/>);
<br/>
</xsl:template>

<xsl:template match="import[not(.//li)]">
<br/>
<font color="darkgreen">import </font> <xsl:apply-templates/> ;
<br/>
</xsl:template>

<xsl:template match="String">
<font color="blue">String </font> <xsl:apply-templates/> 
</xsl:template>

<xsl:template match="function">
<font color="#555555"><xsl:value-of select="@variable"/></font>.<font color="red"><xsl:value-of select="@name"/></font>(<xsl:apply-templates/>)</xsl:template>

</xsl:stylesheet>
