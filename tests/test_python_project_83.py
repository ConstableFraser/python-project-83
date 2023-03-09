import os
import pytest
from page_analyzer.app import app
from dotenv import load_dotenv, find_dotenv
from page_analyzer.find_value_html import get_value
from page_analyzer.get_content import get_content


load_dotenv(find_dotenv())
dbname = os.environ.get("DBNAME")
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")


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


@pytest.mark.parametrize(
    "tag, html, correct",
    [("h1",
      "tests/fixtures/correct/ramokna_ru.html",
      "tests/fixtures/correct/ramokna_h1.txt"),
     ("title",
      "tests/fixtures/correct/ramokna_ru.html",
      "tests/fixtures/correct/ramokna_title.txt"),
     ("content",
      "tests/fixtures/correct/ramokna_ru.html",
      "tests/fixtures/correct/ramokna_description.txt")])
def test_correct(tag, html, correct):
    value = get_value(get_content(html), tag)
    assert get_content(correct) == value


def test_get_value_unknown():
    text = get_content("tests/fixtures/correct/ramokna_ru.html")
    value = get_value(text, "meta")
    assert value is None


def test_get_content():
    value = open("tests/fixtures/example_txt_file.txt", "r").read()
    assert "this is a text file" == value


@pytest.mark.parametrize(
    "tag, html, correct",
    [pytest.param("h1",
                  "tests/fixtures/uncorrect/ru_hexlet_io.html",
                  None,
                  marks=pytest.mark.xfail),
     pytest.param("title",
                  "tests/fixtures/uncorrect/ya_ru.html",
                  "",
                  marks=pytest.mark.xfail),
     pytest.param("content",
                  "tests/fixtures/uncorrect/ozon_ru.html",
                  "",
                  marks=pytest.mark.xfail)])
def test_fails(tag, html, correct):
    value = get_value(get_content(html), tag)
    assert correct == value
