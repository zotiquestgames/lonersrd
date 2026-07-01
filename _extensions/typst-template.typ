// ============================================
// 0. QUARTO COMPATIBILITY DEFINITIONS
// ============================================
#let horizontalrule = {
  v(1em)
  line(start: (25%, 0%), end: (75%, 0%), stroke: 0.5pt + gray)
  v(1em)
}

// FontAwesome icon stubs (Quarto references these in callout blocks)
#let fa-info() = "ℹ"
#let fa-info-circle() = "ℹ"
#let fa-lightbulb() = "💡"
#let fa-exclamation-triangle() = "⚠"
#let fa-exclamation-circle() = "❗"
#let fa-fire() = "🔥"
#let fa-ban() = "🚫"
#let fa-check-circle() = "✓"
#let fa-times-circle() = "✗"

// Quarto callout block
#let callout(
  body: [],
  title: none,
  background_color: rgb("#dae6fb"),
  icon_color: rgb("#0758E5"),
  icon: none,
  body_background_color: white,
) = block(
  breakable: true,
  width: 100%,
  fill: body_background_color,
  stroke: (left: 3pt + icon_color),
  inset: (left: 12pt, right: 10pt, top: 8pt, bottom: 8pt),
  above: 1em,
  below: 1em,
)[
  #if title != none {
    block(below: 4pt)[
      #text(weight: "bold", fill: icon_color)[
        #if icon != none [#icon #h(3pt)]
        #title
      ]
    ]
  }
  #body
]

// Pandoc syntax-highlighted code block wrapper
#let Skylighting(lines) = block(
  fill: luma(246),
  width: 100%,
  inset: (x: 8pt, y: 6pt),
  radius: 2pt,
  breakable: true,
)[
  #set text(font: ("Courier New", "Courier", "monospace"), size: 0.9em)
  #lines.join(linebreak())
]

// Pandoc syntax highlighting tokens
#let NormalTok(content) = content
#let AlertTok(content) = text(fill: rgb("#cd3c14"))[#content]
#let AnnotationTok(content) = text(fill: rgb("#60a0b0"), style: "italic")[#content]
#let AttributeTok(content) = text(fill: rgb("#7d9029"))[#content]
#let BaseNTok(content) = text(fill: rgb("#40a070"))[#content]
#let BuiltInTok(content) = content
#let CharTok(content) = text(fill: rgb("#4070a0"))[#content]
#let CommentTok(content) = text(fill: rgb("#60a0b0"), style: "italic")[#content]
#let CommentVarTok(content) = text(fill: rgb("#60a0b0"), weight: "bold", style: "italic")[#content]
#let ConstantTok(content) = text(fill: rgb("#880000"))[#content]
#let ControlFlowTok(content) = text(fill: rgb("#007020"), weight: "bold")[#content]
#let DataTypeTok(content) = text(fill: rgb("#902000"))[#content]
#let DecValTok(content) = text(fill: rgb("#40a070"))[#content]
#let DocumentationTok(content) = text(fill: rgb("#ba2121"), style: "italic")[#content]
#let ErrorTok(content) = text(fill: rgb("#ff0000"), weight: "bold")[#content]
#let ExtensionTok(content) = content
#let FloatTok(content) = text(fill: rgb("#40a070"))[#content]
#let FunctionTok(content) = text(fill: rgb("#06287e"))[#content]
#let ImportTok(content) = content
#let InformationTok(content) = text(fill: rgb("#60a0b0"), weight: "bold", style: "italic")[#content]
#let KeywordTok(content) = text(fill: rgb("#007020"), weight: "bold")[#content]
#let OperatorTok(content) = text(fill: rgb("#666666"))[#content]
#let OtherTok(content) = text(fill: rgb("#007020"))[#content]
#let PreprocessorTok(content) = text(fill: rgb("#bc7a00"))[#content]
#let RegionMarkerTok(content) = text(fill: rgb("#4444ff"), weight: "bold")[#content]
#let SpecialCharTok(content) = text(fill: rgb("#4070a0"))[#content]
#let SpecialStringTok(content) = text(fill: rgb("#4070a0"))[#content]
#let StringTok(content) = text(fill: rgb("#4070a0"))[#content]
#let VariableTok(content) = text(fill: rgb("#19177c"))[#content]
#let VerbatimStringTok(content) = text(fill: rgb("#4070a0"))[#content]
#let WarningTok(content) = text(fill: rgb("#60a0b0"), weight: "bold", style: "italic")[#content]

