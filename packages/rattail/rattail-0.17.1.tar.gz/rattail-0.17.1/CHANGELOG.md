
# Changelog
All notable changes to rattail will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.17.1 (2024-07-15)

### Fix

- avoid deprecated `self.model` within the auth handler

## v0.17.0 (2024-07-14)

### Feat

- move most of auth handler logic to wuttjamaican

### Fix

- rename some constraints per wutta model

## v0.16.1 (2024-07-12)

### Fix

- remove duplicate method for `AppHandler.load_object()`
- remove duplicate method for `RattailConfig.production()`

## v0.16.0 (2024-07-11)

### Feat

- move some app model logic to wuttjamaican

## v0.15.0 (2024-07-09)

### Feat

- drop python 3.6 support, use pyproject.toml (again)

## v0.14.8 (2024-07-05)

### Fix

- fix model reference in reporting handler

## v0.14.7 (2024-07-04)

### Fix

- add `get_cmd()` method for import handlers

- specify default list for rattail mail templates

- add `get_role()` method for auth handler

## v0.14.6 (2024-07-04)

### Fix

- refactor code so most things work without sqlalchemy

- avoid command line errors if sqlalchemy not installed

- bump version for wuttjamaican

## v0.14.5 (2024-07-04)

### Fix

- change how we override default app handler, engine maker

## v0.14.4 (2024-07-02)

### Fix

- avoid `pkg_resources` for `files.resource_path()`

## v0.14.3 (2024-07-02)

### Fix

- include importing subcommands for discovery

## v0.14.2 (2024-07-02)

### Fix

- delay imports from `wuttjamaican.db`

## v0.14.1 (2024-07-01)

### Fix

- remove references, dependency for `six` package

- remove some unused imports

- remove duplicated / unused code for `rattail.db.config`

- deprecate `parse_bool()` and `parse_list()` in `rattail.config`

## v0.14.0 (2024-07-01)

### Feat

- remove legacy command system

### Fix

- make pyproject.toml instead of setup.cfg for generated project

## v0.13.5 (2024-06-28)

### Fix

- read logs from journald by default, for postfix-summary

- allow config override of "problems" for postfix-summary

## v0.13.4 (2024-06-27)

### Fix

- fix missing module import

## v0.13.3 (2024-06-24)

### Fix

- merge associated shopper records when merging 2 people

- truncate invoice item description for receiving, if needed

## v0.13.2 (2024-06-14)

### Fix

- revert back to setup.py + setup.cfg

## v0.13.1 (2024-06-10)

### Fix

- move canonical app version to pyproject.toml

## v0.13.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml / hatchling

## v0.12.9 (2024-06-10)

### Feat

- add config snippet for new projects, to define static libcache
- define the `app_package` setting for new projects
- add `get_pkg_version()` convenience function

## v0.12.8 (2024-06-06)

### Feat

- project generator should make typer commands, not old-style
- remove old/unused project scaffold template
- add snippet for fanstatic/libcache when generating web project

### Fix

- fix missing import for `rattail make-config` command
- define the `-n` command flag as alias for `--no-init`

## v0.12.7 (2024-06-02)

### Fix

- fix datasync command args, per typer

## v0.12.6 (2024-06-01)

### Feat

- add setting to allow decimal quantities for ordering/receiving

### Fix

- fix `rattail datasync remove-settings` command line, per typer
- fix `--progress-socket` arg handling for typer commands

## v0.12.5 (2024-05-31)

### Fix

- fix args for `rattail populate-batch` command, per typer

## v0.12.4 (2024-05-31)

### Fix

- fix params for generic "run purge" command logic, per typer

## v0.12.3 (2024-05-31)

### Fix

- fix args for `rattail purge-batches` command, per typer

## v0.12.2 (2024-05-30)

### Feat

- log the `pflogsumm` command before running it

### Fix

- fix some commands/arguments, per typer

## v0.12.1 (2024-05-29)

### Feat

- include organic flag when normalizing product

## v0.12.0 (2024-05-29)

This release begins the migration to use `typer` for all commands,
instead of the "traditional" (now WuttJamaican-based) commands.

### Feat

- add `get_runas_user()` method for AppHandler
- move rich and prompt_toolkit things to separate module
- move `finalize_session()` function to `db.util` module
- move "install" command logic to separate handler/module
- move "import command runner" logic to separate handler
- add basic support for `typer` command system
- migrate all commands to use typer
- add command logic functions for running reports, purging things

### Fix

- fix subcommand runas user when caller provides username


## Older Releases

Please see `docs/OLDCHANGES.rst` for older release notes.
