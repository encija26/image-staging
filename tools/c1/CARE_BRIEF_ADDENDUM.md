# Addendum for this run (26 Oct 2026)

- Packet layout: {"out": path, "products": [{"handle", "rows": [{row, vendor_name, bh_name, colour, materials_and_dimensions, vendor_description, modway_fabric_care}]}]}.
- `modway_fabric_care` = "NONE FOUND" on a piece with no upholstery (tables, case goods, beds without a fabric panel, lighting, mirrors, metal or wood chairs) simply means there is no fabric. Write the care from its materials; no Review note for that.
- Apply rule 3 (no cleaning code) and its Review note ONLY where the piece has upholstery or a fabric/vegan leather part and the field says NONE FOUND.
- Same product in different colours: identical care text (no colour words needed). Different fabric per colour (e.g. velvet vs bouclé variant): follow each row's own fabric care.
- The materials_and_dimensions text is the authority on what materials the piece has (rule 8). Never use "—" or "–".
- Output exactly as the brief says: one JSON object keyed by row number string, value {"M": text, "R": review or ""}. Every row in the packet must be present. Reply with only the output path and row count.
