xaal.warp10
===========
This provide a warp10 (https://www.warp10.io/) logger for xAAL. It will log all xAAL messages to a warp10 instance.


Install & Run
-------------
You can install it using pip :

.. code-block:: bash

    $ pip install xaal.warp10

Then you can run it :

.. code-block:: bash

    $ python -m xaal.warp10
    # or
    $ xaal-pkgrun warp10


Config
------

.. code-block:: ini

    [config]
    url   = http://warp10:8080/api/v0/update
    topic = xaal-lab
    token = nI6H6KKxy3QSTxmfe0_lQyaBI0aV3gR4r5niVAKlaUb32cxIemlU7Vpb8AYhOkgZMz.bi...


Grafana
-------
You can use Grafana to display warp10 series, for example :

.. code-block::

    [
    'xxxxxxxx_key_xxxxx'
    '~xaal-home.thermometer.basic.temperature'
    { 'devid' '2f31c921-01b2-4097-bfae-5753dde2cd42' }
    $startISO $endISO
    ]
    FETCH
    'salon ' RENAME
    { 'devid' ''  '.app' '' } RELABEL
