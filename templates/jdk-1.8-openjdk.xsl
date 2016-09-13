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
      <homePath value="{$jdk_home}" />
      <roots>
        <annotationsPath>
          <root type="composite">
            <root type="simple" url="jar://$APPLICATION_HOME_DIR$/lib/jdkAnnotations.jar!/" />
          </root>
        </annotationsPath>
        <classPath>
          <root type="composite">
            <root type="simple" url="jar://{$jdk_home}/jre/lib/charsets.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/cldrdata.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/dnsns.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/icedtea-sound.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/jaccess.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/java-atk-wrapper.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/localedata.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/nashorn.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/sunec.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/sunjce_provider.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/sunpkcs11.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/ext/zipfs.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/jce.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/jsse.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/management-agent.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/resources.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/jre/lib/rt.jar!/" />
          </root>
        </classPath>
        <javadocPath>
          <root type="composite" />
        </javadocPath>
        <sourcePath>
          <root type="composite">
            <root type="simple" url="jar://{$jdk_home}/src.zip!/" />
          </root>
        </sourcePath>
      </roots>
      <additional />
    </jdk>
  </xsl:template>
</xsl:stylesheet>
