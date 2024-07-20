.. -*- coding: utf-8 -*-
.. :Project:   package.qualified.name -- Definition of table public.things
.. :Created:   mer 10 lug 2024 15:02:04 CEST
.. :Author:    Lele Gaifax <lele@example.com>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2024 Lele Gaifax
..

.. _public.things:

=========================
 Table ``public.things``
=========================

The table ``public.things`` contains...

.. index::
   triple: Tables; public; things

.. patchdb:script:: Table public.things
   :description: Create table ``public.things``
   :revision: 1
   :language: sql
   :mimetype: text/x-postgresql
   :conditions: postgres
   :depends: Schema public, Table public.TimeStamped
   :file: things.sql

.. patchdb:script:: Init public.things record
   :description: Initialize a new record inserted in the table
                 public.things
   :language: sql
   :mimetype: text/x-postgresql
   :conditions: postgres
   :depends: Table public.things,
             Function public.init_timestamp()

   create trigger trg_ins_ts_public_things
     before insert
     on public.things
     for each row execute procedure init_timestamp();

.. patchdb:script:: Update public.things record
   :description: Update the `changed` field at each modification
                 of a record in the table public.things
   :language: sql
   :mimetype: text/x-postgresql
   :conditions: postgres
   :depends: Table public.things,
             Function public.update_timestamp()

   create trigger trg_upd_ts_public_things,
     before update
     on public.things,
     for each row execute procedure public.update_timestamp();
