import pytest
from page_analyzer.app import app


@pytest.fixture()
def app_context():
    app_context = app
    app_context.config.update({
                              "TESTING": True
                              })
    return app_context


@pytest.fixture()
def client(app_context):
    return app_context.test_client()


def tests_correct_url(client):
    payload = {'url': '',
               'check': 'Проверить'
               }
    response = client.post('/urls', data=payload)
    assert response.status_code == 302

    payload['url'] = 'http://ozon().ru'
    response = client.post('/urls', data=payload)
    assert response.status_code == 302

    payload['url'] = 'url_is_incorrect_because_contains_more_ \
                      than_255_symbols_url_is_incorrect_because_\
                      contains_more_than_255_symbols_url_is_\
                      incorrect_because_contains_more_than_255_\
                      symbols_url_is_incorrect_because_contains_\
                      more_than_255_symbols_url_is_incorrect_because\
                      _contains.html'
    response = client.post('/urls', data=payload)
    assert response.status_code == 302

    response = client.get('/urls')
    assert response.status_code == 200

    response = client.get('/urls/23452145124351')
    assert response.status_code == 404
