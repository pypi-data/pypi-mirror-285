
# Changelog
All notable changes to WuttJamaican will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.8.2 (2024-07-18)

### Fix

- add `check_user_password()` method for auth handler

## v0.8.1 (2024-07-17)

### Fix

- make `AuthHandler.get_user()` do lookups for uuid, username

## v0.8.0 (2024-07-14)

### Feat

- flesh out the auth handler; add people handler
- add model for Person; tie to User

### Fix

- add migration for auth tables

## v0.7.0 (2024-07-14)

### Feat

- add basic "auth" data models: user/role/perm

### Fix

- always use 'wutta' prefix for provider entry points

## v0.6.1 (2024-07-12)

### Fix

- add `AppHandler.load_object()` method
- add `WuttaConfig.production()` method

## v0.6.0 (2024-07-11)

### Feat

- add basic data model support

## v0.5.0 (2024-07-09)

### Feat

- drop python 3.6 support

## v0.4.0 (2024-07-04)

### Feat

- remove legacy command system

### Fix

- use more explicit import in config constructor

## v0.3.2 (2024-07-04)

### Fix

- let config class specify default app handler, engine maker
- ensure config has no app when constructor finishes

## v0.3.1 (2024-06-14)

### Fix

- fallback to `importlib_metadata` when loading entry points

## v0.3.0 (2024-06-10)

### Feat

- use hatchling for package build backend

## v0.2.1 (2024-06-10)

### Fix

- use `importlib-metadata` backport for older systems

## v0.2.0 (2024-06-10)

### Feat

- replace setup.cfg with pyproject.toml

## [0.1.12] - 2024-05-28
### Changed
- Fix bug when default config paths do not exist.

## [0.1.11] - 2024-04-14
### Changed
- Fix import for `logging.config`.
- Raise `AttributeError` if no app provider has it.

## [0.1.10] - 2024-04-14
### Changed
- `WuttaConfig.get_list()` now returns `None` (instead of `[]`) by
  default if there is no config value present.

## [0.1.9] - 2023-11-30
### Changed
- Add generic handler base class, tests, docs.
- Avoid deprecation warning for ConfigParser.

## [0.1.8] - 2023-11-24
### Changed
- Add app providers, tests, docs.

## [0.1.7] - 2023-11-24
### Changed
- Add config extension class, tests, docs.

## [0.1.6] - 2023-11-22
### Changed
- Move cli framework to `wuttjamaican.cmd` subpackage.
- Add `date-organize` subcommand.

## [0.1.5] - 2023-11-22
### Changed
- Add `wutta make-appdir` subcommand.
- Add `--stdout` and `--stderr` args for base Command class.

## [0.1.4] - 2023-11-21
### Changed
- Add `Subcommand.make_arg_parser()` method.
- Allow factory override in `make_config()`.

## [0.1.3] - 2023-11-21
### Changed
- Allow specifying config object for Command constructor.
- Change entry point group naming for subcommands.

## [0.1.2] - 2023-11-20
### Changed
- Add `get_config_paths()` function, split off from `make_config()`.

## [0.1.1] - 2023-11-19
### Changed
- Add `make_engine_from_config()` method for AppHandler.

## [0.1.0] - 2023-11-19
### Added
- Initial version, with basic config and command frameworks.
