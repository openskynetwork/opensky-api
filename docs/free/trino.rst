.. _trino:

Trino - Historical Data
=======================

.. warning::

   **Read this page - especially** :ref:`trino-performance` **- before writing any queries.**

   * This page contains everything you need to access OpenSky historical data via Trino.
   * Consult it thoroughly before reaching out for support; it likely contains the solution you are looking for.
   * Use the information here as your primary reference, rather than relying on AI-generated suggestions.
   * **Users who repeatedly ignore the performance guidelines will be banned.**

Besides the public REST API, OpenSky provides free access to its full dataset through an SQL-like query interface powered by `Trino <https://trino.io/>`_ and MinIO. This service is available to university-affiliated researchers, governmental organisations, and aviation authorities for aviation-related research and incident investigations. Private or commercial entities must contact us for a licence.

Access is granted based on application review. We reserve the right to decline applications lacking sufficient justification and to revoke access in cases of misuse.

----

.. _trino-getting-started:

Getting Started
---------------

In 2024, OpenSky transitioned to a new backend with an updated access method. Follow the steps below to connect.

1. Register an Account
^^^^^^^^^^^^^^^^^^^^^^

* Register an OpenSky account by clicking `Sign in` at: `OpenSky Register <https://opensky-network.org/>`_.
* Verify your email address.
* Go to **My OpenSky → Request Data Access** and fill out the application form.

2. Connect to Trino
^^^^^^^^^^^^^^^^^^^

Once access is granted, you can connect using:

* The **Trino CLI** (covered below).
* Community-supported Python libraries - `traffic <https://traffic-viz.github.io/>`_ and `pyOpenSky <https://mode-s.org/pyopensky/>`_ - which support Trino natively without requiring code changes. If you need custom logic, use these libraries as implementation references.

.. _trino-cli:

3. Connecting via the Trino CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, make sure you understand what Trino is and how to use it, then `download and install the Trino CLI <https://trino.io/docs/current/client/cli.html>`_.

Connect with the following command:

.. code-block:: bash

   trino --user=$USER --password \
         --server=https://trino.opensky-network.org \
         --external-authentication \
         --catalog "minio" \
         --schema "osky"

.. important::

   * Replace ``$USER`` with your OpenSky username. **Usernames are stored in lowercase** - always use lowercase when connecting via the CLI, Python, or any programmatic access method.
   * The ``--external-authentication`` flag causes a browser window to open so you can log in via the OpenSky website. You must use the same account in the web interface as in the CLI command.

----

.. _trino-exploring:

Exploring the Database
----------------------

List all available tables:

.. code-block:: sql

   SHOW TABLES;

The following 12 tables are currently available:

+----------------------------------+
| Table                            |
+==================================+
| acas_data4                       |
+----------------------------------+
| adsc                             |
+----------------------------------+
| allcall_replies_data4            |
+----------------------------------+
| flarm_raw                        |
+----------------------------------+
| flights_data4                    |
+----------------------------------+
| flights_data5                    |
+----------------------------------+
| identification_data4             |
+----------------------------------+
| operational_status_data4         |
+----------------------------------+
| position_data4                   |
+----------------------------------+
| rollcall_replies_data4           |
+----------------------------------+
| state_vectors_data4              |
+----------------------------------+
| velocity_data4                   |
+----------------------------------+

The ``_data4`` suffix indicates the 4th implementation of the batch layer, which is the current version. Earlier versions are deprecated and may be removed in the future.

If you are familiar with SSR Mode S downlink communications, the table names should be self-explanatory. For a comprehensive introduction to SSR Mode S, see Christian Wolff's `radar tutorial <https://www.radartutorial.eu/>`_. That said, most users only need the ``state_vectors_data4`` table, which is covered in detail below.

----

.. _trino-state-vectors:

State Vectors
-------------

State vectors are the most commonly used table. They summarise position, velocity, and status information derived from all raw Mode S messages. Inspect the schema with:

.. code-block:: sql

   DESCRIBE state_vectors_data4;

Schema
^^^^^^

