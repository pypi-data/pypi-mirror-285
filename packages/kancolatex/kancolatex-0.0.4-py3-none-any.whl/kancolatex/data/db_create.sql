CREATE TABLE IF NOT EXISTS t_kc_wiki_en_json_ship (
    "timestamp" INT,
    "data" TEXT
);

CREATE TABLE IF NOT EXISTS t_kc_wiki_en_json_equipment(
    "timestamp" INT,
    "data" TEXT
);

CREATE TABLE IF NOT EXISTS t_eo_en_json_fit_bonus(
    "timestamp" INT,
    "data" TEXT
);

CREATE TABLE IF NOT EXISTS t_noro6_master_json_media(
    "timestamp" INT,
    "data" TEXT
);

CREATE TABLE IF NOT EXISTS t_kc3_translation_json_items(
    "timestamp" INT,
    "data" TEXT
);

CREATE TABLE IF NOT EXISTS t_kc3_translation_json_ships(
    "timestamp" INT,
    "data" TEXT
);

VACUUM;
