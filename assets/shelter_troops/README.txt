# Quest #4 — Shelter Troops assets

Production templates for this quest must come from current real LDPlayer
screenshots.

Required assets:

- shelter_entry.png
  - Shelter building visual used while searching/panning around Castle.
- no_troops.png
  - Account-independent negative-state message:
    "You need to train more Troops at the Barracks."
- shelter_action.png
  - Active Shelter button on the troop-selection screen.

## no_troops.png rule

Do NOT create troop-specific positive templates.

Every account can have different troop types, counts, and research state.
The stable empty-state message is the reliable cross-account signal.

If no_troops.png is detected:

- there are no eligible troops;
- the routine must stop;
- the Shelter button must NOT be pressed.

The supplied LDPlayer empty-state screenshot was used to identify the crop
candidate for no_troops.png. The production asset still needs to be placed
in this directory and validated by the real Detector.

## Asset source rule

Templates must be cropped from real LDPlayer screenshots.

Do not commit:

- invented coordinates as visual templates;
- web screenshots;
- synthetic UI;
- troop-type-specific assumptions.

The Castle search itself uses bounded panning, so the Shelter building does
not need a fixed coordinate.
