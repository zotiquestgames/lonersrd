# Quarto Website GitHub Template (with Multi-Format Exports)

A clean, modern, and generic GitHub template to kickstart a Quarto website with automatic multi-format compilation (PDF, EPUB, Word, OpenDocument, GFM) and automatic publishing to GitHub Pages.

## Features

- **Multi-Format Exports:** Add any format (e.g., `typst`, `docx`, `odt`, `epub`, `gfm`) to your page's YAML front matter. Quarto will render them, and a custom JavaScript helper will automatically place the download links at the top of the sidebar.
- **Pre-configured Typst PDF Renders:** Includes standard Lua filters and Typst template files (`_extensions/`) for beautiful, professional PDF generation out-of-the-box.
- **GitHub Actions Workflow:** Automatically builds and publishes the website to the `gh-pages` branch on every push to `main` or `master`.
- **Responsive Theme Switching:** Includes Materia (light) and Darkly (dark) themes with custom SCSS adjustments.

---

## Getting Started

### 1. Create a Repository from this Template
1. Click the **Use this template** button at the top of this repository on GitHub.
2. Select **Create a new repository**.
3. Name your repository and click **Create repository**.

### 2. Configure GitHub Pages & Permissions
To allow the GitHub Actions workflow to publish the site, you need to grant write permissions:
1. Go to your new repository's **Settings** tab.
2. Navigate to **Actions** > **General**.
3. Scroll down to **Workflow permissions** and select **Read and write permissions**. Click **Save**.
4. Make a commit or push to `main` (or run the workflow manually under the **Actions** tab) to trigger the initial build.
5. Once the workflow completes, go to **Settings** > **Pages**.
6. Under **Build and deployment**, set the source to **Deploy from a branch**.
7. Under **Branch**, select `gh-pages` and `/ (root)`, then click **Save**.

Your website will be live at `https://<username>.github.io/<repo-name>/`!

---

## How it Works

### Page-Specific Exports

Each file under `docs/` can configure its own output formats using the `format` key in its YAML front matter. For example, `docs/example-document.qmd` compiles to HTML, PDF (via Typst), Word (`.docx`), OpenDocument (`.odt`), EPUB (`.epub`), and GitHub Markdown (`.md`):

```yaml
---
title: "My Document"
format:
  html: {}
  typst:
    toc: true
    template: ../_extensions/typst-template.typ
    template-partials:
      - ../_extensions/typst-show.typ
  odt:
    toc: true
  epub:
    toc: true
  docx:
    toc: true
  gfm:
    toc: false
---
```

When Quarto renders the website, it compiles all these versions and puts them into the output directory (`_site/`).

### Sidebar Layout Helper

By default, Quarto displays format links in a separate area. This template includes a script (`assets/format-links-top.html` which is loaded via `include-after-body` in `_quarto.yml`) that automatically moves these links to the top of the sidebar. It also re-labels "Typst" links to "PDF" for a cleaner, user-friendly look.

To disable format links on a specific page, set `format-links: false` in the page's YAML front matter.

---

## Local Development

To work on your site locally, ensure you have [Quarto](https://quarto.org/docs/get-started/) installed.

### Preview the Website
Run the following command to start a local development server with live reload:
```bash
quarto preview
```

### Render the Website
To render all pages and export formats to the `_site/` directory:
```bash
quarto render
```

---

## Structure

```
├── .github/workflows/
│   └── publish.yml          # GitHub Actions auto-publish workflow
├── _extensions/
│   ├── gfm-callout.lua      # Lua filter for GFM callouts
│   ├── typst-pagebreak-h1.lua # Lua filter for Typst page breaks
│   ├── typst-show.typ       # Typst show partial
│   └── typst-template.typ   # Typst custom template
├── assets/
│   ├── custom.scss          # Custom styling theme overrides
│   ├── fonts.html           # Google Fonts loader
│   └── format-links-top.html # JS script to relocate format links
├── docs/
│   ├── assets/              # Logo and document assets
│   ├── example-document.qmd # Showcase file demonstrating multi-format exports
│   └── about.qmd            # Standalone simple HTML page
├── .gitignore               # Ignored build & IDE files
├── _brand.yml               # Site brand details
├── _quarto.yml               # Main website configuration
├── index.qmd                # Landing page
└── README.md                # This instructions file
```
