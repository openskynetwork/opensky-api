.. The OpenSky Network API documentation master file, created by
   sphinx-quickstart on Tue Mar  1 19:48:21 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The OpenSky Network API documentation
=====================================

This is the official documentation of the OpenSky Network's live API. The API lets you retrieve live airspace information in the form of *State Vectors* (see below). The following paragraphs will help you understand how we represent an aircraft's state and how to use it. There is also a little more specific documentation available for our :doc:`REST API <rest>`. We provide a :doc:`Python <python>` language binding and a :doc:`Java <java>` language binding for the REST API.

.. _state-vectors:

State Vectors
-------------

Airplanes seen by the OpenSky Network are associated with states. The state of an aircraft is simply a summary of all tracking information (mainly position, velocity, and identity) for a certain point in time. We store these states in so called state vectors. Since state vectors are also what you get from the live API, we start with giving you a short introduction to state vectors.

In `ADS-B <https://en.wikipedia.org/wiki/Automatic_dependent_surveillance_%E2%80%93_broadcast>`_, each aircraft (actually each transponder) is identified with a unique address, the `ICAO 24-bit address <https://en.wikipedia.org/wiki/Aviation_transponder_interrogation_modes#ICAO_24-bit_address>`_. Usually this address is displayed in its 6-character hex representation (e.g. ``c0ffee``). OpenSky uses this address to distinguish aircraft.

As soon as an ADS-B message of an airplane arrives at our servers, we create a record for the aircraft -- the so called state vector. All information required to track the airplane, including its identity (ICAO address + call sign), time information (`Unix timestamps <https://en.wikipedia.org/wiki/Unix_time>`_), and spatial information (position, velocity, heading, ...) will be stored in this state vector.

**Example:** Let's assume an airplane with the address ``c0ffee`` enters the airspace covered by OpenSky on March 26, 2016 at about 11:13:44. At 11:13:44.097 it tells us its speed (230 m/s) and heading (30° clock-wise from north). We then create the following record:

    "At time 1458987225, we've seen ``c0ffee`` flying at 230m/s into direction 30°. Velocity was updated at 1458987224.097."

Within the next couple of microseconds, more information arrives and the state vector becomes filled. At time 11:13:44.15, the aircraft first tells us its call-sign *CONAIR*. At time 11:13:44.27, we learn its latitude (51.89°), longitude (1.28°), and altitude (11.5 km). Its state vector then looks like this:

    "At time 1458987225, we've seen ``c0ffee`` (call-sign *CONAIR*) at latitude 51.89°, longitude 1.28°, and altitude 11500m flying at 230m/s into direction 30°. Velocity was updated at 1458987224.097. Position was updated at 1458987224.27."

You might have noticed that the first timestamp in the state vector is rounded to the next full second. This is because we keep updating this state vector until 11:13:45 and then release it to the API. Consequently, the state vector returned by the API at 11:13:45 contains the most recent information known at that time.

Validity
""""""""
So what happens if we do not receive any position or velocity update for a while? Well, if the last known position of the airplane is not older than 15 seconds, we will just reuse it. If we do not know any prior position or if the last known position is too old (>15s), we will omit the position information in the state vector. The same applies for velocity information.

If we do not receive any position or velocity update for a duration of 15 seconds, we consider the state vector obsolete and the API won't return any further state vector for the respective airplane.

Further Reading
---------------

.. toctree::
   :maxdepth: 1

   Intro & Data Structures <self>
   REST API <rest>
   Python API <python>
   Java API <java>


