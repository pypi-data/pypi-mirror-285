-- -*- coding: utf-8; sql-product: postgres -*-
-- :Project:   package.qualified.name -- Structure of table public.things
-- :Created:   mer 10 lug 2024 15:02:05 CEST
-- :Author:    Lele Gaifax <lele@example.com>
-- :License:   GNU General Public License version 3 or later
-- :Copyright: © 2024 Lele Gaifax
--

CREATE TABLE public.things (
    field somedomain_t
  , other otherdomain_t

  , PRIMARY KEY (id) -- inherited from public.TimeStamped
) INHERITS (public.TimeStamped)
