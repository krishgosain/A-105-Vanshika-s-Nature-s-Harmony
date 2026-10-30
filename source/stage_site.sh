#!/bin/bash
# copy final renders into the site: full panoramas + small previews + hero shots + plan
set -e
cd /home/claude/house
F=build2/final
for n in entrance foyer living dining balcony kitchen br3 br2 master mbath; do
  if [ -f $F/$n.jpg ]; then
    python3 -c "
from PIL import Image
im=Image.open('$F/$n.jpg').convert('RGB')
im.save('site/pano/$n.jpg',quality=86,optimize=True,progressive=True)
im.resize((1536,768),Image.LANCZOS).save('site/pano/${n}_s.jpg',quality=80,optimize=True,progressive=True)"
  fi
done
for h in hero_living hero_dining hero_master hero_kitchen; do [ -f $F/$h.jpg ] && python3 -c "
from PIL import Image; Image.open('$F/$h.jpg').convert('RGB').save('site/img/$h.jpg',quality=86,optimize=True,progressive=True)"; done
[ -f $F/plan.jpg ] && python3 -c "
from PIL import Image; Image.open('$F/plan.jpg').convert('RGB').resize((1540,810),Image.LANCZOS).save('site/img/plan.jpg',quality=86,optimize=True)"
du -sh site/pano site/img site/model
