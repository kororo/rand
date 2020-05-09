from tests import create_rand


def test_urls():
    from rand.providers.url.url import RandUrlBaseProvider

    urls = {
        'names_json': 'https://raw.githubusercontent.com/kororo/rand/master/tests/data/names.json',
        'names_txt': 'https://raw.githubusercontent.com/kororo/rand/master/tests/data/names.txt'
    }

    url = RandUrlBaseProvider(prefix='url')
    url.target.urls = urls
    rand = create_rand()
    rand.register_provider(url)
    assert rand.gen('(:url_get:)', ['names_json']) == ['test']
    assert rand.gen('(:url_get_names_json:)-(:ds_get_names_txt:)') == ['test-test']