// ============================================
// 1. CONFIGURATION
// ============================================

// Font definitions
#let font-main = "Montserrat"
#let font-title = "Takota"
#let font-subtitle = "Raleway"
#let font-heading = "Raleway"

// Page dimensions
#let page-dims = (
  width: 6in,
  height: 9in,
  margins: (
    left: 0.75in,
    right: 0.625in,
    top: 1.2in,
    bottom: 1in
  )
)

// Set page properties for the entire document
#set page(
  width: page-dims.width,
  height: page-dims.height,
  margin: page-dims.margins
)

// Pagebreaks before H1 are injected by the typst-pagebreak-h1.lua Lua filter
// as top-level raw blocks (show rules cannot contain pagebreaks in Typst).
#show heading.where(level: 1): it => {
  v(5em)
  set text(font: font-heading, size: 16pt, hyphenate: false, weight: "black")
  it
  v(2em)
}


#show heading.where(level: 2): set text(font: font-heading, size: 14pt, hyphenate: false, weight: "extrabold")
#show heading.where(level: 3): set text(font: font-heading, size: 12pt, hyphenate: false, weight: "extrabold")
#show heading.where(level: 4): set text(font: font-heading, size: 11pt, hyphenate: false, weight: "bold")

// Keep list items together with some flexibility
#show list: it => {
  set block(above: 1em, below: 1em)
  it
}

#show list.item: it => {
  block(
    breakable: false,
    above: 0.8em,
    below: 0.8em,
    it
  )
}

// Table styling
#set table(
  stroke: none,
  fill: (col, row) => {
    if row == 0 {
      // Header row: no background
      none
    } else if calc.odd(row) {
      // Odd body rows (1, 3, ...): light grey background
      luma(240)
    }
  }
)
#show table.cell.where(y: 0): set text(weight: "bold")

// Make all tables span the full width of the page
// Note: For Quarto-generated tables, you may also need to set:
// format:
//   typst:
//     tbl-colwidths: auto
// in your _quarto.yml or document front matter
#show figure.where(kind: table): it => {
  block(width: 100%, it)
}
#show table: set align(center)


// Widow and orphan control
#set par(
  first-line-indent: 0pt,
  hanging-indent: 0pt,
  justify: true
)

// Body text
#set text(font: font-main, size: 11pt, weight: "medium")

// ============================================
// 2. TITLE PAGE (no page number)
// ============================================
#set page(numbering: none, footer: none)

#align(right)[
  #set par(justify: false)
  #v(14em)
  #text(font: font-title, size: 22pt, fill: black, hyphenate: false)[
    $title$
  ]
  #v(-0.7em)
  #text(font: font-subtitle, size: 12pt, weight: "black")[
    $subtitle$
  ]
]

#align(center)[
  #v(15em)
  #text(font: font-main, size: 11pt)[
    Version: $version$
  ]
]

// Ensure blank page after cover (title page on right, blank on left, TOC starts on right)
//#pagebreak()

// ============================================
// 3. TABLE OF CONTENTS (lowercase Roman numerals)
// ============================================
#set page(
  numbering: "i",
  footer: context [
    #line(length: 100%, stroke: 0.5pt + gray)
    #v(4pt)
    #set text(font: font-heading, size: 11pt, weight: "bold")
    #align(if calc.odd(here().page()) { right } else { left })[
      #counter(page).display("i")
    ]
  ]
)

#counter(page).update(1)

$if(toc)$
// Use a show rule for the outline title for more flexibility
#show outline: set text(font: font-main, size: 10.5pt)

// Make level 1 entries in the TOC bold
#show outline.entry.where(level: 1): it => strong(it)
#outline(title: [$toc-title$], depth: $toc-depth$)
$endif$

#pagebreak(to: "odd")

// ============================================
// 4. BODY (Arabic numerals, restart at 1)
// ============================================
// Switch to arabic numerals starting from page 1
#set page(
  numbering: "1",
  footer: context [
    #line(length: 100%, stroke: 0.5pt + gray)
    #v(4pt)
    #set text(font: font-heading, size: 11pt, weight: "bold")
    #align(if calc.odd(here().page()) { right } else { left })[
      #counter(page).display()
    ]
  ]
)

#counter(page).update(1)

$body$
