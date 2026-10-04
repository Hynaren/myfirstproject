from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class OpenFreeMallChestsRoutine(BaseQuestRoutine):
    """Daily Quest #3: open one currently free Mall chest."""

    QUEST_ID = "open_free_mall_chests"

    DEFAULT_WAIT_SECONDS = 0.8
    DEFAULT_SWIPE_DURATION = 350
    MAX_CHEST_SCROLLS = 6
    MAX_LEFT_MENU_SWIPES = 4

    # The Castle shop shortcut is a fixed event-slot style button beside
    # the Solo shortcut. Its artwork changes, so coordinates are the stable
    # navigation contract for this shortcut.
    SHOP_SHORTCUT_CENTER = (355, 67)
    SHOP_SHORTCUT_JITTER = 3

    # Scroll the left category rail upward until Special Bundles is visible.
    LEFT_MENU_SWIPE = (120, 420, 120, 180)

    # Scroll the Best Sellers content downward (finger moves upward) so the
    # free chest near the bottom becomes visible.
    RIGHT_CONTENT_SWIPE = (820, 440, 820, 180)

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        special_bundles_template=None,
        best_sellers_template=None,
        free_chest_template=None,
    ):
        super().__init__(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            popup_manager=popup_manager,
        )

        asset_dir = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "mall_chests"
        )

        self.special_bundles_template = Path(
            special_bundles_template
            or asset_dir / "special_bundles.png"
        )
        self.best_sellers_template = Path(
            best_sellers_template
            or asset_dir / "best_sellers.png"
        )
        self.free_chest_template = Path(
            free_chest_template
            or asset_dir / "free_chest.png"
        )

    def log(self, message):
        if self.logger:
            self.logger(message)

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            f"[OpenFreeMallChestsRoutine] Template missing: {path}"
        )
        return False

    def _templates_ready(self):
        return (
            self._template_ready(self.special_bundles_template)
            and self._template_ready(self.best_sellers_template)
            and self._template_ready(self.free_chest_template)
        )

    def _open_shop(self):
        self.log(
            "[OpenFreeMallChestsRoutine] "
            f"Opening Shop shortcut at {self.SHOP_SHORTCUT_CENTER}"
        )

        if not self.action_engine.tap(
            *self.SHOP_SHORTCUT_CENTER,
            jitter=self.SHOP_SHORTCUT_JITTER,
        ):
            self.log(
                "[OpenFreeMallChestsRoutine] Shop shortcut TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _open_special_bundles(self):
        # Special Bundles can be several positions below the initial Shop
        # category view. Keep swiping the left rail upward until the target
        # is visible, with a bounded maximum.
        for swipe_index in range(self.MAX_LEFT_MENU_SWIPES):
            self.log(
                "[OpenFreeMallChestsRoutine] "
                f"Left category swipe "
                f"{swipe_index + 1}/{self.MAX_LEFT_MENU_SWIPES}"
            )

            if not self.action_engine.swipe(
                *self.LEFT_MENU_SWIPE,
                duration=self.DEFAULT_SWIPE_DURATION,
            ):
                self.log(
                    "[OpenFreeMallChestsRoutine] "
                    "Special Bundles menu scroll FAILED"
                )
                return False

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

            result = self.action_engine.detect(
                str(self.special_bundles_template)
            )

            if result is not None and result.found:
                self.log(
                    "[OpenFreeMallChestsRoutine] "
                    f"Special Bundles found at {result.center} "
                    f"confidence={result.confidence:.4f}"
                )

                if not self.action_engine.tap(*result.center):
                    self.log(
                        "[OpenFreeMallChestsRoutine] "
                        "Special Bundles TAP FAILED"
                    )
                    return False

                self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
                return True

        self.log(
            "[OpenFreeMallChestsRoutine] "
            "Special Bundles NOT FOUND after bounded left-menu scrolls"
        )
        return False

    def _open_best_sellers(self):
        result = self.action_engine.detect(
            str(self.best_sellers_template)
        )

        if result is None or not result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] Best Sellers NOT FOUND"
            )
            return False

        self.log(
            "[OpenFreeMallChestsRoutine] "
            f"Best Sellers found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[OpenFreeMallChestsRoutine] Best Sellers TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _find_free_chest(self):
        result = self.action_engine.detect(
            str(self.free_chest_template)
        )

        if result is None:
            return None

        if result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                f"Free chest found at {result.center} "
                f"confidence={result.confidence:.4f}"
            )
            return result

        return None

    def _scroll_to_free_chest(self):
        # Best Sellers may contain a long offer list. Keep swiping the
        # right content area upward until the Free chest is exposed.
        for scroll_index in range(self.MAX_CHEST_SCROLLS + 1):
            self.log(
                "[OpenFreeMallChestsRoutine] "
                f"Best Sellers chest scan "
                f"{scroll_index + 1}/{self.MAX_CHEST_SCROLLS + 1}"
            )

            result = self._find_free_chest()
            if result is not None:
                return result

            if scroll_index >= self.MAX_CHEST_SCROLLS:
                break

            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest not visible; scrolling Best Sellers content "
                f"toward end ({scroll_index + 1}/{self.MAX_CHEST_SCROLLS})"
            )

            if not self.action_engine.swipe(
                *self.RIGHT_CONTENT_SWIPE,
                duration=self.DEFAULT_SWIPE_DURATION,
            ):
                self.log(
                    "[OpenFreeMallChestsRoutine] "
                    "Best Sellers content scroll FAILED"
                )
                return None

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        self.log(
            "[OpenFreeMallChestsRoutine] Free chest NOT FOUND"
        )
        return None

    def _claim_free_chest(self, result):
        if not self.action_engine.tap(*result.center):
            self.log(
                "[OpenFreeMallChestsRoutine] Free chest TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        # The active/free chest is the state anchor. Once claimed, this
        # exact visual should no longer be present in the Best Sellers list.
        verify_result = self.action_engine.detect(
            str(self.free_chest_template)
        )

        if verify_result is None:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest verification FAILED: screenshot"
            )
            return False

        if verify_result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest still visible after claim"
            )
            return False

        self.log(
            "[OpenFreeMallChestsRoutine] "
            "Free chest claimed and verified"
        )
        return True

    def run(self):
        self.log("[OpenFreeMallChestsRoutine] START")

        if not self._templates_ready():
            return False

        if not self._open_shop():
            return False

        if not self._open_special_bundles():
            return False

        if not self._open_best_sellers():
            return False

        chest = self._scroll_to_free_chest()
        if chest is None:
            return False

        if not self._claim_free_chest(chest):
            return False

        self.log("[OpenFreeMallChestsRoutine] DONE")
        return True
