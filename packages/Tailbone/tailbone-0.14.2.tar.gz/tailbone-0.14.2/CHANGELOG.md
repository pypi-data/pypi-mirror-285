
# Changelog
All notable changes to Tailbone will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.14.2 (2024-07-15)

### Fix

- add null menu handler, for use with API apps

## v0.14.1 (2024-07-14)

### Fix

- update usage of auth handler, per rattail changes
- fix model reference in menu handler
- fix bug when making "integration" menus

## v0.14.0 (2024-07-14)

### Feat

- move core menu logic to wuttaweb

## v0.13.2 (2024-07-13)

### Fix

- fix logic bug for datasync/config settings save

## v0.13.1 (2024-07-13)

### Fix

- fix settings persistence bug(s) for datasync/configure page

## v0.13.0 (2024-07-12)

### Feat

- begin integrating WuttaWeb as upstream dependency

### Fix

- cast enum as list to satisfy deform widget

## v0.12.1 (2024-07-11)

### Fix

- refactor `config.get_model()` => `app.model`

## v0.12.0 (2024-07-09)

### Feat

- drop python 3.6 support, use pyproject.toml (again)

## v0.11.10 (2024-07-05)

### Fix

- make the Members tab optional, for profile view

## v0.11.9 (2024-07-05)

### Fix

- do not show flash message when changing app theme

- improve collapse panels for butterball theme

- expand input for butterball theme

- add xref button to customer profile, for trainwreck txn view

- add optional Transactions tab for profile view

## v0.11.8 (2024-07-04)

### Fix

- fix grid action icons for datasync/configure, per oruga

- allow view supplements to add extra links for profile employee tab

- leverage import handler method to determine command/subcommand

- add tool to make user account from profile view

## v0.11.7 (2024-07-04)

### Fix

- add stacklevel to deprecation warnings

- require zope.sqlalchemy >= 1.5

- include edit profile email/phone dialogs only if user has perms

- allow view supplements to add to profile member context

- cast enum as list to satisfy deform widget

- expand POD image URL setting input

## v0.11.6 (2024-07-01)

### Fix

- set explicit referrer when changing dbkey

- remove references, dependency for `six` package

## v0.11.5 (2024-06-30)

### Fix

- allow comma in numeric filter input

- add custom url prefix if needed, for fanstatic

- use vue 3.4.31 and oruga 0.8.12 by default

## v0.11.4 (2024-06-30)

### Fix

- start/stop being root should submit POST instead of GET

- require vendor when making new ordering batch via api

- don't escape each address for email attempts grid

## v0.11.3 (2024-06-28)

### Fix

- add link to "resolved by" user for pending products

- handle error when merging 2 records fails

## v0.11.2 (2024-06-18)

### Fix

- hide certain custorder settings if not applicable

- use different logic for buefy/oruga for product lookup keydown

- product records should be touchable

- show flash error message if resolve pending product fails

## v0.11.1 (2024-06-14)

### Fix

- revert back to setup.py + setup.cfg

## v0.11.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml + hatchling

## v0.10.16 (2024-06-10)

### Feat

- standardize how app, package versions are determined

### Fix

- avoid deprecated config methods for app/node title

## v0.10.15 (2024-06-07)

### Fix

- do *not* Use `pkg_resources` to determine package versions

## v0.10.14 (2024-06-06)

### Fix

- use `pkg_resources` to determine package versions

## v0.10.13 (2024-06-06)

### Feat

- remove old/unused scaffold for use with `pcreate`

- add 'fanstatic' support for sake of libcache assets

## v0.10.12 (2024-06-04)

### Feat

- require pyramid 2.x; remove 1.x-style auth policies

- remove version cap for deform

- set explicit referrer when changing app theme

- add `<b-tooltip>` component shim

- include extra styles from `base_meta` template for butterball

- include butterball theme by default for new apps

### Fix

- fix product lookup component, per butterball

## v0.10.11 (2024-06-03)

### Feat

- fix vue3 refresh bugs for various views

- fix grid bug for tempmon appliance view, per oruga

- fix ordering worksheet generator, per butterball

- fix inventory worksheet generator, per butterball

## v0.10.10 (2024-06-03)

### Feat

- more butterball fixes for "view profile" template

### Fix

- fix focus for `<b-select>` shim component

## v0.10.9 (2024-06-03)

### Feat

- let master view control context menu items for page

- fix the "new custorder" page for butterball

### Fix

- fix panel style for PO vs. Invoice breakdown in receiving batch

## v0.10.8 (2024-06-02)

### Feat

- add styling for checked grid rows, per oruga/butterball

- fix product view template for oruga/butterball

- allow per-user custom styles for butterball

- use oruga 0.8.9 by default

## v0.10.7 (2024-06-01)

### Feat

- add setting to allow decimal quantities for receiving

- log error if registry has no rattail config

- add column filters for import/export main grid

- escape all unsafe html for grid data

- add speedbumps for delete, set preferred email/phone in profile view

- fix file upload widget for oruga

### Fix

- fix overflow when instance header title is too long (butterball)

## v0.10.6 (2024-05-29)

### Feat

- add way to flag organic products within lookup dialog

- expose db picker for butterball theme

- expose quickie lookup for butterball theme

- fix basic problems with people profile view, per butterball

## v0.10.5 (2024-05-29)

### Feat

- add `<tailbone-timepicker>` component for oruga

## v0.10.4 (2024-05-12)

### Fix

- fix styles for grid actions, per butterball

## v0.10.3 (2024-05-10)

### Fix

- fix bug with grid date filters

## v0.10.2 (2024-05-08)

### Feat

- remove version restriction for pyramid_beaker dependency

- rename some attrs etc. for buefy components used with oruga

- fix "tools" helper for receiving batch view, per oruga

- more data type fixes for ``<tailbone-datepicker>``

- fix "view receiving row" page, per oruga

- tweak styles for grid action links, per butterball

### Fix

- fix employees grid when viewing department (per oruga)

- fix login "enter" key behavior, per oruga

- fix button text for autocomplete

## v0.10.1 (2024-04-28)

### Feat

- sort list of available themes

- update various icon names for oruga compatibility

- show "View This" button when cloning a record

- stop including 'falafel' as available theme

### Fix

- fix vertical alignment in main menu bar, for butterball

- fix upgrade execution logic/UI per oruga

## v0.10.0 (2024-04-28)

This version bump is to reflect adding support for Vue 3 + Oruga via
the 'butterball' theme.  There is likely more work to be done for that
yet, but it mostly works at this point.

### Feat

- misc. template and view logic tweaks (applicable to all themes) for
  better patterns, consistency etc.

- add initial support for Vue 3 + Oruga, via "butterball" theme


## Older Releases

Please see `docs/OLDCHANGES.rst` for older release notes.
