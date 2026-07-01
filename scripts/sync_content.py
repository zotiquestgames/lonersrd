"""
Regenerates, from the raw source-of-truth files under content/:
  1. the front-mattered, render-ready .md files at the repo root
  2. _sidebar-auto.yml, the website.sidebar nav (merged into _quarto.yml via
     metadata-files)

Why this exists: content/ is the target of an external sync (a GitHub Action
in the private zotiquestgames/loner repo copies its docs/ folder here). That
sync only ever touches content/**, so it can never destroy the Quarto front
matter, font-paths, typst template wiring, or navigation below -- those are
re-derived every time this script runs. In particular, a new file dropped
into a known collection folder (see COLLECTIONS below) automatically gets a
sidebar entry (appended after the curated, hand-ordered items) instead of
being an orphan page.

Runs automatically as a Quarto project pre-render step (see _quarto.yml),
so everything is fresh before `quarto render` / `preview` / `publish`.

Adding a brand-new top-level section (e.g. a future "Monster Manual"):
  1. Add one entry to COLLECTIONS below (folder, section title, optional
     curated order/legacy subsection). Sections are pure expand/collapse
     togglers in the sidebar -- no hub/landing page needed.
  2. Add one glob line to `project.render` in _quarto.yml, e.g.
     "monster_manual/*.md" (Quarto reads that list before pre-render runs,
     so a brand-new folder can't be discovered automatically there).
That's it -- frontmatter and the sidebar section are then fully derived.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

AUTHOR = "Roberto Bisceglie"
VERSION = "3.0"

# Fixed, hand-authored SRD documents -- not folder-driven collections, just
# individually named books. (title, subtitle) per rel path; title=None means
# derive from the file's first H1.
SRD_DOCS = {
    "loner-3e.md": (None, None),
    "loner-2e.md": ("Loner - Core Rules 2nd Edition (Legacy)", None),
    "loner-1e.md": ("Loner - Core Rules 1st Edition (Legacy)", None),
    "companion.md": (None, None),
    "character_builders_guide.md": (None, None),
    "world_builders_guide.md": (None, None),
    "the_path_not_taken.md": (
        None,
        "Two modes of temporal play for solo storytelling: looping fates and irrevocable leaps.",
    ),
    "cinematic_action.md": (None, None),
    "urban_fantasy.md": (None, None),
}

# One entry per top-level, folder-driven sidebar section. Files present in
# content/<folder>/ but not listed in "curated" are auto-appended (sorted by
# filename, title derived from H1) -- this is what makes newly-synced files
# show up in nav without editing this file.
COLLECTIONS = [
    {
        "folder": "adventure_packs",
        "section": "Adventure Packs",
        "curated": [
            ("AP01_fantasy.md", "Fantasy Adventure Pack"),
            ("AP02_space.md", "Space Sci-Fi Adventure Pack"),
            ("AP03_superheroes.md", "Superheroes Adventure Pack"),
            ("AP04_crime.md", "Crime Adventure Pack"),
            ("AP05_mystery.md", "Mystery Adventure Pack"),
            ("AP06_horror.md", "Horror Adventure Pack"),
            ("AP07_action_adventure.md", "Action Adventure Pack"),
            ("AP08_spy.md", "Spy Adventure Pack"),
            ("AP09_postapoc.md", "Post-Apocalyptic Adventure Pack"),
            ("AP10_pirates.md", "Pirates Adventure Pack"),
            ("AP11_western.md", "Western Adventure Pack"),
            ("AP12_cyberpunk.md", "Cyberpunk Adventure Pack"),
        ],
        "legacy": {
            "folder": "adventure_packs_2e",
            "section": "Adventure Packs (Legacy 2e)",
            "curated": [
                ("AP01_fantasy.md", "Fantasy Adventure Pack"),
                ("AP02_space.md", "Space Sci-Fi Adventure Pack"),
                ("AP03_superheroes.md", "Superheroes Adventure Pack"),
                ("AP04_crime.md", "Crime Adventure Pack"),
                ("AP05_mystery.md", "Mystery Adventure Pack"),
                ("AP06_horror.md", "Horror Adventure Pack"),
                ("AP07_action_adventure.md", "Action Adventure Pack"),
                ("AP08_spy.md", "Spy Adventure Pack"),
                ("AP09_postapoc.md", "Post-Apocalyptic Adventure Pack"),
                ("AP10_pirates.md", "Pirates Adventure Pack"),
                ("AP11_western.md", "Western Adventure Pack"),
                ("AP12_cyberpunk.md", "Cyberpunk Adventure Pack"),
            ],
            "extra_entries": [("geared_towards_loner/kwaidan.md", "Kwaidan!")],
        },
    },
    {
        "folder": "geared_towards_loner",
        "section": "Geared Towards Loner games",
        # tales_and_tumbles.md is placed under SRD ("For Kids") and
        # kwaidan.md under the legacy subsection -- skip them here so
        # they aren't duplicated as "newcomers".
        "skip": {"tales_and_tumbles.md", "kwaidan.md"},
        "curated": [
            ("kwaidan_revised.md", "Kwaidan! (Revised)"),
            ("cog_compass.md", "Cog & Compass"),
            ("mech_requiem.md", "Mech: Requiem"),
            ("legends_of_camelot.md", "Legends of Camelot"),
            ("pulp_adventures.md", "Pulp Adventures!"),
            ("steel_and_sorcery.md", "Steel & Sorcery"),
            ("dungeoneer.md", "Dungeoneer"),
            ("spacer.md", "Spacer"),
            ("arabian_nights_adventures.md", "Arabian Nights Adventures"),
            ("cozy_fantasy.md", "Cozy Fantasy"),
            ("savage_blades_of_xylandra.md", "Savage Blades of Xylandra"),
            ("pulp_heroes.md", "Pulp Heroes!"),
            ("the_shattered_reach.md", "The Shattered Reach"),
            ("galaxy_drifter.md", "Galaxy Drifter"),
            ("norse_saga.md", "Norse Saga"),
            ("cthulhu.md", "Cthulhu"),
            ("paranormal_files.md", "Paranormal Files"),
        ],
        # urban_fantasy.md lives at the repo root (synced separately, see
        # SRD_DOCS), not inside content/geared_towards_loner/, but belongs
        # in this section's nav.
        "extra_entries": [("urban_fantasy.md", "Urban Fantasy")],
        "legacy": {
            "section": "Geared Towards Loner games (Legacy)",
            "extra_entries": [("geared_towards_loner/kwaidan.md", "Kwaidan!")],
        },
    },
]

# Document title overrides, independent of sidebar labels (most pages derive
# their title from their own H1, which is usually what you want -- this is
# only for the rare page whose H1 doesn't match its real title, e.g. an
# "Introduction" H1 on the first page of a book).
TITLE_OVERRIDES = {
    "geared_towards_loner/mech_requiem.md": "Loner: Mech Requiem",
}

FRONTMATTER_TMPL = """---
title: "{title}"{subtitle_line}
author: "{author}"
date: last-modified
version: {version}
lang: en
format:
  html: {{}}
  typst:
    toc: true
    toc-depth: 2
    number-sections: true
    fontsize: 11pt
    tbl-colwidths: auto
    template: {prefix}_extensions/typst-template.typ
    font-paths: {prefix}_extensions/fonts
    template-partials:
      - {prefix}_extensions/typst-show.typ
  odt:
    toc: true
  epub:
    toc: true
  docx:
    toc: true
  gfm:
    toc: false
