import unittest,importlib.util
from ml.image_quality import alternating_border,check_cutout
class BorderTests(unittest.TestCase):
    def test_regular_checker_pattern(self):
        self.assertTrue(alternating_border([(220,220,220,255) if (i//20)%2 else (240,240,240,255) for i in range(200)]))
    def test_plain_gray_and_green_do_not_trigger(self):
        self.assertFalse(alternating_border([(220,220,220,255)]*200))
        self.assertFalse(alternating_border([(40,120,60,255)]*200))
@unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow required')
class CutoutTests(unittest.TestCase):
    def test_checkerboard_cutout_is_withheld(self):
        from PIL import Image,ImageDraw
        im=Image.new('RGB',(240,240));draw=ImageDraw.Draw(im)
        for y in range(0,240,20):
            for x in range(0,240,20):draw.rectangle((x,y,x+19,y+19),fill=(240,240,240) if (x//20+y//20)%2 else (220,220,220))
        draw.ellipse((60,40,180,200),fill=(30,120,60))
        self.assertIn('checkerboard',check_cutout(im))
    def test_alpha_cutout_is_withheld_but_plain_background_is_not(self):
        from PIL import Image
        self.assertIn('transparent',check_cutout(Image.new('RGBA',(240,240),(0,100,0,0))))
        self.assertIsNone(check_cutout(Image.new('RGB',(240,240),(220,220,220))))
