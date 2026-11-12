"""Replace the picture on a slide with a new PNG, keeping its position and width.
Usage: python swap_image.py deck.pptx out.pptx SLIDE_TITLE_TEXT new.png [--add]
Finds the first slide whose text contains SLIDE_TITLE_TEXT. Replaces its largest picture
(crop cleared, height set from the PNG's aspect ratio, capped at the old visible height).
--add: slide has no picture yet; insert full-width below the title instead."""
import sys
from pptx import Presentation
from pptx.oxml.ns import qn
from PIL import Image
src, out, title, png = sys.argv[1:5]
add = '--add' in sys.argv
p = Presentation(src)
slide = next(s for s in p.slides if any(sh.has_text_frame and title in sh.text_frame.text for sh in s.shapes))
w, h = Image.open(png).size
if add:
    W = int(p.slide_width * 0.85); H = int(W * h / w)
    slide.shapes.add_picture(png, int(p.slide_width * 0.075), int(p.slide_height * 0.2), W, H)
else:
    pic = max((x for x in slide.shapes if x.shape_type == 13), key=lambda x: x.width * x.height)
    max_h = int(pic.height * (1 - pic.crop_top - pic.crop_bottom))
    part, rId = slide.part.get_or_add_image_part(png)
    pic._element.blipFill.find(qn('a:blip')).set(qn('r:embed'), rId)
    pic.crop_left = pic.crop_right = pic.crop_top = pic.crop_bottom = 0
    W = pic.width; H = int(W * h / w)
    if H > max_h: H = max_h; pic.width = int(H * w / h)
    pic.height = H
p.save(out); print('saved', out)