---

"""

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER_BLOCK_RE = re.compile(r"^---\n.*?\n---\n+", re.DOTALL)


def strip_frontmatter(text):
    return FRONTMATTER_BLOCK_RE.sub("", text, count=1)


def clean_title(raw):
    return raw.strip().replace("\\!", "!").replace("**", "").rstrip("\\").strip().replace('"', "'")


def frontmatter_for(rel):
    """(title, subtitle) for a document's own front matter -- independent of
    its sidebar label. title=None means derive from the file's H1."""
    if rel in SRD_DOCS:
        return SRD_DOCS[rel]
    return (TITLE_OVERRIDES.get(rel), None)


def title_for(rel):
    title_override, _ = frontmatter_for(rel)
    if title_override:
        return title_override
    src = CONTENT / rel
    if not src.exists():
        return Path(rel).stem
    body = strip_frontmatter(src.read_text(encoding="utf-8"))
    m = H1_RE.search(body)
    return clean_title(m.group(1)) if m else Path(rel).stem


def all_synced_files():
    """rel paths (under content/, mirrored at repo root) for every file this
    script manages: SRD docs plus everything in each COLLECTIONS folder."""
    rels = list(SRD_DOCS)
    for coll in COLLECTIONS:
        for section in (coll, coll.get("legacy") or {}):
            folder = section.get("folder")
            if folder:
                rels += [f"{folder}/{p.name}" for p in sorted((CONTENT / folder).glob("*.md"))]
    return rels


