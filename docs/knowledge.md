# FreelanSign Knowledge Base

## General

### Architecture

#### Backend

- Architecture Générale du backend

```bash
total 888
drwxr-xr-x@ 22 bertrandrenaudin  staff   704B Nov  3 21:42 .
drwxr-xr-x@ 23 bertrandrenaudin  staff   736B Nov  4 22:37 ..
-rw-r--r--@  1 bertrandrenaudin  staff   224K Oct 27 09:48 .coverage
-rw-r--r--@  1 bertrandrenaudin  staff   303B Oct 27 11:07 .coveragerc
-rw-r--r--@  1 bertrandrenaudin  staff   6.0K Nov  4 16:09 .DS_Store
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Oct 14 21:46 .pytest_cache
drwxr-xr-x@ 10 bertrandrenaudin  staff   320B Nov  3 21:38 apps
drwxr-xr-x@ 10 bertrandrenaudin  staff   320B Nov  3 21:40 config
-rw-r--r--@  1 bertrandrenaudin  staff   173K Oct 27 09:48 coverage.xml
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 27 11:07 doc
-rw-r--r--@  1 bertrandrenaudin  staff   682B Oct 12 18:14 Dockerfile
drwxr-xr-x@ 85 bertrandrenaudin  staff   2.7K Oct 27 09:48 htmlcov
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 23 15:14 logs
-rw-r--r--@  1 bertrandrenaudin  staff   662B Oct 12 18:14 manage.py
-rw-r--r--@  1 bertrandrenaudin  staff   231B Oct 12 21:17 pyproject.toml
-rw-r--r--@  1 bertrandrenaudin  staff   306B Oct 27 11:07 pytest.ini
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 27 11:07 requirements
-rw-r--r--@  1 bertrandrenaudin  staff   567B Oct 12 21:17 setup.cfg
-rw-r--r--@  1 bertrandrenaudin  staff    12K Oct 12 18:14 swagger.yaml
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 18 11:06 templates
drwxr-xr-x@  9 bertrandrenaudin  staff   288B Nov  4 16:09 tools
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Oct 15 22:11 venv
```

- Architecture de `apps` :

