A `Zen` is a supercharged SQL query.

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

Using raw SQL in your application can lead to certain problems, changing raw SQL is prone to mistakes, we have no
way of easily rolling back a query, or tracking its performance history across changes. 
Let's add a version to it to solve the issue.

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

Now, how do you refer to the query? a commit hash? an internal made-up name that has no
programmatic implications? let's add a name to it.

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

What if the query needs an input from the user, or you simply don't want to re-deploy every time 
you want to change a parameter, let's parametrize the query, additionally let's add default values.


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

What we did is implement all of this programmatically in HTTP for you, so you don't have to.