def collection_entries(folder, curated, skip=frozenset()):
    """(href, text) pairs for content/<folder>/*.md: curated items first in
    their curated order, then any newly-synced files not yet curated."""
    curated_names = {name for name, _ in curated}
    present = {p.name for p in (CONTENT / folder).glob("*.md")}

    entries = [(f"{folder}/{name}", text) for name, text in curated if name in present]
    newcomers = sorted(present - curated_names - set(skip))
    entries += [(f"{folder}/{name}", title_for(f"{folder}/{name}")) for name in newcomers]
    return entries


def yaml_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def dump_contents(items, indent):
    pad = "  " * indent
    lines = []
    for item in items:
        if "contents" in item:
            lines.append(f'{pad}- section: "{yaml_escape(item["section"])}"')
            if item.get("href"):
                lines.append(f'{pad}  href: {item["href"]}')
            lines.append(f"{pad}  contents:")
            lines.extend(dump_contents(item["contents"], indent + 2))
        else:
            lines.append(f'{pad}- href: {item["href"]}')
            lines.append(f'{pad}  text: "{yaml_escape(item["text"])}"')
    return lines


def collection_tree_node(coll):
    contents = [
        {"href": rel, "text": text}
        for rel, text in collection_entries(coll["folder"], coll["curated"], coll.get("skip", set()))
    ]
    contents += [{"href": rel, "text": text} for rel, text in coll.get("extra_entries", [])]

    legacy = coll.get("legacy")
    if legacy:
        legacy_contents = []
        if legacy.get("folder"):
            legacy_contents += [
                {"href": rel, "text": text}
                for rel, text in collection_entries(
                    legacy["folder"], legacy.get("curated", []), legacy.get("skip", set())
                )
            ]
        legacy_contents += [{"href": rel, "text": text} for rel, text in legacy.get("extra_entries", [])]
        contents.append({"section": legacy["section"], "contents": legacy_contents})

    return {"section": coll["section"], "contents": contents}


def generate_sidebar():
    tree = [
        {
            "section": "SRD",
            "contents": [
                {"href": "loner-3e.md", "text": "Core Rules 3e"},
                {"href": "companion.md", "text": "Companion"},
                {"href": "character_builders_guide.md", "text": "Character Builder's Guide"},
                {"href": "world_builders_guide.md", "text": "World Builder's Guide"},
                {"href": "the_path_not_taken.md", "text": "The Path Not Taken"},
                {"href": "cinematic_action.md", "text": "Cinematic Action"},
                {"href": "geared_towards_loner/tales_and_tumbles.md", "text": "For Kids"},
                {
                    "section": "Legacy Core Rules",
                    "contents": [
                        {"href": "loner-1e.md", "text": "Core Rules 1e (legacy)"},
                        {"href": "loner-2e.md", "text": "Core Rules 2e (legacy)"},
                    ],
                },
            ],
        },
    ]
    tree += [collection_tree_node(coll) for coll in COLLECTIONS]

    lines = ["website:", "  sidebar:", "    style: docked", "    collapse-level: 1", "    contents:"]
    lines += dump_contents(tree, 3)
    (ROOT / "_sidebar-auto.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("OK  _sidebar-auto.yml")


def main():
    for rel in all_synced_files():
        src = CONTENT / rel
        if not src.exists():
            print(f"WARN missing content/{rel}, skipping")
            continue
        body = strip_frontmatter(src.read_text(encoding="utf-8"))
        title = title_for(rel)
        _, subtitle = frontmatter_for(rel)
        subtitle_line = f'\nsubtitle: "{subtitle}"' if subtitle else ""
        depth = len(Path(rel).parts) - 1
        prefix = "../" * depth

        fm = FRONTMATTER_TMPL.format(
            title=title, subtitle_line=subtitle_line, author=AUTHOR, version=VERSION, prefix=prefix
        )
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(fm + body, encoding="utf-8")
        print(f"OK  {rel}")

    generate_sidebar()


if __name__ == "__main__":
    main()
