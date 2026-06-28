# Diagram Style Guide

All diagrams in this folder follow a consistent hand-drawn style generated via Graphviz + sketchviz + Inkscape.

## Font

- **Permanent Marker** for all text: graph labels, node labels, edge labels.
- Set on the graph, nodes, and edges separately — Graphviz does not inherit font automatically.

```dot
fontname="Permanent Marker";
node [fontname="Permanent Marker", fontsize=12];
edge [fontname="Permanent Marker", fontsize=12];
```

## Node shape

- Use `shape="rect"` as the default. It renders cleanly in the hand-drawn style.
- `shape="plain"` with `style="rounded"` is also acceptable for softer nodes (see `get_started.dot`).
- Do not use `diamond`, `circle`, `doublecircle`, or `ellipse`. Decision nodes are still `rect` — write the question as the label text.

## Labels

- Write all node labels in **ALL CAPS**.
- Use `\n` for line breaks within labels. Keep lines short (3–5 words each).
- Graph title: set with `label = "TITLE";` and `labelloc="t";` at the graph level.

## Colors and export

```dot
bgcolor=white;
dpi=300;
```

These ensure a white background and a crisp export at 2000px width (set in `convert.sh`).

## Edges

- Solid edges are the default.
- Use `style=dotted` for optional or informational connections.
- Use `style=dashed` for fallback or secondary paths.
- Keep edge labels short (one or two words: `Yes`, `No`, `informs`).

## Clusters

Use sparingly. If used, give the cluster a short `label` in ALL CAPS and avoid `style=dashed` on the cluster border — it looks noisy at the hand-drawn render stage.

## File naming

Name files after the diagram content, lowercase with underscores:

```
scene_breakdown.dot
quiet_moments_session_flow.dot
```

## Building diagrams

From inside `docs/diagrams/`:

```bash
./convert.sh
```

This processes every `.dot` file in the folder and outputs `.svg` and `.png` for each. The PNG is what gets embedded in Markdown documents.

## Embedding in Markdown

Use a plain image tag with a relative path from the document:

```markdown
![](diagrams/quiet_moments_session_flow.png)
```

(Adjust the relative path if the Markdown file is outside `docs/`.)