```bash
-rw-r--r--@ 1 bertrandrenaudin  staff   169B Oct 12 18:48 apps/__pycache__/__init__.cpython-313.pyc
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Nov  3 21:40 apps/branding/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff   626B Nov  3 21:40 apps/branding/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   408B Nov  3 21:40 apps/branding/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff   4.0K Nov  3 21:40 apps/branding/models.py
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Oct 12 18:14 apps/catalog/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff   1.1K Oct 12 18:14 apps/catalog/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   151B Oct 12 18:14 apps/catalog/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff   3.6K Oct 27 11:07 apps/catalog/models.py
-rw-r--r--@ 1 bertrandrenaudin  staff    63B Oct 12 18:14 apps/catalog/views.py
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Oct 12 18:14 apps/client/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff   299B Oct 12 18:14 apps/client/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   170B Oct 12 18:14 apps/client/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff   1.2K Oct 12 18:14 apps/client/models.py
-rw-r--r--@ 1 bertrandrenaudin  staff    63B Oct 12 18:14 apps/client/views.py
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Oct 12 18:14 apps/core/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff    63B Oct 12 18:14 apps/core/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   145B Oct 12 18:14 apps/core/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff   553B Oct 12 18:14 apps/core/enums.py
-rw-r--r--@ 1 bertrandrenaudin  staff   1.9K Oct 12 18:14 apps/core/exceptions.py
-rw-r--r--@ 1 bertrandrenaudin  staff   1.1K Oct 12 18:14 apps/core/logging.py
-rw-r--r--@ 1 bertrandrenaudin  staff   1.1K Oct 12 18:14 apps/core/managers.py
-rw-r--r--@ 1 bertrandrenaudin  staff    22B Nov  4 22:53 apps/core/models.py
-rw-r--r--@ 1 bertrandrenaudin  staff   368B Oct 12 18:14 apps/core/permissions.py
-rw-r--r--@ 1 bertrandrenaudin  staff    63B Oct 12 18:14 apps/core/views.py
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Oct 12 18:14 apps/quote/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff   839B Oct 12 18:14 apps/quote/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   241B Oct 12 18:14 apps/quote/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff    14K Nov  4 22:55 apps/quote/models.py
-rw-r--r--@ 1 bertrandrenaudin  staff   661B Oct 12 18:14 apps/quote/signals.py
-rw-r--r--@ 1 bertrandrenaudin  staff    63B Oct 12 18:14 apps/quote/views.py
-rw-r--r--@ 1 bertrandrenaudin  staff     0B Oct 12 18:14 apps/user/__init__.py
-rw-r--r--@ 1 bertrandrenaudin  staff   2.0K Oct 12 18:14 apps/user/admin.py
-rw-r--r--@ 1 bertrandrenaudin  staff   257B Oct 12 18:14 apps/user/apps.py
-rw-r--r--@ 1 bertrandrenaudin  staff   619B Oct 12 18:14 apps/user/signals.py
-rw-r--r--@ 1 bertrandrenaudin  staff   703B Oct 27 11:07 apps/user/urls.py

apps/branding/adapters:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 __pycache__
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 persistence
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 storage

apps/branding/application:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:40 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 dto
-rw-r--r--@  1 bertrandrenaudin  staff   601B Nov  3 21:40 errors.py
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 ports
drwxr-xr-x@ 12 bertrandrenaudin  staff   384B Nov  3 21:40 usecases

apps/branding/domain:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:40 entities
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 policies
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 services
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:40 value_objects

apps/branding/interface:
total 64
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:40 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.0K Nov  3 21:40 permissions.py
-rw-r--r--@  1 bertrandrenaudin  staff   5.1K Nov  3 21:40 serializers.py
-rw-r--r--@  1 bertrandrenaudin  staff   825B Nov  3 21:40 urls.py
-rw-r--r--@  1 bertrandrenaudin  staff    13K Nov  3 21:40 views.py

apps/branding/migrations:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:40 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
-rw-r--r--@  1 bertrandrenaudin  staff   3.2K Nov  3 21:40 0001_initial.py

apps/branding/tests:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:40 .
drwxr-xr-x@ 13 bertrandrenaudin  staff   416B Nov  3 21:40 ..
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 adapters
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 application
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 domain
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 interface

apps/catalog/adapters:
total 0
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 23 15:11 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 persistence

apps/catalog/application:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 dto
-rw-r--r--@  1 bertrandrenaudin  staff   1.1K Oct 27 11:07 errors.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 ports
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 usecases

apps/catalog/domain:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.9K Oct 27 11:07 errors.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 policies
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 services

apps/catalog/interface:
total 48
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Oct 29 16:22 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   3.7K Oct 27 11:07 error_handler.py
-rw-r--r--@  1 bertrandrenaudin  staff   500B Oct 12 18:14 filters.py
-rw-r--r--@  1 bertrandrenaudin  staff   3.5K Oct 27 11:07 serializers.py
-rw-r--r--@  1 bertrandrenaudin  staff   441B Oct 12 18:14 urls.py
-rw-r--r--@  1 bertrandrenaudin  staff   6.8K Oct 27 11:07 views.py

apps/catalog/migrations:
total 16
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Oct 12 18:48 __pycache__
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Oct 12 18:48 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   3.6K Oct 12 18:14 0001_initial.py
-rw-r--r--@  1 bertrandrenaudin  staff   2.1K Oct 12 18:14 0002_remove_prestation_unique_area_prestation_name_and_more.py

apps/catalog/tests:
total 24
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Oct 23 15:14 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 domain
-rw-r--r--@  1 bertrandrenaudin  staff   5.0K Oct 12 18:14 test_api_catalog.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.1K Oct 12 18:14 test_models.py

apps/client/adapters:
total 0
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 23 16:00 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 persistence

apps/client/application:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 dto
-rw-r--r--@  1 bertrandrenaudin  staff   335B Oct 27 11:07 errors.py
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 ports
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:38 usecases

apps/client/domain:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.0K Oct 27 11:07 errors.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 policies

apps/client/interface:
total 40
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Oct 29 16:22 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   5.8K Oct 27 11:07 serializers.py
-rw-r--r--@  1 bertrandrenaudin  staff   259B Oct 12 18:14 urls.py
-rw-r--r--@  1 bertrandrenaudin  staff   5.5K Oct 27 11:07 views.py

apps/client/migrations:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 12 18:48 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Oct 12 18:48 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.7K Oct 12 18:14 0001_initial.py

apps/client/tests:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 23 16:14 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:38 .
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Nov  3 21:38 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 adapters
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 application
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 domain
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 27 11:07 test_api_client_endpoint.py


apps/core/middleware:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 12 18:48 __pycache__
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 .
drwxr-xr-x@ 18 bertrandrenaudin  staff   576B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.5K Oct 12 18:14 request_logging.py

apps/core/migrations:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  4 22:55 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  4 22:55 .
drwxr-xr-x@ 18 bertrandrenaudin  staff   576B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.2K Nov  4 22:55 0001_initial.py

apps/core/models:
total 16
-rw-r--r--@  1 bertrandrenaudin  staff   143B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  4 22:55 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 .
drwxr-xr-x@ 18 bertrandrenaudin  staff   576B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   3.0K Nov  4 22:53 mixins.py

apps/core/tests:
total 24
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Oct 27 09:48 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 18 bertrandrenaudin  staff   576B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   687B Oct 12 18:14 test_enums.py
-rw-r--r--@  1 bertrandrenaudin  staff   2.9K Oct 12 18:14 test_mixins.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.2K Oct 12 18:14 test_money.py

apps/core/utils:
total 16
-rw-r--r--@  1 bertrandrenaudin  staff   257B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 12 18:48 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 .
drwxr-xr-x@ 18 bertrandrenaudin  staff   576B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   2.1K Oct 12 18:14 money.py

apps/quote/adapters:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Nov  3 21:40 __pycache__
drwxr-xr-x@  9 bertrandrenaudin  staff   288B Nov  3 22:04 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 email
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 pdf
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 persistence
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  4 22:51 reference
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 rendering

apps/quote/application:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:40 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  3 21:40 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 dto
-rw-r--r--@  1 bertrandrenaudin  staff   424B Oct 27 11:07 errors.py
drwxr-xr-x@ 12 bertrandrenaudin  staff   384B Nov  3 21:38 ports
drwxr-xr-x@ 10 bertrandrenaudin  staff   320B Nov  3 21:40 usecases

apps/quote/domain:
total 0
-rw-r--r--@  1 bertrandrenaudin  staff     0B Nov  3 21:40 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:40 __pycache__
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:40 policies
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:40 services

apps/quote/interface:
total 136
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  4 22:51 __pycache__
drwxr-xr-x@  9 bertrandrenaudin  staff   288B Nov  3 21:40 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.7K Oct 12 18:14 permissions.py
-rw-r--r--@  1 bertrandrenaudin  staff   825B Oct 19 18:01 renderers.py
-rw-r--r--@  1 bertrandrenaudin  staff    24K Nov  4 22:50 serializers.py
-rw-r--r--@  1 bertrandrenaudin  staff   536B Oct 27 11:07 urls.py
-rw-r--r--@  1 bertrandrenaudin  staff    24K Nov  3 21:40 views.py

apps/quote/migrations:
total 56
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  4 22:55 __pycache__
drwxr-xr-x@  8 bertrandrenaudin  staff   256B Nov  4 22:55 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff    12K Oct 12 18:14 0001_initial.py
-rw-r--r--@  1 bertrandrenaudin  staff   4.4K Oct 12 18:14 0002_alter_quotelineitem_options_and_more.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.1K Oct 12 18:14 0003_alter_paymentterms_owner_and_more.py
-rw-r--r--@  1 bertrandrenaudin  staff   473B Nov  4 22:55 0004_alter_quote_reference.py

apps/quote/tests:
total 72
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@ 14 bertrandrenaudin  staff   448B Oct 27 09:48 __pycache__
drwxr-xr-x@ 16 bertrandrenaudin  staff   512B Nov  3 21:38 .
drwxr-xr-x@ 15 bertrandrenaudin  staff   480B Nov  3 21:38 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 adapters
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 application
-rw-r--r--@  1 bertrandrenaudin  staff   1.1K Oct 27 11:07 conftest.py
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 domain
-rw-r--r--@  1 bertrandrenaudin  staff   1.3K Oct 27 11:07 test_add_prestation_line_api.py
-rw-r--r--@  1 bertrandrenaudin  staff   527B Oct 27 11:07 test_mock_verification.py
-rw-r--r--@  1 bertrandrenaudin  staff   3.0K Oct 27 11:07 test_models.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.5K Oct 27 11:07 test_pdf_download_api.py
-rw-r--r--@  1 bertrandrenaudin  staff   2.9K Oct 12 18:14 test_permissions.py
-rw-r--r--@  1 bertrandrenaudin  staff   823B Oct 27 11:07 test_preview.py
-rw-r--r--@  1 bertrandrenaudin  staff   3.4K Oct 27 11:07 test_quote_actions_api.py
-rw-r--r--@  1 bertrandrenaudin  staff   3.6K Oct 12 18:14 test_serializers.py

apps/user/adapters:
total 0
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 24 15:31 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 persistence

apps/user/application:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 dto
-rw-r--r--@  1 bertrandrenaudin  staff   2.8K Oct 27 11:07 errors.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 ports
drwxr-xr-x@  9 bertrandrenaudin  staff   288B Nov  3 21:38 usecases

apps/user/backend:
total 0
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 14 21:45 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 14 21:45 apps

apps/user/domain:
total 8
drwxr-xr-x@  3 bertrandrenaudin  staff    96B Oct 29 16:22 __pycache__
drwxr-xr-x@  6 bertrandrenaudin  staff   192B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   2.9K Oct 27 11:07 errors.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 policies
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Nov  3 21:38 services

apps/user/interface:
total 88
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  7 bertrandrenaudin  staff   224B Oct 29 16:22 __pycache__
drwxr-xr-x@  9 bertrandrenaudin  staff   288B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   6.3K Oct 24 16:19 auth_views.py
-rw-r--r--@  1 bertrandrenaudin  staff   4.0K Oct 27 11:07 errors_handler.py
-rw-r--r--@  1 bertrandrenaudin  staff   9.6K Oct 27 11:07 serializers.py
-rw-r--r--@  1 bertrandrenaudin  staff   212B Oct 12 18:14 urls.py
-rw-r--r--@  1 bertrandrenaudin  staff    14K Oct 27 11:07 views.py

apps/user/migrations:
total 72
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@ 11 bertrandrenaudin  staff   352B Oct 12 18:48 __pycache__
drwxr-xr-x@ 12 bertrandrenaudin  staff   384B Oct 12 18:48 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   4.9K Oct 12 18:14 0001_initial.py
-rw-r--r--@  1 bertrandrenaudin  staff   546B Oct 12 18:14 0002_remove_user_username_alter_user_email.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.7K Oct 12 18:14 0003_alter_user_managers_profile.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.1K Oct 12 18:14 0004_migrate_profile_data.py
-rw-r--r--@  1 bertrandrenaudin  staff   626B Oct 12 18:14 0005_alter_user_options_user_uniq_user_email_ci.py
-rw-r--r--@  1 bertrandrenaudin  staff   2.7K Oct 12 18:14 0006_professionaluser.py
-rw-r--r--@  1 bertrandrenaudin  staff   679B Oct 12 18:14 0007_professionaluser_allowed_areas.py
-rw-r--r--@  1 bertrandrenaudin  staff   354B Oct 12 18:14 0008_remove_professionaluser_allowed_areas.py

apps/user/models:
total 24
-rw-r--r--@  1 bertrandrenaudin  staff    34B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 12 18:48 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   4.9K Oct 12 18:14 models.py

apps/user/services:
total 8
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@  4 bertrandrenaudin  staff   128B Oct 12 18:48 __pycache__
drwxr-xr-x@  5 bertrandrenaudin  staff   160B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   637B Oct 12 18:14 email_change.py

apps/user/tests:
total 64
-rw-r--r--@  1 bertrandrenaudin  staff     0B Oct 12 18:14 __init__.py
drwxr-xr-x@ 10 bertrandrenaudin  staff   320B Oct 27 09:43 __pycache__
drwxr-xr-x@ 10 bertrandrenaudin  staff   320B Nov  3 21:38 .
drwxr-xr-x@ 17 bertrandrenaudin  staff   544B Nov  3 21:38 ..
-rw-r--r--@  1 bertrandrenaudin  staff   1.4K Oct 12 18:14 test_auth_api.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.4K Oct 12 18:14 test_auth_logout.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.3K Oct 27 11:07 test_professional_api.py
-rw-r--r--@  1 bertrandrenaudin  staff   1.2K Oct 27 11:07 test_professional_serializer_minimal.py
-rw-r--r--@  1 bertrandrenaudin  staff   4.1K Oct 12 18:14 test_refresh_rotation.py
-rw-r--r--@  1 bertrandrenaudin  staff   6.6K Oct 27 11:07 test_user_api.py
```
