-- RECONSTRUCTED (best-effort): the original of this file was never opened
-- during the session that built it, and was lost to an accidental
-- `git clean`. This reproduces the documented behavior referenced in
-- typst-template.typ's comment: insert a Typst pagebreak before every
-- level-1 heading (except the first) so each chapter starts on a new page.
-- Review before relying on it for anything more specific than that.

local seen_first_h1 = false

function Header(el)
  if el.level == 1 then
    if seen_first_h1 then
      local pagebreak = pandoc.RawBlock('typst', '#pagebreak()')
      return { pagebreak, el }
    else
      seen_first_h1 = true
    end
  end
end
