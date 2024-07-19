SELECT
  "value"
FROM (
  SELECT
    "value",
    json_extract("value", '$.types') AS "types"
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
  WHERE
    ? IN (
      SELECT
        "value"
      FROM
        json_each("types")
    )
)
;
