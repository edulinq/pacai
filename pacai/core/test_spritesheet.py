import glob
import os

import pacai.core.spritesheet
import pacai.test.base

class SpriteSheetTest(pacai.test.base.BaseTest):
    # Load all the known/included sprite sheets.
    def test_load_default_sprite_sheets(self):
        for path in glob.glob(os.path.join(pacai.core.spritesheet.SPRITE_SHEETS_DIR, '*.json')):
            pacai.core.spritesheet.load(path)
