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
            <root type="simple" url="jrt://{$jdk_home}!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/ant-javafx.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/deploy.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/java.jnlp.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/javafx-swt.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/javaws.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/jdk.deploy.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/jdk.javaws.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/jdk.plugin.dom.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/jdk.plugin.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/plugin-legacy.jar!/" />
            <root type="simple" url="jar://{$jdk_home}/lib/plugin.jar!/" />
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
