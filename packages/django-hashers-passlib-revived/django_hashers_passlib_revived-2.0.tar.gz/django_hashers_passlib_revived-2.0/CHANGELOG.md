# ChangeLog

## 2.0 (WIP)

The original project [django-hashes-passlib](https://github.com/mathiasertl/django-hashers-passlib) has no longer been maintained by the original developer. It was forked and renamed to `django-hashers-passlib-revived`

- Added support for Django 4.1, 4.2 and 5.0.
- Added support for Python 3.11 and 3.12.
- Added Types for everything.
- Use Poetry for a local developme environment.
- Overall code cleanup and modernization.

## 1.0.0 (never released)

- Add support for Django 3.2 and Django 4.0.
- Add support for Python 3.7 - 3.10.
- Drop support for long out-of-date Django versions 1.8, 1.10 and 1.11.
- Drop support for deprecated versions of Python (2.7 - 3.6).
- Add `argon2d` and `argon2id` hashers. We recommend that you add all argon2 hashers if needed.
- Switch to GitHub Actions for CI testing.
- Modernize project setup (`pyproject.toml`, `setup.cfg`, etc).
- Add black and pylint to suite of linters/formatters.

## 0.4 (19 November 2017)

- Support passlib 1.7.
- Add argon2 and scrypt hashers.
- Make hash parameters configurable via the PASSLIB_KEYWORDS setting.
- Add `VERSION` and `get_version()` similar to Django.
- Integrate with Travis to run test-suite with Python 2.7, 3.4+ and all currently supported versions of
  Django.
- Update python version classifiers in setup.py.
- Also upload wheels.

## 0.3 (05 December 2015)

- Require `Python3>=3.4`.
- Depend on `Django>=1.8`.
- Update passlib and bcrypt dependencies.

## 0.2 (22 March 2014)

- Remove distribute_setup.py.
- Implement a generic `safe_summary()` method for all hashers.
- Add bcrypt to requirements.txt.
- Version reported to setup.py is now the same as `git describe` if executed
  from a git repository.
- Add a `version` setup.py command.
- Fix `ldap_md5` and `ldap_sha1` converters in Python 3.

## 0.1 (01 January 2014)

- Initial release.
