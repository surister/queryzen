# Same hybrid-search query, different places.
While developing and investigating use cases for CrateDB I often find myself doing hybrid-search 
in different places, sometimes it's a python script, a fastapi backend or some integration/tookit.
The query is pretty much the same or very similar.

I'm constantly copy-pasting the query and adding new tests, I'm repeating myself all the time,
with QueryZen I can develop once, test once and deploy once.

If there was some change in how we do hybrid-search in CrateDB, I would need to change it
everywhere, with `QueryZen` I can just create a new Zen, and change the version in the applications.

## Parametrizing the hybrid-search query.
The query can originally be found in: [CrateDB Blog: Hybrid Search Explained](https://cratedb.com/blog/hybrid-search-explained).

```sql
WITH bm25 as (
  SELECT
    _score,
    RANK() OVER (
      ORDER BY
        _score DESC
    ) as rank,
    title
  FROM
    fs_search
  WHERE
    MATCH("content", 'knn search')
  ORDER BY
    _score DESC
),
vector as (
  SELECT
    _score,
    RANK() OVER (
      ORDER BY
        _score DESC
    ) as rank,
    title
  FROM
    fs_search
  WHERE
    KNN_MATCH(
      xs,
      [vector...],
      15
    )
)
SELECT
  TRUNC((1.0 / (bm25.rank + 60)) + (1.0 / (vector.rank + 60)), 6) as final_rank,
  bm25.rank as bm25_rank,
  vector.rank as vector_rank,
  bm25.title
FROM
  bm25,
  vector
WHERE
  bm25.title = vector.title
ORDER BY final_rank DESC
```

The first things that we can parametrize are the `vector`, and the match for bm25, `'knn search'`,
we could and should parametrize more things like: the table names, the column names and the RRF k parameter,
which is hardcoded as 60. For now we will only do the match terms.


```python
from queryzen import QueryZen

qz = QueryZen()

query = """
WITH bm25 as (
  SELECT
    _score,
    RANK() OVER (
      ORDER BY
        _score DESC
    ) as rank,
    title
  FROM
    fs_search
  WHERE
    MATCH("content", :match_term)
  ORDER BY
    _score DESC
),
vector as (
  SELECT
    _score,
    RANK() OVER (
      ORDER BY
        _score DESC
    ) as rank,
    title
  FROM
    fs_search
  WHERE
    KNN_MATCH(
      xs,
      :vector,
      15
    )
)
SELECT
  TRUNC((1.0 / (bm25.rank + 60)) + (1.0 / (vector.rank + 60)), 6) as final_rank,
  bm25.rank as bm25_rank,
  vector.rank as vector_rank,
  bm25.title
FROM
  bm25,
  vector
WHERE
  bm25.title = vector.title
ORDER BY final_rank DESC
"""

qz.create(collection='crate', name='hybrid-search', query=query)
```

Now in any Python program I can reuse the query!

### hybrid_search.py
```python
from queryzen import QueryZen, exceptions
from .vectors import make_vector

qz = QueryZen()

def hybrid_search(search_phrase: str):
    """Searches a search_phrase in the Database, using hybrid search (BM25 + vector search)"""
    try:
        zen = qz.get(collection='crate', name='hybrid-search', version=1)
    except exceptions.ZenDoesNotExist:
        # handle zen not existing.
        pass
    
    result = qz.run(zen,
                    database='crate',
                    match_term=search_phrase,
                    vector=make_vector(search_phrase))    
    return result.rows
```

Now in my collection `crate`, there is a zen named `hybrid_search` with version 1, if I were to update
the query, I could create a new one, with version 2, and test it. In the end application I would
only need to change the `version=1` to `version=2`.

Furthermore, I could just ship in a small package the `hybrid_search` function, and ship in my
entire company's Python ecosystem the same way of doing hybrid search, centralized.

