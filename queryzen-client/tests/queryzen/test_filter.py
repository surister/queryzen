def test_filter_simple(queryzen):
    """
    Test queryzen.filter
    """

    qs = queryzen.filter()
    assert not qs  # Is empty

    q = queryzen.create('z', 'select 1')
    queryzen.create('z', 'select 2')

    qs = queryzen.filter()

    assert len(qs) == 2
    assert isinstance(qs, list)
    assert qs[0].version == 1
    assert q == qs[0]
    assert qs[1].version == 2


def test_filter_many(queryzen):
    qz = queryzen
    name = 'name1'
    collection = 'col1'
    version = 1
    qz.create(name, query='q', collection=collection)
    qz.create(name, query='q', collection=collection)
    qz.create('name2', query='q')

    result = qz.filter(name=name)

    assert all(map(lambda z: z.name == name, result))
    assert all(map(lambda z: z.collection == collection, result))
    assert not all(map(lambda z: z.version == version, result))

    result = qz.filter(version=version)

    assert all(map(lambda z: z.version == version, result))
    assert not all(map(lambda z: z.name == name, result))
    assert not all(map(lambda z: z.collection == collection, result))


def test_filter_advanced_filters(queryzen):
    """Test additional and more advanced filtering like filtering by children and gt/lt/contains"""

    queryzen.create(collection='m', name='mountain_view', query='q', version=1)
    queryzen.create(collection='m', name='mountain_view', query='q', version=2)
    queryzen.create(collection='ma', name='mountain_view', query='q', version=1)
    queryzen.create(collection='ma', name='pellizcola', query='q', version=1)
    correct_query = queryzen.create(collection='ma',
                                    name='pellizcola',
                                    query="select 'correct_query'",
                                    version=2)

    queryzen.run(correct_query) # We run so executions__sate is 'VA' (valid)

    r = queryzen.filter(collection_contains='ma',
                        name__contains='l',
                        version__gt=1,
                        executions__state='VA')

    assert len(r) == 1
