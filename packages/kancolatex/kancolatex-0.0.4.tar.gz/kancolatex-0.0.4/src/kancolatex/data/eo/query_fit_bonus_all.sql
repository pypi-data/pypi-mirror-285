SELECT
  "value"
FROM (
  SELECT
    "value",
    json_extract("value", '$.ids') AS "ids"
  FROM
    (
      SELECT
        "data"
      FROM
        t_eo_en_json_fit_bonus
      ORDER BY
        "timestamp" DESC
      LIMIT 1
    ),
    json_each("data")
)
;
