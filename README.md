# lizheng-mdb-to-old-txt

Hermes skill for converting Lizheng new-version Access `.mdb` databases into old-version TXT interface files.

## Files

- `SKILL.md`: the Hermes skill definition
- `convert_new_mdb_to_old.py`: Python exporter that reads `.mdb` with `mdbtools` and writes old-version TXT interface files

## Purpose

This repository stores the reusable Hermes skill distilled from a real-world workflow for:
- reading `.mdb` with `mdbtools`
- mapping known fields to old TXT interface segments
- exporting `gb18030`-encoded TXT files
- following validated Lizheng drillhole/project grouping rules

## Current TXT Output Rules

The current exporter follows these confirmed formatting rules for old-version Lizheng TXT interface files.

### 1. No field-name example header rows

The output TXT must contain real data rows only.

Incorrect:

```text
#GC#GCKCJD\tGCJSDW\t...
详细勘察\t...
```

Correct:

```text
#GC#详细勘察\t...
```

### 2. Segment marker directly joins the first field value

There must be:
- no space after the marker
- no extra tab after the marker

Examples:

```text
#GC#详细勘察\t...
#ZK#GZK1\t控制孔\t...
#TC#素填土\t...
```

### 3. Drillhole main record format

The drillhole master record stays on one line:

```text
#ZK#钻孔编号\t钻孔类型\tX\tY\t...
```

Example:

```text
#ZK#GZK1\t控制孔\t...
```

### 4. Drillhole child-project grouping rule

For project segments that belong to a drillhole and contain `ZKBH` (such as `TC`, `BG`, `DT`, `SW`, and similar sections), output must be grouped like this:

1. output a standalone drillhole line first
2. then output the project rows for that drillhole
3. only emit that standalone `#ZK#钻孔编号` once per drillhole per project block
4. when switching to the next drillhole, emit a new standalone `#ZK#钻孔编号`

Example:

```text
#ZK#GZK26
#TC#素填土\t...
#TC#粉质黏土\t...
#TC#细砂\t...
#ZK#GZK25
#TC#素填土\t...
```

### 5. No extra blank lines

The exporter writes Windows-style line endings (`\r\n`) and should not introduce blank rows between:
- `#ZK#钻孔编号`
- and its following child project rows

### 6. Encoding

Generated TXT files use:

- `gb18030`

## Notes on Field Mapping

### Confirmed alias mapping

The `QY` segment includes confirmed alias mappings where the new database uses old field names with a trailing underscore, for example:

- `QYZLMD -> QYZLMD_`
- `QYBZ -> QYBZ_`
- `QYHSL -> QYHSL_`
- `QYYX -> QYYX_`
- `QYSY -> QYSY_`
- `QYZXMD -> QYZXMD_`
- `QYZDMD -> QYZDMD_`
- and other confirmed `QY` underscore aliases already included in the script

### Conservative mapping areas

Some sections are still exported with a conservative strategy of “same-name direct mapping first, otherwise blank”, especially where business semantics are not yet fully confirmed. This particularly applies to complex consolidation-related sections such as:

- `GJ`
- `GY`

## Verification Checklist

After modifying the exporter, verify that:

- the TXT starts with real segment data, not comment lines or example headers
- `#GC#`, `#ZK#`, `#TC#` markers directly touch the first data field
- drillhole master records remain on one line
- child project blocks emit a standalone `#ZK#钻孔编号` before project rows
- the same drillhole/project block does not repeat the standalone `#ZK#钻孔编号`
- there are no extra blank lines
- the file encoding remains `gb18030`
