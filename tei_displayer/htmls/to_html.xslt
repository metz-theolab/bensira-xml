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
        <!-- <script src="script.js"></script> -->
        <h1 class="ms"><xsl:value-of select="//ms/@name"/></h1>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <!-- Manuscrit -->
  <xsl:template match="ms">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Chapitre : Die Kapitelueberschrift wird nur angezeigt, wenn ein NEUES
       Kapitel beginnt, d.h. wenn das unmittelbar vorhergehende Kapitel eine
       andere Nummer hat (oder es kein vorhergehendes Kapitel gibt). Wichtig
       fuer das Florilegium (Manuskript C), wo aufeinanderfolgende Verse
       desselben Sira-Kapitels jeweils in eigene chap-divs verpackt sind und
       die Ueberschrift sonst mehrfach hintereinander erscheinen wuerde. Fuer
       die uebrigen Handschriften unveraendert, da dort nie zwei gleich
       nummerierte Kapitel aufeinanderfolgen. -->
  <xsl:template match="div[@type='chap']">
    <xsl:if test="not(preceding-sibling::div[@type='chap'][1]/@n = @n)">
      <h2 class="chapter">Chapter <xsl:value-of select="@n"/></h2>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>


  <!-- Verset. Bei Versen mit vielen Randglossen (langen, mehrzeiligen Lesarten)
       wird vertikaler Platz reserviert, damit der lange Randblock nicht in den
       naechsten Vers ueberlaeuft (= "Absatz" nur an diesen Stellen). -->
  <xsl:template match="div[@type='verse']">
    <xsl:variable name="mcount" select="count(following-sibling::margin[
        not(@type='interlinear') and not(@type='infralinear')
        and generate-id(preceding-sibling::div[@type='verse'][1]) = generate-id(current())])"/>
    <p class="verse" id="v{ancestor::div[@type='chap']/@n}_{translate(@n,'/ ','--')}">
      <xsl:if test="$mcount &gt;= 4">
        <xsl:attribute name="style">min-height: <xsl:value-of select="$mcount"/>em;</xsl:attribute>
      </xsl:if>
      <span class="verse_nb"><xsl:value-of select="@n"/></span>
      <xsl:apply-templates/>
    </p>
  </xsl:template>


  <!-- margin -->
  <!-- Interlinear/Infralinear bleiben eigene (inline) Elemente wie bisher. -->
  <xsl:template match="margin[@type='interlinear' or @type='infralinear']">
    <div class="margin" id="{@type}" data-line="{@line}">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <!-- Alle uebrigen Randglossen werden pro Vers UND pro Seite (links/rechts) zu
       EINEM Block zusammengefasst. Gleiche Handschriftenzeile (line+folio) wird
       mit " | " getrennt, verschiedene Zeilen/Typen untereinander (<br/>).
       So koennen sich Glossen desselben Verses auf derselben Seite nicht mehr
       ueberlappen; an allen anderen Stellen bleibt die Ausgabe unveraendert. -->
  <xsl:template match="margin[
      not(@type='interlinear') and not(@type='infralinear')
      and not(preceding-sibling::margin[
          not(@type='interlinear') and not(@type='infralinear')
          and generate-id(preceding-sibling::div[@type='verse'][1]) = generate-id(current()/preceding-sibling::div[@type='verse'][1])
          and ((@type='margin_car_left' or @type='margin_left' or @type='block_margin_left') = (current()/@type='margin_car_left' or current()/@type='margin_left' or current()/@type='block_margin_left'))
      ])
  ]">
    <div class="margin" data-line="{@line}">
      <xsl:attribute name="id">
        <xsl:choose>
          <xsl:when test="@type='margin_car_left' or @type='margin_left' or @type='block_margin_left'">margin_car_left</xsl:when>
          <xsl:otherwise>margin_car</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <!-- Jede einzelne Randlesart (bzw. jede Handschriftenzeile) bekommt ihre
           eigene Verszahl vorangestellt, genau wie in der gedruckten Ausgabe,
           wo jede Anmerkung in der Zeile ihrer Verszahl steht. Die Verszahl wird
           aus dem Attribut @verse der <margin> genommen (aus der PDF eingetragen);
           fehlt es, wird ersatzweise die naechstvorangehende Verseinheit benutzt. -->
      <xsl:for-each select=". | following-sibling::margin[
          not(@type='interlinear') and not(@type='infralinear')
          and generate-id(preceding-sibling::div[@type='verse'][1]) = generate-id(current()/preceding-sibling::div[@type='verse'][1])
          and ((@type='margin_car_left' or @type='margin_left' or @type='block_margin_left') = (current()/@type='margin_car_left' or current()/@type='margin_left' or current()/@type='block_margin_left'))
      ]">
        <xsl:variable name="prev" select="preceding-sibling::margin[
            not(@type='interlinear') and not(@type='infralinear')
            and generate-id(preceding-sibling::div[@type='verse'][1]) = generate-id(current()/preceding-sibling::div[@type='verse'][1])
            and ((@type='margin_car_left' or @type='margin_left' or @type='block_margin_left') = (current()/@type='margin_car_left' or current()/@type='margin_left' or current()/@type='block_margin_left'))
        ][1]"/>
        <xsl:variable name="sameline" select="position() &gt; 1 and @line = $prev/@line and normalize-space(@folio) = normalize-space($prev/@folio)"/>
        <xsl:if test="position() &gt; 1 and not($sameline)"><br/></xsl:if>
        <xsl:if test="$sameline"><xsl:text> | </xsl:text></xsl:if>
        <xsl:if test="not($sameline)">
          <span class="margin_vn">
            <xsl:choose>
              <xsl:when test="string(@verse)"><xsl:value-of select="@verse"/></xsl:when>
              <xsl:otherwise><xsl:value-of select="preceding-sibling::div[@type='verse'][1]/@n"/></xsl:otherwise>
            </xsl:choose>
          </span>
        </xsl:if>
        <xsl:apply-templates/>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!-- Nicht-erste Glossen einer (Vers, Seite)-Gruppe werden im Block mitgerendert. -->
  <xsl:template match="margin[
      not(@type='interlinear') and not(@type='infralinear')
      and preceding-sibling::margin[
          not(@type='interlinear') and not(@type='infralinear')
          and generate-id(preceding-sibling::div[@type='verse'][1]) = generate-id(current()/preceding-sibling::div[@type='verse'][1])
          and ((@type='margin_car_left' or @type='margin_left' or @type='block_margin_left') = (current()/@type='margin_car_left' or current()/@type='margin_left' or current()/@type='block_margin_left'))
      ]
  ]"/>


  <!-- Ligne -->
  <xsl:template match="line">
    <sup class="line">&#x200F;<xsl:value-of select="@n"/></sup>
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

  <!-- line break -->
  <xsl:template match="lb">
    <br/>
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

  <xsl:template match="del">
      <span class="del">
      <xsl:if test="@rend">
        <xsl:attribute name="id">
          <xsl:value-of select="@rend"/>
        </xsl:attribute>
      </xsl:if>
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
