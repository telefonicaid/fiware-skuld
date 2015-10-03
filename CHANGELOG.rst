Changelog
=========

v1.0.0 (2015-10-01)
-------------------

New
~~~

- Code reorganisation: scripts are adapted to be invoked as an only daily task via cron:
** Every day users close to expiration are notified (but only once).
** Every day expired accounts are changed to basic and the users' VMs are stopped.
** Every day resources of users expired some days ago are definitively cleaned.
- Full documentation at README.
- Lots of bugfixes and improvements in logging.
- Add utility to extract information from report files.