+------------------+--------------+------------------------------------------------------+
| Column           | Type         | Description                                          |
+==================+==============+======================================================+
| time             | int          | Unix timestamp the state vector was valid at.        |
+------------------+--------------+------------------------------------------------------+
| icao24           | string       | Unique 24-bit transponder address (hex).             |
+------------------+--------------+------------------------------------------------------+
| lat              | double       | Latitude in decimal degrees (WGS84).                 |
+------------------+--------------+------------------------------------------------------+
| lon              | double       | Longitude in decimal degrees (WGS84).                |
+------------------+--------------+------------------------------------------------------+
| velocity         | double       | Speed over ground in **metres per second**.          |
+------------------+--------------+------------------------------------------------------+
| heading          | double       | Direction of movement in degrees from true north.    |
+------------------+--------------+------------------------------------------------------+
| vertrate         | double       | Vertical speed in **m/s** (positive = climbing).     |
+------------------+--------------+------------------------------------------------------+
| callsign         | string       | Flight identifier broadcast by the aircraft.         |
+------------------+--------------+------------------------------------------------------+
| onground         | boolean      | ``true`` if the aircraft is on the ground.           |
+------------------+--------------+------------------------------------------------------+
| alert            | boolean      | ATC alert squawk active.                             |
+------------------+--------------+------------------------------------------------------+
| spi              | boolean      | Special position indicator active.                   |
+------------------+--------------+------------------------------------------------------+
| squawk           | string       | 4-digit octal transponder code assigned by ATC.      |
+------------------+--------------+------------------------------------------------------+
| baroaltitude     | double       | Barometric altitude in **metres**.                   |
+------------------+--------------+------------------------------------------------------+
| geoaltitude      | double       | Geometric (GNSS) altitude in **metres**.             |
+------------------+--------------+------------------------------------------------------+
| lastposupdate    | double       | Timestamp of the last recorded position update.      |
+------------------+--------------+------------------------------------------------------+
| lastcontact      | double       | Last time OpenSky received a signal from the         |
|                  |              | aircraft.                                            |
+------------------+--------------+------------------------------------------------------+
| serials          | array<int>   | Serial numbers of the receivers that heard this      |
|                  |              | message.                                             |
+------------------+--------------+------------------------------------------------------+
| hour             | int          | **Partition column.** Unix timestamp of the start    |
|                  |              | of the hour this record belongs to.                  |
+------------------+--------------+------------------------------------------------------+

Units
^^^^^

All tables use a consistent unit system:

* **Speed**: metres per second
* **Distance / altitude**: metres
* **Time**: seconds (Unix timestamps)

Example Query
^^^^^^^^^^^^^

Retrieve a randomly selected state vector from a specific hour:

.. code-block:: sql

   SELECT *
   FROM state_vectors_data4
   WHERE hour = 1480759200
   ORDER BY rand()
   LIMIT 1;

Timestamps & Data Retention
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenSky retains state vectors for up to 300 seconds after an aircraft leaves coverage. To exclude stale vectors, add:

.. code-block:: sql

   AND time - lastcontact <= 15

``state_vectors_data4`` has unlimited retention. Some other tables retain data for approximately one year only.

----

.. _trino-other-tables:

The Other Tables
----------------

Most tables other than ``state_vectors_data4`` contain the columns ``mintime``, ``maxtime``, and ``msgcount``, which summarise duplicate messages:

* **mintime** - timestamp of the first message received in the interval.
* **maxtime** - timestamp of the last message received in the interval.
* **msgcount** - number of duplicate messages received.

For detailed specifications, refer to:

* **SSR Mode S tables** (``acas_data4``, ``allcall_replies_data4``, ``rollcall_replies_data4``): ICAO Annex 10 Volume 4.
* **ADS-B tables** (``identification_data4``, ``operational_status_data4``, ``position_data4``, ``velocity_data4``): RTCA DO-260B.

The ``flights_data4`` table provides structured flight data (one row per flight) and uses a **day** partition column instead of ``hour`` - see :ref:`trino-performance` for why this matters.

Example - all-call replies:

.. code-block:: sql

   SELECT *
   FROM allcall_replies_data4
   WHERE hour = 1478293200
   LIMIT 1;

----

.. _trino-performance:

Tools & Performance Considerations
-----------------------------------

.. danger::

   **Repeated failure to follow these guidelines will result in your account being suspended.**

   Always filter on the partition column. Always.

Python Libraries
^^^^^^^^^^^^^^^^

`traffic <https://traffic-viz.github.io/>`_ and `pyOpenSky <https://mode-s.org/pyopensky/>`_ are the recommended tools for most users. They provide high-level APIs for trajectory extraction, flight filtering, and more, and they query Trino natively without requiring you to write raw SQL.

**The performance rules below apply equally whether you are writing raw SQL or using traffic / pyOpenSky.** Both libraries ultimately issue Trino queries on your behalf. If you request a large, unpartitioned time range through the Python API, you will trigger exactly the same full-table scan as a poorly written SQL query. Always scope your requests to the smallest time window you actually need.

Performance Guidelines
^^^^^^^^^^^^^^^^^^^^^^

