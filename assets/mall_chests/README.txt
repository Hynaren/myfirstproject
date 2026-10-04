# Quest #3 — Open free Mall Chests assets

Required production templates:

- special_bundles.png — Special Bundles entry on the left category rail.
- best_sellers.png — Best Sellers entry after Special Bundles is expanded.
- free_chest.png — active/free chest visual in the Best Sellers content.

Source:

- Crop only from current LDPlayer screenshots supplied for Quest #3.
- Do not use web/search screenshots as production templates.

Navigation baseline:

- Shop shortcut is fixed beside the Solo shortcut; code uses the fixed
  shortcut slot rather than a Shop template.
- Left rail is scrolled upward to expose Special Bundles.
- Best Sellers content is scrolled upward by finger to reveal the Free chest.

Template rules:

- Keep enough surrounding UI context for stable matching, but avoid large
  dynamic offer artwork.
- free_chest.png must represent the active/free state, not an already-opened
  or disabled chest.
- Validate every template with detect-only before live execution.
