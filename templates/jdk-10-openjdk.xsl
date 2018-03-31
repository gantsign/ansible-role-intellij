<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="@*|node()">
    <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
  </xsl:template>

  <xsl:template match="component[@name='ProjectJdkTable' and jdk[name/@value='JDK_NAME']]" priority="1">
    <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
  </xsl:template>

  <xsl:template match="component[@name='ProjectJdkTable']">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
        <xsl:call-template name="jdk"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="jdk[name/@value='JDK_NAME']">
    <xsl:call-template name="jdk"/>
  </xsl:template>

  <xsl:template name="jdk">
    <jdk version="2">
      <name value="JDK_NAME" />
      <type value="JavaSDK" />
      <version value="java version &quot;10&quot;" />
      <homePath value="{$jdk_home}" />
      <roots>
        <annotationsPath>
          <root type="composite">
            <root url="jar://$APPLICATION_HOME_DIR$/lib/jdkAnnotations.jar!/" type="simple" />
          </root>
        </annotationsPath>
        <classPath>
          <root type="composite">
            <root url="jrt://{$jdk_home}!/java.activation" type="simple" />
            <root url="jrt://{$jdk_home}!/java.base" type="simple" />
            <root url="jrt://{$jdk_home}!/java.compiler" type="simple" />
            <root url="jrt://{$jdk_home}!/java.corba" type="simple" />
            <root url="jrt://{$jdk_home}!/java.datatransfer" type="simple" />
            <root url="jrt://{$jdk_home}!/java.desktop" type="simple" />
            <root url="jrt://{$jdk_home}!/java.instrument" type="simple" />
            <root url="jrt://{$jdk_home}!/java.logging" type="simple" />
            <root url="jrt://{$jdk_home}!/java.management" type="simple" />
            <root url="jrt://{$jdk_home}!/java.management.rmi" type="simple" />
            <root url="jrt://{$jdk_home}!/java.naming" type="simple" />
            <root url="jrt://{$jdk_home}!/java.prefs" type="simple" />
            <root url="jrt://{$jdk_home}!/java.rmi" type="simple" />
            <root url="jrt://{$jdk_home}!/java.scripting" type="simple" />
            <root url="jrt://{$jdk_home}!/java.se" type="simple" />
            <root url="jrt://{$jdk_home}!/java.se.ee" type="simple" />
            <root url="jrt://{$jdk_home}!/java.security.jgss" type="simple" />
            <root url="jrt://{$jdk_home}!/java.security.sasl" type="simple" />
            <root url="jrt://{$jdk_home}!/java.smartcardio" type="simple" />
            <root url="jrt://{$jdk_home}!/java.sql" type="simple" />
            <root url="jrt://{$jdk_home}!/java.sql.rowset" type="simple" />
            <root url="jrt://{$jdk_home}!/java.transaction" type="simple" />
            <root url="jrt://{$jdk_home}!/java.xml" type="simple" />
            <root url="jrt://{$jdk_home}!/java.xml.bind" type="simple" />
            <root url="jrt://{$jdk_home}!/java.xml.crypto" type="simple" />
            <root url="jrt://{$jdk_home}!/java.xml.ws" type="simple" />
            <root url="jrt://{$jdk_home}!/java.xml.ws.annotation" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.accessibility" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.aot" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.attach" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.charsets" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.compiler" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.crypto.cryptoki" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.crypto.ec" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.dynalink" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.editpad" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.hotspot.agent" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.httpserver" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.incubator.httpclient" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.ed" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.jvmstat" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.le" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.opt" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.vm.ci" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.vm.compiler" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.internal.vm.compiler.management" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jartool" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.javadoc" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jcmd" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jconsole" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jdeps" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jdi" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jdwp.agent" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jlink" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jshell" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jsobject" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.jstatd" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.localedata" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.management" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.management.agent" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.naming.dns" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.naming.rmi" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.net" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.pack" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.rmic" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.scripting.nashorn" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.scripting.nashorn.shell" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.sctp" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.security.auth" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.security.jgss" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.unsupported" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.xml.bind" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.xml.dom" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.xml.ws" type="simple" />
            <root url="jrt://{$jdk_home}!/jdk.zipfs" type="simple" />
          </root>
        </classPath>
        <javadocPath>
          <root type="composite" />
        </javadocPath>
        <sourcePath>
          <root type="composite">
            <root url="jar://{$jdk_home}/lib/src.zip!/java.se" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.aot" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jdi" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.net" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.rmi" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.sql" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.xml" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jcmd" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.pack" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.rmic" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.sctp" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.base" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jdeps" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jlink" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.zipfs" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.corba" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.prefs" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.se.ee" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.attach" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jshell" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jstatd" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.ws" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.naming" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.xml.ws" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.editpad" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jartool" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.javadoc" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.dom" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.desktop" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.logging" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.charsets" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.compiler" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.dynalink" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jconsole" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jsobject" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.bind" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.compiler" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.xml.bind" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.crypto.ec" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.scripting" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.httpserver" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.jdwp.agent" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.localedata" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.management" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.naming.dns" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.naming.rmi" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.activation" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.instrument" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.management" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.sql.rowset" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.xml.crypto" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.ed" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.le" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.unsupported" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.smartcardio" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.transaction" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.opt" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.datatransfer" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.accessibility" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.hotspot.agent" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.security.auth" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.security.jgss" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.security.jgss" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.security.sasl" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.vm.ci" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.management.rmi" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.crypto.cryptoki" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.jvmstat" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.management.agent" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.scripting.nashorn" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/java.xml.ws.annotation" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.incubator.httpclient" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.vm.compiler" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.scripting.nashorn.shell" type="simple" />
            <root url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.vm.compiler.management" type="simple" />
          </root>
        </sourcePath>
      </roots>
      <additional />
    </jdk>
  </xsl:template>
</xsl:stylesheet>
