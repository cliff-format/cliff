# CLIFF Prompt Assembly for AI Translation

CLIFF 1.0 is designed so a translation model can read the same file it will
edit. No intermediate JSON wrapping is needed. This document defines the
recommended (non-normative) prompt assembly.

## 1. Presentation

Send the model:

1. the `CLIFF 1.0` version line and the header;
2. the current section header and its group metadata;
3. the batch of entries to translate (each with its effective context);
4. instruction lines built from the header `standard` fields;
5. the referenced glossary entries relevant to the batch (from the files
   listed in `dependency`), in CLIFF `variant: glossary` form.

Delete `#` comment lines. They are developer-only and may make the model
treat them as translation input.

## 2. Effective context computation

Before prompting, compute for each entry:

- effective `context` = group `context` lines + entry `context` lines
  (joined with spaces);
- effective `type` = entry or group value (required);
- effective `emotion` = entry value, group value, or the default derived from
  `type` (`objective` for non-speech, `neutral` for speech);
- effective `max-width` = entry or group value;
- relevant glossary entries from `dependency` files.

If a field is absent, output nothing — do not inject empty placeholders.

## 3. Recommended prompt

```text
Translate the following localization file from <source-language> to
<target-language>.

Rules:
- Keep the CLIFF structure exactly: version line, header keys, group paths,
  entry ids, field keys, and the order of entries.
- Fill in target for each entry and set the correct status.
- Preserve ICU MessageFormat syntax exactly (MF1 {...} and MF2 {{...}}).
- Follow the standard lines and the attached glossary entries.
- Match the declared type and emotion tags.
- Respect max-width display cells (Latin/digit=1, CJK/fullwidth/emoji=2).
- Translate with faithfulness, expressiveness, and elegance: keep wordplay
  and register; use natural <target-language> word order.

<CLIFF document here>
```

## 4. Batch boundaries

Batch by section. Never split an entry, and always repeat the section header
and its group metadata in each batch. Entries carry their own context, so
cross-section dialogue dependencies should be summarized by the authoring
tool in the entry `context` field.

## 5. Validation feedback loop

After the model edits the file, run the validator. Because every error
reports a line number and the allowed values, the corrective prompt is:

```text
The file failed validation. Fix only these lines:

<validator output>

<original or minimal surrounding CLIFF lines>
```

Do not ask the model to reformat the whole file; line-local repair is CLIFF's
failure-recovery model.