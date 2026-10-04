# Quest #4 — Shelter Troops assets

Production templates for this quest must come from current real LDPlayer
screenshots.

Required assets:

- shelter_entry.png
  - Shelter building visual used while searching/panning around Castle.
- duration_ok.png
  - OK button in the Shelter duration-selection dialog.
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
- the Shelter action must not be pressed;
- Quest #4 may invoke the reusable Train Troops recovery hook;
- after recovery, the empty state must be checked again.

## Train Troops reuse

The actual Barracks navigation and one-Grunt training flow belongs to
Daily Quest #18 "Train troops in the Barracks".

Quest #4 should call that reusable flow rather than duplicate its UI logic.

## Asset source rule

Templates must be cropped from real LDPlayer screenshots.

Do not commit:

- invented coordinates as visual templates;
- web screenshots;
- synthetic UI;
- troop-type-specific assumptions.
