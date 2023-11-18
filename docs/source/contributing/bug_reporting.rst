.. title:: Bug reporting

.. _bug_reporting:

Bug reporting
=============

Report bugs or not working features from your school here:

* List of existing issues: https://github.com/kurwjan/LanisAPI/issues
* Create a new issue: https://github.com/kurwjan/LanisAPI/issues/new

**When you report a bug please provide the log and exception text**::

    INFO - LanisClient   USING VERSION 0.3.0
    WARNING - LanisClient   LANISAPI IS STILL IN A EARLY STAGE SO EXPECT BUGS.
    WARNING - LanisClient   IMPORTANT: Schulportal Hessen can change things quickly and is fragmented (some schools work, some not), so expect something to not be working
    INFO - LanisClient   Authenticate: Using cookies to authenticate, skip authentication.
    INFO - LanisClient   Cryptor - Generate key: Generated key cfb787ef-....-4...-....-............-......3...
    INFO - LanisClient   Cryptor - Encrypt: Encrypted text U2FsdGVk....
    INFO - httpx   HTTP Request: POST https://start.schulportal.hessen.de/ajax.php?f=rsaPublicKey "HTTP/1.1 200 OK"
    Traceback (most recent call last):
    File "/home/kurwjan/Projects/LanisAPI/test/main.py", line 20, in <module>
        main()
    .... errors .....
    File "/home/kurwjan/Projects/LanisAPI/src/lanisapi/helpers/request.py", line 25, in get
        return cls._check_response(response)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/kurwjan/Projects/LanisAPI/src/lanisapi/helpers/request.py", line 70, in _check_response
        raise LoginPageRedirectError(msg)
    lanisapi.exceptions.LoginPageRedirectError: Lanis returned the login page while trying to access https://start.schulportal.hessen.de/ajax.php?f=rsaPublicKey. Maybe the session is over.

Often the full log is actually not needed but still please send the full log.

Library errors
--------------

Hopefully you will receive a ``AppNotAvailableError``, ``NotAuthenticatedError`` or similar error which are defined here.
These error are easily self-fixable.

*However if you get a* ``..NotFoundError`` *you need to probably open a bug report.*

``CriticalElementWasNotFoundError`` and html_logs.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you receive a ``CriticalElementWasNotFoundError`` there is something really wrong and it would be really helpful
that you report it and provide the content of the ``html_logs.txt``.
This file contains the suspicious html element *which may also contain sensitive data.*

Example ``html_logs.txt``
^^^^^^^^^^^^^^^^^^^^^^^^^
::

    ############.....
    # ... info and format ...
    ############.....

    #--Start------------------------#
    1700334895-get_task()-4-title: Missing element!

    *~~Element-HTML~~~~~~~~~~~~*

    <tr data-entry="1" data-book="4635" class="printable"> <td> <h3 style="margin: 0;"><a href="meinunterricht.php?a=sus_view&amp;id=4635" title="gesamte Kursmappe anschauen"> <i class="fa fa-flip-horizontal fa-address-book "></i> <span class="name">Erdkunde 09gc (091EK02-GYM)</span> </a> </h3> <span class="teacher"> <div class="btn-group"> <button type="button" class="btn btn-primary dropdown-toggle btn-xs" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Qaumy, Sohal (QAU)"> <i class="fa fa-user"></i> QAU <span class="caret"></span> </button> <ul class="dropdown-menu"> <li><a href="#"><i class="fa fa-user fa-fw"></i> Qaumy, Sohal</a></li> <li role="separator" class="divider"></li> <li> <a title="Nachricht schreiben" href="nachrichten.php?to[]=bC0xNzg2MjE=}"> <i class="fas fa-mail-bulk fa-fw"></i> Nachricht schreiben
                                        </a> </li> </ul> </div> </span> </td> <td> <b class="thema">PP Erdkunde Projektarbeit Raumanalyse</b> <small> <span class="datum">03.11.2023</span> </small> <br> </td> <td> <div class="btn-group-vertical btn-sameWidth " role="group" aria-label="Menü der Kursmappe"> <div class="btn-group files"> <button type="button" class="btn btn-info btn-sm dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"> <i class="fas fa-paperclip"></i> 1 Anhang <span class="caret"></span> </button> <ul class="dropdown-menu"> <li><a class="file" data-extension="pptx" data-file="PP-Projektarbeit-Klasse-9.pptx" href="#" target="_blank"> PP-Projektarbeit-Klasse-9.pptx <small>(17 MB)</small></a></li> <li role="separator" class="divider"></li> <li><a href="meinunterricht.php?a=downloadFile&amp;b=zip&amp;id=4635&amp;e=1" target="_blank"><i class="fa fa-file-zip-o fa-fw"></i> alle downloaden</a></li> </ul> </div> <a href="meinunterricht.php?a=sus_view&amp;id=4635" title="gesamte Kursmappe anschauen" class="btn btn-primary btn-sm"> <i class="fa fa-flip-horizontal fa-address-book "></i> alle Einträge                                                                
                                </a> </div> </td> </tr>
    #--End--------------------------#


Other errors
------------

Other errors like ``JSONDecodeError`` are probably caused by the library not supporting your school.
Please file a bug report with possible data to resolve it.
