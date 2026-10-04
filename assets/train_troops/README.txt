# Quest #18 — Train Troops assets

The quest target is 800 troops.

Required initial anchors:

- barracks_entry.png
- train_action.png
- resource_shortage.png
- resource_option_1.png
- resource_option_2.png
- resource_option_3.png

These names are implementation contracts only until real LDPlayer screenshots
are validated.

## Resource shortage

The game may offer multiple ways to add/use stored resources when training
cannot proceed.

The routine must detect actual visible options rather than tapping fixed
coordinates.

Each option must be validated from real LDPlayer evidence.

## Reusable Grunt flow

Quest #4 can reuse Quest #18's training implementation to create at least
one Grunt when Shelter has no eligible troops.

The final Grunt selector/template will be added after inspecting Barracks.

## Source rule

All production templates must come from real LDPlayer screenshots.

Do not commit synthetic, web, or guessed UI templates.