**1. Always filter on the partition column.**

   Every query *must* include a ``WHERE`` clause on the appropriate partition column:

   * ``hour`` - used by all tables **except** ``flights_data4``.
   * ``day`` - used by ``flights_data4``.

   The partition value is the Unix timestamp at the start of the respective hour or day. Without this filter, Trino performs a full table scan across the entire dataset, which is extremely slow and degrades performance for all users.

   .. code-block:: sql

      -- Correct: partition filter present
      SELECT * FROM state_vectors_data4
      WHERE hour = 1480762800
        AND icao24 = 'a0d724';

      -- WRONG: no partition filter - will scan the entire table
      SELECT * FROM state_vectors_data4
      WHERE icao24 = 'a0d724';

   .. note::
      For ``flights_data4``, always use ``WHERE day = <unix_day_timestamp>`` instead of ``hour``.
      Filtering on ``time`` alone is **not** sufficient - you must also include the partition column.

**2. Break large queries into smaller chunks.**

   Multiple targeted queries - each covering a short partition range - are faster and less resource-intensive than a single query spanning many days or weeks.

**3. Limit parallel queries.**

   The system is a shared resource. Each user is limited to **two concurrent queries** and **two queued queries**. Global limits also apply; if you receive a queue error, wait and retry.

**4. Avoid long-running queries.**

   The maximum query duration is **30 minutes**, including queuing time. If a query takes more than five minutes, reduce the time frame or split it into batches.

**5. Do not request bulk downloads via ad-hoc queries.**

   If you need multiple full-day datasets, contact us for alternative bulk-download solutions.

Killing Queries
^^^^^^^^^^^^^^^

If your process is stuck or running an unintended query, open the `Trino UI <https://trino.opensky-network.org/ui/>`_, filter by your username, navigate to the query subpage, and click **KILL** in the top-right corner.

----

.. _trino-examples:

Useful Query Examples
---------------------

The examples below are illustrative. For production use, consider the `traffic <https://traffic-viz.github.io/>`_ and `pyOpenSky <https://mode-s.org/pyopensky/>`_ libraries, which handle many of these patterns for you.

Latest Position per Aircraft (Every Minute)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sql

   SELECT v.*
   FROM state_vectors_data4 v
   JOIN (
       SELECT FLOOR(time / 60) AS minute,
              MAX(time)        AS recent,
              icao24
       FROM state_vectors_data4
       WHERE hour = 1480762800
       GROUP BY icao24, FLOOR(time / 60)
   ) m
     ON  v.icao24 = m.icao24
     AND v.time   = m.recent
   WHERE v.hour = 1480762800;

Last Position Seen by a Specific Receiver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sql

   SELECT v.*
   FROM state_vectors_data4 v
   JOIN (
       SELECT MAX(t.time) AS recent,
              COUNT(*)    AS cnt,
              t.icao24
       FROM state_vectors_data4 t
       CROSS JOIN UNNEST(t.serials) AS s(item)
       WHERE t.hour   = 1480762800
         AND s.item   = 1344390019
       GROUP BY t.icao24
       HAVING COUNT(*) > 30
   ) m
     ON  v.icao24 = m.icao24
     AND v.time   = m.recent
   WHERE v.hour = 1480762800;

.. note::

   The ``HAVING COUNT(*) > 30`` filter reduces noise from erroneous receiver associations. You can refine results further with latitude and longitude constraints.

Count Distinct Aircraft in an Airspace Sector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example: Frankfurt Airport vicinity.

.. code-block:: sql

   SELECT COUNT(DISTINCT icao24)
   FROM state_vectors_data4
   WHERE lat  BETWEEN 49.98 AND 50.07
     AND lon  BETWEEN 8.48  AND 8.62
     AND hour = 1493892000;

----

.. _trino-data-gaps:

Known Data Gaps
---------------

Due to technical issues in 2023 and 2024, some historical data was permanently lost. Exclude the periods below from your research to ensure accuracy (all times UTC):

+------------------------------+------------------------------+
| Start                        | End                          |
+==============================+==============================+
| 2023-01-02 23:00             | 2023-01-03 10:00             |
+------------------------------+------------------------------+
| 2023-01-18 11:00             | 2023-01-23 07:00             |
+------------------------------+------------------------------+
| 2023-06-21 13:00             | 2023-06-21 22:00             |
+------------------------------+------------------------------+
| 2023-11-15 06:00             | 2023-11-16 08:00             |
+------------------------------+------------------------------+
| 2023-11-20 01:00             | 2023-11-20 03:00             |
+------------------------------+------------------------------+
| 2023-12-02 08:00             | 2023-12-05 03:00             |
+------------------------------+------------------------------+
| 2024-05-20 10:00             | 2024-05-21 05:00             |
+------------------------------+------------------------------+

----

You are now ready to query OpenSky's historical dataset. If you discover anything noteworthy or have suggestions for improving this guide, please reach out to us.
