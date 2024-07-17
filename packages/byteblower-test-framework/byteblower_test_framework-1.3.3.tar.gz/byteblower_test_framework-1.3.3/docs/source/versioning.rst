==========
Versioning
==========

Versioning schema
=================

The ByteBlower Test Framework follows the versioning schema:

   ``<major>.<minor>.<patch>["-alpha|beta|rc|post"["."{0-9}*]]``

* ``<patch>`` increases for bugfix-only releases.
* ``<minor>`` increases for new features.
* ``<major>`` increases for new features with big incompatible changes
  in the API or configuration parameters.

Deprecations handling
=====================

Some releases of the ByteBlower Test Framework include deprecations.
This in general means that the API or scenario definition in the release
have items (API interfaces or configuration parameters) which will be
removed in one of the upcoming releases.

The deprecated items describe how to migrate to the new situation in
their documentation.

Backward-compatibility with the old API interfaces or configuration
parameters is maintained for a minimum amount of time. This gives our
users the time to either pin to a specific (*maximum*) version of the
ByteBlower Test Framework or to migrate to the new situation.

Deprecated API interfaces and configuration parameters will be removed
no earlier than 6 months after the date of the release where the
deprecation was announced.

Deprecations in *beta* releases for items introduced in the same *feature*
release will be removed in the next official release.

For example following sequence:

#. Release v1.2.3
#. Release *beta* v1.2.4b1: Including new API call ``hello()``
#. ...
#. Release *beta* v1.2.4b7: Deprecating API call ``hello()``
#. Release v1.2.4: Removes API call ``hello()``
