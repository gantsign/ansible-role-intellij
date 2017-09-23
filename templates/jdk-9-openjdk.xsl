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
      <version value="java version &quot;9&quot;" />
      <homePath value="{$jdk_home}" />
      <roots>
        <annotationsPath>
          <root type="composite">
            <root type="simple" url="jar://$APPLICATION_HOME_DIR$/lib/jdkAnnotations.jar!/" />
          </root>
        </annotationsPath>
        <classPath>
          <root type="composite">
            <root type="simple" url="jrt://{$jdk_home}!/java.activation" />
            <root type="simple" url="jrt://{$jdk_home}!/java.base" />
            <root type="simple" url="jrt://{$jdk_home}!/java.compiler" />
            <root type="simple" url="jrt://{$jdk_home}!/java.corba" />
            <root type="simple" url="jrt://{$jdk_home}!/java.datatransfer" />
            <root type="simple" url="jrt://{$jdk_home}!/java.desktop" />
            <root type="simple" url="jrt://{$jdk_home}!/java.instrument" />
            <root type="simple" url="jrt://{$jdk_home}!/java.logging" />
            <root type="simple" url="jrt://{$jdk_home}!/java.management" />
            <root type="simple" url="jrt://{$jdk_home}!/java.management.rmi" />
            <root type="simple" url="jrt://{$jdk_home}!/java.naming" />
            <root type="simple" url="jrt://{$jdk_home}!/java.prefs" />
            <root type="simple" url="jrt://{$jdk_home}!/java.rmi" />
            <root type="simple" url="jrt://{$jdk_home}!/java.scripting" />
            <root type="simple" url="jrt://{$jdk_home}!/java.se" />
            <root type="simple" url="jrt://{$jdk_home}!/java.se.ee" />
            <root type="simple" url="jrt://{$jdk_home}!/java.security.jgss" />
            <root type="simple" url="jrt://{$jdk_home}!/java.security.sasl" />
            <root type="simple" url="jrt://{$jdk_home}!/java.smartcardio" />
            <root type="simple" url="jrt://{$jdk_home}!/java.sql" />
            <root type="simple" url="jrt://{$jdk_home}!/java.sql.rowset" />
            <root type="simple" url="jrt://{$jdk_home}!/java.transaction" />
            <root type="simple" url="jrt://{$jdk_home}!/java.xml" />
            <root type="simple" url="jrt://{$jdk_home}!/java.xml.bind" />
            <root type="simple" url="jrt://{$jdk_home}!/java.xml.crypto" />
            <root type="simple" url="jrt://{$jdk_home}!/java.xml.ws" />
            <root type="simple" url="jrt://{$jdk_home}!/java.xml.ws.annotation" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.accessibility" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.attach" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.charsets" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.compiler" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.crypto.cryptoki" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.crypto.ec" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.dynalink" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.editpad" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.hotspot.agent" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.httpserver" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.incubator.httpclient" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.internal.ed" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.internal.jvmstat" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.internal.le" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.internal.opt" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.internal.vm.ci" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jartool" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.javadoc" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jcmd" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jconsole" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jdeps" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jdi" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jdwp.agent" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jlink" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jshell" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jsobject" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.jstatd" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.localedata" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.management" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.management.agent" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.naming.dns" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.naming.rmi" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.net" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.pack" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.policytool" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.rmic" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.scripting.nashorn" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.scripting.nashorn.shell" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.sctp" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.security.auth" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.security.jgss" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.unsupported" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.xml.bind" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.xml.dom" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.xml.ws" />
            <root type="simple" url="jrt://{$jdk_home}!/jdk.zipfs" />
          </root>
        </classPath>
        <javadocPath>
          <root type="composite" />
        </javadocPath>
        <sourcePath>
          <root type="composite">
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.se" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jdi" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.net" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.rmi" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.sql" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.xml" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jcmd" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.pack" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.rmic" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.sctp" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.base" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jdeps" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jlink" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.zipfs" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.corba" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.prefs" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.se.ee" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.attach" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jshell" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jstatd" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.ws" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.naming" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.xml.ws" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.editpad" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jartool" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.javadoc" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.dom" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.desktop" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.logging" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.charsets" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.compiler" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.dynalink" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jconsole" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jsobject" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.xml.bind" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.compiler" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.xml.bind" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.crypto.ec" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.scripting" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.httpserver" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.jdwp.agent" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.localedata" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.management" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.naming.dns" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.naming.rmi" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.policytool" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.activation" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.instrument" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.management" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.sql.rowset" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.xml.crypto" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.ed" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.le" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.unsupported" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.smartcardio" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.transaction" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.opt" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.datatransfer" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.accessibility" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.hotspot.agent" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.security.auth" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.security.jgss" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.security.jgss" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.security.sasl" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.vm.ci" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.management.rmi" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.crypto.cryptoki" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.internal.jvmstat" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.management.agent" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.scripting.nashorn" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/java.xml.ws.annotation" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.incubator.httpclient" />
            <root type="simple" url="jar://{$jdk_home}/lib/src.zip!/jdk.scripting.nashorn.shell" />
          </root>
        </sourcePath>
      </roots>
      <additional />
    </jdk>
  </xsl:template>
</xsl:stylesheet>
