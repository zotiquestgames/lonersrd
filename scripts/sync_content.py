"""
Regenerates, from the raw source-of-truth files under content/:
  1. the front-mattered, render-ready .md files at the repo root (mirroring
     content/'s folder structure exactly)
  2. _sidebar-auto.yml, the website.sidebar nav (merged into _quarto.yml via
     metadata-files)
  3. diagrams/ at the repo root, copied straight from content/diagrams/

Why this exists: content/ is the target of an external sync (a GitHub Action
in the private zotiquestgames/loner repo copies its docs/ folder here, one
folder per section: core/, adventure_packs/, geared_towards_loner/, each
with its own legacy/ subfolder where applicable, plus diagrams/). That sync
only ever touches content/**, so it can never destroy the Quarto front
matter, font-paths, typst template wiring, or navigation below -- those are
re-derived every time this script runs. In particular, a new file dropped
into a known collection folder (see COLLECTIONS below) automatically gets a
sidebar entry (appended after the curated, hand-ordered items) instead of
being an orphan page. Relative diagrams/ image paths are also normalized
per-file depth (see normalize_diagram_paths) since upstream's source keeps
reintroducing whatever variant is wrong for a given file's location.

Runs automatically as a Quarto project pre-render step (see _quarto.yml),
so everything is fresh before `quarto render` / `preview` / `publish`.

Adding a brand-new top-level section (e.g. a future "Monster Manual"):
  1. Add one entry to COLLECTIONS below (folder, section title, optional
     curated order/legacy subsection). Sections are pure expand/collapse
     togglers in the sidebar -- no hub/landing page needed.
  2. Add one or two glob lines to `project.render` in _quarto.yml, e.g.
     "monster_manual/*.md" and "monster_manual/legacy/*.md" (Quarto reads
     that list before pre-render runs, so a brand-new folder can't be
     discovered automatically there).
That's it -- frontmatter and the sidebar section are then fully derived.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

AUTHOR = "Roberto Bisceglie"
VERSION = "3.0"

# One entry per top-level, folder-driven sidebar section. Files present in
# content/<folder>/ but not listed in "curated" are auto-appended (sorted by
# filename, title derived from H1) -- this is what makes newly-synced files
# show up in nav without editing this file.
COLLECTIONS = [
    {
        "folder": "core",
        "section": "SRD",
        "curated": [
            ("loner-3e.md", "Core Rules 3e"),
            ("loner_companion.md", "Companion"),
            ("character_builders_guide.md", "Character Builder's Guide"),
            ("world_builders_guide.md", "World Builder's Guide"),
            ("the_path_not_taken.md", "The Path Not Taken"),
            ("cinematic_action.md", "Cinematic Action"),
        ],
        # "For Kids" lives in geared_towards_loner/, not core/, but belongs
        # in this section's nav.
        "extra_entries": [("geared_towards_loner/tales_and_tumbles.md", "For Kids")],
        "legacy": {
            "folder": "core/legacy",
            "section": "Legacy Core Rules",
            "curated": [
                ("loner-1e.md", "Core Rules 1e (legacy)"),
                ("loner-2e.md", "Core Rules 2e (legacy)"),
            ],
        },
    },
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
            "folder": "adventure_packs/legacy",
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
            # Cross-references geared_towards_loner/legacy/'s own Kwaidan!
            # entry -- no separate copy, just an extra sidebar link.
            "extra_entries": [("geared_towards_loner/legacy/kwaidan.md", "Kwaidan!")],
        },
    },
    {
        "folder": "geared_towards_loner",
        "section": "Geared Towards Loner games",
        # tales_and_tumbles.md is placed under SRD ("For Kids") -- skip it
        # here so it isn't duplicated as a "newcomer".
        "skip": {"tales_and_tumbles.md"},
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
            ("urban_fantasy.md", "Urban Fantasy"),
            ("norse_saga.md", "Norse Saga"),
            ("cthulhu.md", "Cthulhu"),
            ("paranormal_files.md", "Paranormal Files"),
        ],
        "legacy": {
            "folder": "geared_towards_loner/legacy",
            "section": "Geared Towards Loner games (Legacy)",
            "curated": [
                ("kwaidan.md", "Kwaidan!"),
            ],
        },
    },
]

# Document title/subtitle overrides, independent of sidebar labels (most
# pages derive their title from their own H1, which is usually what you
# want -- this is only for pages whose H1 doesn't match their real title,
# or that need a subtitle).
DOC_OVERRIDES = {
    "core/legacy/loner-1e.md": ("Loner - Core Rules 1st Edition (Legacy)", None),
    "core/legacy/loner-2e.md": ("Loner - Core Rules 2nd Edition (Legacy)", None),
    "core/the_path_not_taken.md": (
        None,
        "Two modes of temporal play for solo storytelling: looping fates and irrevocable leaps.",
    ),
    "geared_towards_loner/mech_requiem.md": ("Loner: Mech Requiem", None),
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

# diagrams/ always lives at the repo root, but the private repo's source
# content is inconsistent about the relative path to it (bare "diagrams/",
# "../diagrams/", "../../diagrams/", or the old pre-restructure
# "../../docs/diagrams/") -- and every automated sync from upstream keeps
# reintroducing whichever one is wrong for a given file's depth. Normalize
# it here so the site can't break on this again regardless of what
# upstream ships.
DIAGRAMS_PATH_RE = re.compile(r"(?:\.\./)*(?:docs/)?diagrams/")


def normalize_diagram_paths(body, depth):
    correct_prefix = "../" * depth + "diagrams/"
    return DIAGRAMS_PATH_RE.sub(correct_prefix, body)


def strip_frontmatter(text):
    return FRONTMATTER_BLOCK_RE.sub("", text, count=1)


def clean_title(raw):
    return raw.strip().replace("\\!", "!").replace("**", "").rstrip("\\").strip().replace('"', "'")


def frontmatter_for(rel):
    """(title, subtitle) for a document's own front matter -- independent of
    its sidebar label. title=None means derive from the file's H1."""
    return DOC_OVERRIDES.get(rel, (None, None))


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
    script manages: everything in each COLLECTIONS folder (and its legacy
    subfolder, if any)."""
    rels = []
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
        legacy_contents = [
            {"href": rel, "text": text}
            for rel, text in collection_entries(
                legacy["folder"], legacy.get("curated", []), legacy.get("skip", set())
            )
        ]
        legacy_contents += [{"href": rel, "text": text} for rel, text in legacy.get("extra_entries", [])]
        contents.append({"section": legacy["section"], "contents": legacy_contents})

    return {"section": coll["section"], "contents": contents}


def generate_sidebar():
    tree = [collection_tree_node(coll) for coll in COLLECTIONS]
    lines = ["website:", "  sidebar:", "    style: docked", "    collapse-level: 1", "    contents:"]
    lines += dump_contents(tree, 3)
    (ROOT / "_sidebar-auto.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("OK  _sidebar-auto.yml")


def sync_dir_verbatim(rel_dir):
    """Copies a content/<rel_dir>/ tree to <rel_dir>/ at the repo root as-is
    (no front matter) -- used for diagrams/ and for non-.md assets (images
    etc.) sitting alongside a collection's documents."""
    src_dir = CONTENT / rel_dir
    if not src_dir.exists():
        return
    dest_dir = ROOT / rel_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in src_dir.rglob("*"):
        if src.is_dir() or src.name.startswith("."):
            continue
        rel = src.relative_to(src_dir)
        dest = dest_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)


