3.0.0
-----

* Use poetry

* Added `regex_filter`. Filters files using a regex.

* Fixed issue when listing mutliple files in a directory.

* Gzip is supported for local and remote files.

2.4.1
----

* fix:  Add missing ALB auth error: AuthMissingAWSALBAuthNonce
    
* fix: LoadBalancerLogEntry not always provides targetGroup ARN
    
* fix: LoadBalancerLogEntry tests fix

Thanks @pkoltermann!

1.8.3
-----

* Use tox.

1.8.1
-----

* Add support for ELB Classic logs. Thank you @PavelVaks.

* Parse cookies into dicts. Thank you @sancastlem.

* Project now uses black.
