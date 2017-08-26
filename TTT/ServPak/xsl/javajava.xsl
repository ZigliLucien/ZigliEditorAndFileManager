<?xml version="1.0"?>
<xsl:stylesheet 
xmlns:date="file:/usr/local/java/bin/java.util.Date"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="text"/>

  <xsl:template match="java"><xsl:apply-templates/></xsl:template>

  <xsl:template match="class">
<xsl:value-of select="concat(@presc,' ')"/> class <xsl:value-of select="concat(' ',@name,' ',@desc)"/> {<xsl:apply-templates/>}</xsl:template>


<xsl:template match="doccomment[@auth]">
/** <xsl:for-each select="commentline">
    * <xsl:apply-templates/></xsl:for-each>
*
* @author <xsl:value-of select="@auth"/>
* @version <xsl:value-of select="date:to-string(date:new())"/>
*
*/
</xsl:template>

<xsl:template match="doccomment[not(@*)]">
/** <xsl:for-each select="commentline">
    * <xsl:apply-templates/></xsl:for-each>
*/
</xsl:template>

  <xsl:template match="constructor">
   <xsl:value-of select="concat(@presc,' ',../@name)"/>(<xsl:apply-templates select="args"/>)<xsl:value-of select="@desc"/>{<xsl:apply-templates select="exec"/>} </xsl:template>

  <xsl:template match="package">
 package <xsl:value-of select="(.)"/>; </xsl:template>

  <xsl:template match="method">
<xsl:value-of select="concat(@presc,' ',@name)"/>(<xsl:apply-templates select="args"/>)<xsl:value-of select="@desc"/>{<xsl:apply-templates select="exec"/>}</xsl:template>

<xsl:template match="li[@mod]"><xsl:value-of select="name(..)"/><xsl:apply-templates/>;</xsl:template>

<xsl:template match="*//li[not(@*)]"><xsl:value-of select="translate(name(../..),'_',' ')"/><xsl:value-of select="concat(' ',translate(name(..),'_','.'))"/><xsl:apply-templates/>;</xsl:template>

    <xsl:template match="FileReader">
BufferedReader <xsl:value-of select="@name"/> = new BufferedReader(new FileReader(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>));
    </xsl:template>

    <xsl:template match="FileWriter">
PrintWriter <xsl:value-of select="@name"/> = new PrintWriter(new FileWriter(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>),true);
    </xsl:template>

    <xsl:template match="Reader">
BufferedReader <xsl:value-of select="@name"/> = new BufferedReader(new <xsl:value-of select="@input"/>(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>));    </xsl:template>

    <xsl:template match="Writer">
PrintWriter <xsl:value-of select="@name"/> = new PrintWriter(new <xsl:value-of select="@output"/>(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>),true); </xsl:template>

    <xsl:template match="DataIn">
 DataInputStream <xsl:value-of select="@name"/> = new DataInputStream(new <xsl:value-of select="@input"/>(<xsl:value-of select="concat('&quot;',@filein,'&quot;')"/>)); </xsl:template>

    <xsl:template match="DataOut">
DataOutputStream <xsl:value-of select="@name"/> = new DataOutputStream(new <xsl:value-of select="@output"/>(<xsl:value-of select="concat('&quot;',@fileout,'&quot;')"/>)); </xsl:template>

    <xsl:template match="ReadSource">
      for( String v=null; (v=<xsl:value-of select="@in"/>.readLine()) != null;) {
      <xsl:apply-templates/> } </xsl:template>

    <xsl:template match="DataSourceIO">
      for(int data=0;(data =<xsl:value-of select="@in"/>.read()) != -1;) {
      <xsl:value-of select="@out"/>.write(data); }
	<xsl:value-of select="@out"/>.flush();<xsl:value-of select="@out"/>.close(); </xsl:template>

    <xsl:template match="gentype"> 
<xsl:param name="data"><xsl:apply-templates/></xsl:param> <xsl:value-of select="concat(@object,' ',@name,' = ',$data,';')"/> </xsl:template>

    <xsl:template match="quicktype">
<xsl:param name="data"><xsl:apply-templates/></xsl:param> <xsl:value-of select="concat(@object,' ',@name,' = new ',@object,'(',$data,');')"/> </xsl:template> 

    <xsl:template match="shorttype">
 <xsl:param name="data"><xsl:apply-templates/></xsl:param> <xsl:value-of select="concat(@name,' = new ',@object,'(',$data,');')"/> </xsl:template>


    <xsl:template match="new">
      <xsl:param name="data"><xsl:apply-templates/></xsl:param>
<xsl:value-of select="concat('new ',@name,'(',$data,')')"/> </xsl:template>

  <xsl:template match="comment">
/* <xsl:for-each select="commentline">
    * <xsl:apply-templates/> </xsl:for-each>
*/ 
</xsl:template>

 <xsl:template match="try|finally|switch">
<xsl:value-of select="name()"/>{<xsl:apply-templates/> 
}  
</xsl:template>

<xsl:template match="catch">
catch(<xsl:value-of select="@exc"/>) {<xsl:apply-templates/>} 
</xsl:template>

<xsl:template match="for">
for (<xsl:value-of select="concat(@initial,'; ',@test,'; ',@increment)"/>) {
<xsl:apply-templates/>
}
</xsl:template>

<xsl:template match="while|if[not(.//li)]">
<xsl:value-of select="name()"/> (<xsl:value-of select="@condition"/>) {
<xsl:apply-templates/>
}
</xsl:template>

<xsl:template match="else">
<xsl:value-of select="name()"/> {
  <xsl:apply-templates/> }
</xsl:template>


  <xsl:template match="ff|fg|exec"><xsl:apply-templates/></xsl:template>

<xsl:template match="*[@isadapter='yes']">
<xsl:param name="eventtype" select="concat(substring-before(name(.),'L'),'Event')"/><xsl:value-of select="concat('add',name(.))"/>(new <xsl:value-of select="concat(substring-before(name(.),'L'),'Adapter')"/>(){
public void <xsl:value-of select="@event"/>(<xsl:value-of select="$eventtype"/> e){<xsl:apply-templates/>}});
</xsl:template>

<xsl:template match="*[@isadapter !='yes']">
<xsl:param name="eventtype" select="concat(substring-before(name(.),'L'),'Event')"/><xsl:value-of select="concat('add',name(.))"/>(new <xsl:value-of select="name(.)"/>(){
public void <xsl:value-of select="@event"/>(<xsl:value-of select="$eventtype"/> e){<xsl:apply-templates/>}});
</xsl:template>

<xsl:template match="paint">
public void paint(Graphics g){<xsl:apply-templates/>}
</xsl:template>

<xsl:template match="print">
System.out.println(<xsl:apply-templates/>);
</xsl:template>

<xsl:template match="import[not(.//li)]">
import <xsl:apply-templates/> ;
</xsl:template>

<xsl:template match="String[not(.//li)]"> String <xsl:apply-templates/> </xsl:template>

<xsl:template match="function"> <xsl:value-of select="@variable"/>.<xsl:value-of select="@name"/>(<xsl:apply-templates/>) </xsl:template>

</xsl:stylesheet>
