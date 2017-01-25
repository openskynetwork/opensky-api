The Mashape Live Flight Tracking API Documentation
==================================================


This is the documentation of the `Mashape Live Flight Tracking API <https://market.mashape.com/opensky/live-flight-tracking>`_. The API lets you retrieve live airspace information for commercial purposes. To get 
access to this API, you will need a Mashape account. If you want to retrieve live flight information for research and non-commercial purposes only, use the free `OpenSky API <https://opensky-network.org/apidoc/>`_ instead.

.. _state-vectors:

.. include:: ../free/state-vectors.rst


REST Endpoint Definition
------------------------

The root URL of our REST API is::

    https://opensky-network.p.mashape.com/


.. include:: ../free/rest-states-all-request.rst

Example query: :code:`https://opensky-network.p.mashape.com/states/all?time=1458564121&icao24=3c6444`

Response
^^^^^^^^
.. include:: ../free/states-response.rst

.. _limitations:

Limitations
^^^^^^^^^^^

Users can retrieve data of up to one hour in the past. If the time parameter has a value t<now−3600, the API will return ``400 Bad Request``.
The time resolution is 5 seconds. That means, if the time parameter is set to t, the API will return state vectors for time t−(t mod 5)


Examples
^^^^^^^^

Example Queries
"""""""""""""""

In all example queries, you need to replace `<requried>` with the key provided to you by Mashape.

Retrieve all states with curl:

.. code-block:: bash

    curl --get --include'https://opensky-network.p.mashape.com/states/all'  \
       -H'X-Mashape-Key: <required>'  \
       -H'Accept: application/json'

Retrieve state of two particular airplanes with curl:

.. code-block:: bash

    curl --get --include \
       'https://opensky-network.p.mashape.com/states/all?icao24=3c6444&icao24=3e1bf9'  \
       -H'X-Mashape-Key: <required>'  \
       -H'Accept: application/json'

Retrieve all states with Java:

.. code-block:: java

    // These code snippets use an open-source library. http://unirest.io/java
    HttpResponse<JsonNode> response = Unirest
        .get("https://opensky-network.p.mashape.com/states/all")
        .header("X-Mashape-Key","<required>")
        .header("Accept","application/json")
        .asJson();

Retrieve all states with Python:

.. code-block:: python

    # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get("https://opensky-network.p.mashape.com/states/all",
           headers={
             "X-Mashape-Key":"<required>",
             "Accept":"application/json"
           })


Example Responses
"""""""""""""""""

An example JSON response body for three aircraft:

.. code-block:: bash

    {"time": 1483630740, "states": [
        [ "89906b", "EVA810 ", "Taiwan", 1483630738, 1483630737, 121.3298, 25.1442, 548.64, false, 80.97, 229.12,-2.6, null ],
        [ "a1110d", "SKW1389 ", "United States", 1483630735, 1483630733, -119.8027, 35.4435, 7376.16, false, 218.1, 144.7, -6.5, null ],
        [ "a0cfbd", "AAL472 ", "United States", 1483630739, 1483630739, -102.9802, 38.5061, 10363.2, false, 172.43, 248.1, 0, null ] 
    ]}

For more examples on how to access the API, check `Mashape <https://market.mashape.com/opensky/live-flight-tracking>`_.


.. toctree::
    :hidden:
    :maxdepth: 1
 
    index
