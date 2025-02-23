A `Zen` is a super charged SQL query.

Lets take a normal SQL query.

```sql
-- CrateDB dialect
SELECT
  country,
  height,
  mountain,
  coordinates
FROM
  "sys"."summits"
WHERE
  country = 'CH'
  and height >= 2000
ORDER BY
  'height'
LIMIT 10
```

Using this in your application can lead to problems, if you want to change the SQL, you can break
your application, let's add a version to it to solve the issue.

```sql
-- CrateDB dialect
-- Version: 1
SELECT
  country,
  height,
  mountain,
  coordinates
FROM
  "sys"."summits"
WHERE
  country = 'CH'
  and height >= 2000
ORDER BY
  'height'
LIMIT 10
```

Now, how do you refer to the query? a commit hash? a internal made-up name that has no
programmatic implications? this can lead to confusion, let's add a name to it.

```sql
-- CrateDB dialect
-- Version: 1
-- Name: mountain_summits
SELECT
  country,
  height,
  mountain,
  coordinates
FROM
  "sys"."summits"
WHERE
  country = 'CH'
  and height >= 2000
ORDER BY
  'height'
LIMIT 10
```

What if the query reflects the input from a user, or you simply don't want to re-deploy every time 
you want to change the height, let's parametrize the query, additionally let's add default values.


```sql
-- CrateDB dialect
-- Version: 1
-- Name: mountain_summits
-- Parameters: {'schema', 'table_name', 'country', 'height', 'orderby', 'limit'}
-- Default: {'limit': 100, 'orderby': 'height'}
SELECT
  country,
  height,
  mountain,
  coordinates
FROM
  IDENT(:schema).IDENT(:table_name)
WHERE
  country = :country
  and height >= :height
ORDER BY
  :orderby
LIMIT :limit
```

Now what we have is `Zen`, we can run it with different values, track its performance over different
versions, deploy and test new versions without disturbing your deployed Zens, set Default values
and run it in different Databases and more!