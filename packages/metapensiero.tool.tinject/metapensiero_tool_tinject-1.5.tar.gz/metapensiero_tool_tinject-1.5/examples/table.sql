«header»
CREATE TABLE «schema_name».«table_name» (
    field somedomain_t
  , other otherdomain_t

  , PRIMARY KEY (id) -- inherited from public.TimeStamped
) INHERITS (public.TimeStamped)