def sync_collection_assets():
    """Non-.md files (images etc.) sitting directly in a collection folder
    (not diagrams/, which is handled separately) -- copied through verbatim,
    same folder, so relative references from the .md files keep working."""
    for coll in COLLECTIONS:
        for section in (coll, coll.get("legacy") or {}):
            folder = section.get("folder")
            if not folder:
                continue
            src_dir = CONTENT / folder
            if not src_dir.is_dir():
                continue
            dest_dir = ROOT / folder
            for src in src_dir.iterdir():
                if src.is_dir() or src.suffix == ".md" or src.name.startswith("."):
                    continue
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest_dir / src.name)


def main():
    for rel in all_synced_files():
        src = CONTENT / rel
        if not src.exists():
            print(f"WARN missing content/{rel}, skipping")
            continue
        depth = len(Path(rel).parts) - 1
        body = strip_frontmatter(src.read_text(encoding="utf-8"))
        body = normalize_diagram_paths(body, depth)
        title = title_for(rel)
        _, subtitle = frontmatter_for(rel)
        subtitle_line = f'\nsubtitle: "{subtitle}"' if subtitle else ""
        prefix = "../" * depth

        fm = FRONTMATTER_TMPL.format(
            title=title, subtitle_line=subtitle_line, author=AUTHOR, version=VERSION, prefix=prefix
        )
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(fm + body, encoding="utf-8")
        print(f"OK  {rel}")

    sync_dir_verbatim("diagrams")
    sync_collection_assets()
    generate_sidebar()


if __name__ == "__main__":
    main()
