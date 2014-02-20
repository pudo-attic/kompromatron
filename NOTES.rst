

Spenden query:

.. code-block:: sql

    SELECT spe.id AS id, spe.jahr AS jahr, spe.betrag_euro AS betrag_eur, par.id AS partei_acronym, par.name AS partei_name, spr.name AS spender_name, spr.strasse AS spender_strasse, spr.plz AS spender_plz, spr.stadt AS spender_stadt, spr.typ AS spender_typ FROM spenden spe, spender spr, parteien par WHERE par.id = spe.partei_id AND spr.id = spe.spender_id AND spr.revision = spe.spender_rev;
