# -*- coding: utf-8 -*-
# :Project:   package.qualified.name -- Entities in schema public
# :Created:   Wed 17 Jul 2024 22:25:14 CEST
# :Author:    Lele Gaifax <lele@example.com>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024 Lele Gaifax
#

from sqlalchemy.orm import mapper

from ...tables import public as t

## ⌄⌄⌄ tinject import marker ⌄⌄⌄, please don't remove!
from .thing import Thing

## ⌃⌃⌃ tinject import marker ⌃⌃⌃, please don't remove!

mapper(Thing, t.things, properties={
})
