SELECT
  "value"
FROM
  (
    SELECT
      "data" AS "content"
    FROM 
      t_kc_wiki_en_json_ship
    ORDER BY 
      "timestamp" DESC
    LIMIT 1
  ),
  json_each("content")
WHERE
  json_extract("value", '$._japanese_name') = ?
;
