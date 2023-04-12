### hexlet test, linter status and maintainability:
[![Actions Status](https://github.com/ConstableFraser/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/ConstableFraser/python-project-83/actions)
[![Linter](https://github.com/ConstableFraser/python-project-83/actions/workflows/Linter.yml/badge.svg)](https://github.com/ConstableFraser/python-project-83/actions/workflows/Linter.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/02d7cf3a054818153080/maintainability)](https://codeclimate.com/github/ConstableFraser/python-project-83/maintainability)

# PAGE SEO-ANALYZER
## useful features:
1. scanning main page of website for seo-suitability (tags: h1, title and description)
2. checking website for availability

## how it works:
1. type the name of the website in according with requirements and push the Enter
2. information page about website will open
3. push the "Запустить проверку" (launch checking)
4. see result of checking at the table below

![Guide](res/Page_analyzer.jpg)

## demo version:
https://page-analyzer-service.onrender.com/


**technical information**
python, poetry, flask, gunicorn, jinja2, beautifulsoup, psycopg2, postgresql, bootstrap


# HOW TO INSTALL AND USE

```
make install - to install dependencies
make start - to start the application
```
