<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <!-- Racine : génère la structure HTML -->
  <xsl:template match="/root">
    <html>
      <head>
        <title>
          <xsl:value-of select="//ms/@name"/>
        </title>
        <link rel="stylesheet" href="styles.css"></link>
        <meta charset="UTF-8"/> 
      </head>
      <body>
        <h1 class="ms"><xsl:value-of select="//ms/@name"/></h1>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <!-- Manuscrit -->
  <xsl:template match="ms">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Chapitre -->
  <xsl:template match="div[@type='chap']">
    <h2 class="chapter">Chapitre <xsl:value-of select="@n"/></h2>
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Verset -->
  <xsl:template match="div[@type='verse']">
    <p class="verse">
      <b><xsl:value-of select="@n"/></b>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <!-- Ligne -->
  <xsl:template match="line">
    <sup class="line">&#x200F;<xsl:value-of select="@n"/></sup>
    <!-- uncomment if you need the folio writen
    <xsl:if test="string(@folio)">
      <span style="color:gray;"> [<xsl:value-of select="@folio"/>]</span>
    </xsl:if> -->
  </xsl:template>

  <!-- w (mot) -->
  <xsl:template match="w">
      <xsl:apply-templates/>
  </xsl:template>

  <!-- g (reconstructed) -->
<xsl:template match="g">
  <span class="reconstructed">
    <xsl:apply-templates/>
  </span>
</xsl:template>

  <!-- stich -->
  <xsl:template match="stich">
    <span class="stich">
    </span>
  </xsl:template>

  <!-- hi (mise en valeur) -->

<xsl:template match="hi">
  <span class="hi">
    <xsl:if test="@rend">
      <xsl:attribute name="id">
        <xsl:value-of select="@rend"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:apply-templates/>
  </span>
</xsl:template>

<!-- margin -->
<xsl:template match="margin">
  <span class="margin">
    <xsl:attribute name="id">
      <xsl:value-of select="@type"/>
    </xsl:attribute>
    <xsl:apply-templates/>
  </span>
</xsl:template>


  <!-- space (génération, des espaces) -->
<xsl:template match="space[@unit='char']">
  <xsl:call-template name="repeat-underscore">
    <xsl:with-param name="n" select="number(@extent)"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="repeat-underscore">
  <xsl:param name="n"/>
  <xsl:if test="$n &gt; 0">
    <xsl:text>_</xsl:text>
    <xsl:call-template name="repeat-underscore">
      <xsl:with-param name="n" select="$n - 1"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>

  <!-- Par défaut, applique les templates aux enfants -->
  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Texte brut -->
  <xsl:template match="text()">
    <xsl:value-of select="."/>
  </xsl:template>



</xsl:stylesheet>