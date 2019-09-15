# 💨💨💨 Pyuubin – Mailing System 💨💨💨

[![Build Status](https://travis-ci.org/MichalMazurek/pyuubin.svg?branch=master)](https://travis-ci.org/MichalMazurek/pyuubin)

Asynchronous mailing system over HTTP API.

郵便 (Yūbin) - Postal Service

ぴゅー (Pyu-) – SFX for a sudden burst of speed, like running away from something

## Installation

```bash
pip install pyuubin
```

## Installation from source

```bash
pip install .
```

## Running the service

You need to run the API and Worker for the system to work.

### The API

Use hypercorn or uvicorn to run it

```bash
hypercorn pyuubin.api.app:app --access-log - --error-log -
```

### The Worker

```bash
$ python -m pyuubin.worker --help
Usage: worker.py [OPTIONS]

  Run the worker.

Options:
  -n, --name TEXT                 Name of the service
  -w, --workers INTEGER           Number of workers
  -d, --debug                     Enable debug mode.
  -e, --print-environment-variables
                                  print environment variables to be put in
                                  .env file for configuration
  --help                          Show this message and exit.
```

## Configuration

You can configure Pyuubin by using environmental variables. List of variables is available on running

```bash
$ python -m pyuubin -e
PYUUBIN_REDIS_PREFIX=pyuubin:
PYUUBIN_REDIS_MAIL_QUEUE=pyuubin::mail_queue
PYUUBIN_REDIS_URL=redis://localhost:6379
PYUUBIN_SMTP_HOST=smtp.gmail.com
PYUUBIN_SMTP_PORT=465
PYUUBIN_SMTP_USER=email@gmail.com
PYUUBIN_SMTP_PASSWORD=SecretStr('**********')
PYUUBIN_SMTP_TLS=True
PYUUBIN_MAIL_FROM=email@gmail.com
PYUUBIN_MAIL_RETURN=returns@exampple.tld
PYUUBIN_MAIL_CONNECTOR=pyuubin.connectors.smtp
PYUUBIN_AUTH_HTPASSWD_FILE=
```

> Note that the password is a `SecretStr` type from pydantic, so in your `.env.` file please just write your password without `SecretStr()`, so actually what you want is: `PYUUBIN_SMTP_PASSWORD=secret`

Pyuubin supports `.env` files. You can create one quite easily by running above command and directing the output to a `.env` file.

```bash
$ python -m pyuubin -e > .env
$
```

Then edit this file, put the values required and run the app.

## Authentication - Password File

Generating passwords with htpasswd:

```bash
htpasswd -Bc test_htpasswd app1
```

> Note: Only blowfish encrypted hashes are supported

## API Specification

You can find API docs here: [redoc pages](https://pyuubin.io/docs/index.html)

## TODO

- Documentation
- Client library
- Handling of rejected/failed mails
- Bounces management
- Rate limitting for source / global
