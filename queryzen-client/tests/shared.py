from queryzen import Zen


def check_zen(zen: Zen, name, query, version):
    assert isinstance(zen, Zen)
    assert zen.query == query
    assert zen.name == name
    assert zen.version == version
