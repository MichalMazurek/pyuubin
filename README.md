# Yuubin

Asynchronous mailing system.
郵便 (Yūbin) - Postal Service

## Installation

```bash
pip install yuubin
```

## Installation from source

```bash
pip install .
```

## Authentication - Password File

Generating passwords with htpasswd:

```bash
htpasswd -Bc test_htpasswd app1
```

> Note: Only blowfish encrypted hashes are supported

## M2Crypto on MacOSX

The installation might fail for m2crypto. You need to install `openssl` and `swig`.

```bash
brew install openssl
brew install swig
```

And then you can install `m2crypto`

```bash
env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" SWIG_FEATURES="-cpperraswarn -includeall -I$(brew --prefix openssl)/include" pip install m2crypto
```

## TODO

- Documentation
- Handling of rejected/failed mails
- Bounces management
- Rate limitting for source / global
