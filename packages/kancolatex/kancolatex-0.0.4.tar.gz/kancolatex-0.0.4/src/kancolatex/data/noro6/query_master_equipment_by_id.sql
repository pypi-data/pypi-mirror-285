SELECT
  "value"
FROM
  (
    SELECT
      json_extract(data, '$.items') as ships
    FROM t_noro6_master_json_media
  ) as base,
  json_each(base.ships)
WHERE
  json_extract("value", '$.id') = ?
