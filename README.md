# Multi-purpose Django site

A small Django base meant to grow one app at a time.

## Layout

```
site/
├── manage.py
├── docker-compose.yml       # optional PostgreSQL, for when you switch off SQLite locally
├── config/                  # project package (no business logic)
│   ├── settings/
│   │   ├── base.py          # shared settings; loads .env; SQLite/PostgreSQL switch; logging
│   │   ├── dev.py           # DEBUG, console email, default for manage.py
│   │   ├── test.py          # fast hasher, locmem email, quiet logging
│   │   └── prod.py          # security flags, WhiteNoise, required DB variables; default for wsgi/asgi
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                    # every feature lives here as "apps.<name>"
│   ├── core/                # shared pieces: TimeStampedModel, home page
│   └── accounts/            # custom User (email login) and Profile
├── templates/               # project-wide templates (base.html, 403/404/500 error pages)
├── static/                  # project-wide static files
├── locale/                  # translations (en, sv ready)
├── pyproject.toml           # dependencies, managed with uv
├── uv.lock                  # exact locked versions (commit this)
└── .env.example
```

Each app keeps its own templates under `apps/<name>/templates/<name>/` and its
own tests in `apps/<name>/tests.py` (switch to a `tests/` package when it grows).

## Decisions

- **Single organisation.** No tenant/organisation model; permissions use Django groups.
- **Server-rendered Django templates for v1.** No API layer yet; keep business logic in
  models, forms and small service functions rather than in templates, so an API
  (e.g. Django REST Framework) can be added later without a rewrite.
- **Custom user model with email login** from day one. The user model is a project-wide
  foundation choice (it cannot be changed after the first migration); everything else in
  `accounts` (profile, avatar) is ordinary feature code.
- **SQLite for local development in version 1, PostgreSQL in production.** Locally and in
  tests Django uses a SQLite file (nothing to install or run). Setting `DB_ENGINE=postgres`
  switches any local run to PostgreSQL (see "Moving to PostgreSQL" below); production always
  uses PostgreSQL and refuses to start without its database variables. Keep the code
  database-neutral (no raw SQL, no PostgreSQL-only fields) until the switch is made.
- **No signup page.** Users are added by an administrator in the Django admin. An
  invitation or self-signup flow can be added later if it is ever needed.
- **Password reset deferred.** The reset URLs are routed but nothing links to them, and they
  render Django's admin-styled pages. Email setup is not done yet.
- **Manual app registration.** New apps are added to settings and URLs by hand; explicit is
  easier to debug than auto-discovery.

## Getting started

