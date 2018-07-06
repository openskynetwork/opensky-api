.. The OpenSky Network API documentation master file, created by
   sphinx-quickstart on Tue Mar  1 19:48:21 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The OpenSky Network API documentation
=====================================

This is the official documentation of the OpenSky Network's live API. The API lets you retrieve live airspace information for research and non-commerical purposes. See our `terms and conditions <https://opensky-network.org/about/terms-of-use>`_  for more details on the data license model. If you want to retrieve live flight information for commercial purposes, please `contact us <https://opensky-network.org/about/contact>`_.

Information is provided in the form of *State Vectors* (see below). The following paragraphs will help you understand how we represent an aircraft's state and how to use it. There is also a little more specific documentation available for our :doc:`REST API <rest>`. We provide a :doc:`Python <python>` language binding and a :doc:`Java <java>` language binding for the REST API.

.. _state-vectors:

.. include:: state-vectors.rst


Further Reading
---------------

.. toctree::
   :maxdepth: 1

   Intro & Data Structures <self>
   REST API <rest>
   Python API <python>
   Java API <java>


