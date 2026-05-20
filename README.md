# lizheng-mdb-to-old-txt

Hermes skill for converting Lizheng new-version Access `.mdb` databases into old-version TXT interface files.

## Files

- `SKILL.md`: the Hermes skill definition

## Purpose

This repository stores the reusable Hermes skill distilled from a real-world workflow for:
- reading `.mdb` with `mdbtools`
- mapping known fields to old TXT interface segments
- exporting `gb18030`-encoded TXT files
- following validated Lizheng drillhole/project grouping rules
