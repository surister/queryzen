from queryzen import sum


def test_sum():
    assert sum(1, 2) == 3


q1 = QueryLambda.create(
    name='mountain_view',
    query='SELECT * from mountains WHERE height >= :height',
    version=1
)

same_q1 = QueryLambda.get(
    name='mountain_view',
    version=1  # Optional, if it isn't provided, return latest
)

result = same_q1.execute(
    parameters={
        'height': 2,
    }
)
