A `Zen` is a named, versioned and parametrized SQL query.

But where does it come from?

Let's take a normal SQL query.

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

Using raw SQL in your application can lead to certain problems: changing raw SQL is prone to mistakes, there is no
way of easily rolling back a query if a developer makes a mistake, or tracking its performance across changes. 

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
programmatic implications? let's add a name to it so we can reference it during its lifetime.

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

Now what we have is `Zen`, If you run this with `QueryZen`:

You can run it with different values, track its performance over different
versions, deploy and test new versions without disturbing your deployed Zens, set default values, run it in different
databases, deploy it once and use it in several applications.