Needs [uv](https://docs.astral.sh/uv/). No `.env` file and no database server are needed.

```bash
uv sync                                   # creates .venv and installs from uv.lock
uv run python manage.py migrate           # creates db.sqlite3
uv run python manage.py createsuperuser   # asks for an email address and a password
uv run python manage.py runserver
```

The development database is the file `db.sqlite3` (ignored by git). Delete it and run
`migrate` again to start over. To change other settings, copy `.env.example` to `.env`.

### Moving to PostgreSQL

SQLite data does not move over by itself, so treat the SQLite database as disposable
development data. When you are ready to switch locally:

```bash
docker compose up -d --wait db            # start PostgreSQL in Docker
echo "DB_ENGINE=postgres" >> .env         # or export DB_ENGINE=postgres in the shell
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

The defaults (database, user and password all `site`, on `localhost:5432`) match
`docker-compose.yml`; override them with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` and
`DB_PORT`. `docker compose stop db` stops it (data stays in the `pgdata` volume);
`docker compose down -v` stops it **and deletes the data**. To carry real data across, use
`uv run python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e admin.logentry -e sessions > data.json` while on SQLite, then `loaddata data.json` after
migrating on PostgreSQL, and check the result. Do the switch before you have data you care about.

Run the tests on PostgreSQL before each release, because it is stricter than SQLite
(e.g. about types, case-sensitive text matching and locking):
`DB_ENGINE=postgres uv run python manage.py test --settings=config.settings.test`.

Add a package with `uv add <package>` (or `uv add --dev <package>` for dev-only tools).
This updates both `pyproject.toml` and `uv.lock`. Production-only packages live in the
`prod` extra (`uv add --optional prod <package>`).

## Testing

By default the tests run on an in-memory SQLite database, so they need nothing running and
your `db.sqlite3` is never touched. With `DB_ENGINE=postgres` (and the container running)
Django creates and removes a separate `test_<name>` database instead.

```bash
uv run python manage.py test --settings=config.settings.test            # whole suite
uv run python manage.py test apps.accounts --settings=config.settings.test --keepdb   # faster reruns
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run                # no forgotten migrations
```

Test output is kept quiet through the logging config, not `logging.disable()`, so
`self.assertLogs(...)` works normally in any app's tests.

## Adding an app

1. Create it: `mkdir apps/events && uv run python manage.py startapp events apps/events`
2. Set `name = "apps.events"` in `apps/events/apps.py`.
3. Add `"apps.events"` to `LOCAL_APPS` in `config/settings/base.py`.
4. Include its URLs in `config/urls.py`, above the `core` catch-all.
5. Create and apply migrations: `makemigrations events`, then `migrate`.
6. Add tests for its main behaviour.
7. Run the tests, `check` and `makemigrations --check --dry-run` (see Testing).

Use `settings.AUTH_USER_MODEL` for foreign keys to users, and
`apps.core.models.TimeStampedModel` for timestamps where they are useful. Each app owns its
own domain logic: put code in `core` only when it is genuinely shared and stable.

## Accounts

- `accounts.User` extends `AbstractUser` and logs in with **email** (no username).
  Emails are stored lowercase, unique case-insensitively (enforced by a database
  constraint, not just in `save()`), and matched case-insensitively at login.
  It is thin on purpose; extra personal data goes on `Profile`.
- `accounts.Profile` is one-to-one with the user and is created automatically by a
  `post_save` signal, so every user has one however it was created (admin, shell,
  `createsuperuser`). It holds display name, bio, phone number and avatar.
- URLs: `/accounts/login/`, `/accounts/logout/` (POST), `/accounts/profile/`,
  `/accounts/profile/edit/`, `/accounts/password_change/`.

### Adding a user

In the admin (`/admin/`): **Users → Add user**, enter the email address and a password, and
give the person those credentials. They can change their password themselves at
`/accounts/password_change/` once logged in. Until password reset exists, a user who has
forgotten their password needs an administrator to set a new one in the admin.

## Configuration and logging

Settings are read from environment variables. A `.env` file next to `manage.py` is loaded
automatically (copy `.env.example`); variables already set in the real environment win.

Logging goes to the console (stderr) so systemd/journald or Docker collects it. Set the
level with `DJANGO_LOG_LEVEL` (default `INFO`). In app code use
`logging.getLogger(__name__)`; loggers under `apps.*` are configured automatically.

## Deployment checklist

`config.settings.prod` always uses PostgreSQL (it ignores `DB_ENGINE`) and refuses to start
without `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` and all of `DB_NAME`, `DB_USER`,
`DB_PASSWORD` and `DB_HOST`, so a missing variable fails at startup rather than pointing
the site at the wrong, possibly empty, database. Run the test suite on PostgreSQL before
the first deploy.

1. **Install:** `uv sync --no-dev --extra prod` (adds gunicorn and WhiteNoise).
2. **Configure:** set the variables from `.env.example` in the real environment (or a `.env`
   with restricted permissions). Run PostgreSQL however you prefer (managed service, or
   `docker-compose.yml` with a strong password); it must be reachable from the app.
3. **Check:** `uv run python manage.py check --deploy --settings=config.settings.prod`
   and read every warning. Only the optional HSTS-preload warning is expected.
4. **Migrate:** `uv run python manage.py migrate --settings=config.settings.prod`
5. **Static files:** `uv run python manage.py collectstatic --noinput --settings=config.settings.prod`
   on every deploy; WhiteNoise serves `staticfiles/`.
6. **Media:** WhiteNoise does *not* serve uploads (avatars). Serve `media/` from your web
   server, or move to object storage later.
7. **HTTPS and proxy:** terminate HTTPS at a reverse proxy. `SECURE_PROXY_SSL_HEADER` makes
   Django trust the `X-Forwarded-Proto` header, so it is only safe when the proxy sets or
   overwrites that header and clients cannot reach gunicorn directly. If gunicorn is exposed
   directly, remove that setting. Keep `DJANGO_HSTS_SECONDS=0` until HTTPS works everywhere
   (including subdomains), then raise it in steps.
8. **Backups:** schedule `pg_dump` for the database and copy `media/`, and test a restore
   once. Nothing else in the deployment holds state.
9. **Run:** `uv run gunicorn config.wsgi` (wsgi/asgi default to the prod settings).

## Working with git

- `main` always works: the tests pass and `makemigrations --check` is clean. Do not commit
  half-finished work to it.
- One branch per app or larger change, named for what it does (`app/finance-tracker`,
  `fix/login-redirect`). Merge into `main` when it works.
- Before merging: run the tests, `uv run python manage.py check` and
  `uv run python manage.py makemigrations --check --dry-run` (see Testing).
- Commit migration files together with the model change that needs them. Never edit or
  delete a migration that has been merged; add a new one instead.
- Commit `pyproject.toml` and `uv.lock` together whenever a dependency changes.
- Never commit `.env`, `db.sqlite3` or `media/`; they are in `.gitignore`. Put new
  settings in `.env.example` (with a harmless placeholder), not in `.env`.
- Keep commit messages short and in the imperative: "Add match model and admin", with a few
  lines of explanation when the reason is not obvious.

## Later

- Ruff (linting and formatting) together with GitHub Actions running tests and checks on each
  pull request. This needs a git repository first.
- Password reset with email, and optionally an invitation or signup flow.
