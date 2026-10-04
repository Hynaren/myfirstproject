# Quest #18 — Train Troops assets

Production templates confirmed from real LDPlayer screenshots:

- grunt_card.png — Tier-1 Grunt card.
- quantity_field.png — troop quantity field.
- quantity_keypad.png — numeric keypad after opening quantity.
- train_action.png — Train button.
- resource_shortage.png — shortage dialog/header state.
- resource_use.png — Use button in the Auto Use dialog.
- finish_now.png — Finish Now / Speed Up button.

Still required:

- barracks_entry.png — Barracks building in the Castle.

## Confirmed flow

Barracks
→ Grunt
→ quantity field
→ numeric keypad
→ 800
→ confirm
→ Train

If resource shortage appears:

shortage
→ Use
→ game auto-fills resources
→ game auto-presses Train
→ Finish Now

Do not press Train again after Use.

## Asset source rule

All production templates must come from real LDPlayer screenshots.

The current supplied screenshots are sufficient for every asset above except
barracks_entry.png, because they show the inside of Barracks rather than the
Barracks building in Castle.

Do not create synthetic, web, or guessed templates.


## Final speed-up board assets

After Finish Now, the game opens the time-speed board:

Finish Now -> Auto Use -> Use Time Speed

Required production templates:

- auto_use.png — Auto Use control on the speed-up board.
- use_time_speed.png — Use Time Speed button on the speed-up board.

Both controls are detected by Vision before tapping.
