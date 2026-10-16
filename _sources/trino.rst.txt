.. _trino:

Trino - Historical Data
=======================

.. warning::

   **Read this page closely - especially** :ref:`trino-performance` **- before writing any queries and especially if you are or are using an LLM.**

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

The following datasets are covered in this guide. Use ``SHOW TABLES`` to check the tables and views available to your account:

+----------------------------------+
| Table                            |
+==================================+
| acas_data4                       |
+----------------------------------+
| allcall_replies_data4            |
+----------------------------------+
| df18_data4                       |
+----------------------------------+
| flarm_decoded                    |
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
| readsb_adsc_sv                   |
+----------------------------------+
| readsb_mlat_sv                   |
+----------------------------------+
| rollcall_replies_data4           |
+----------------------------------+
| state_vectors_data4              |
+----------------------------------+
| velocity_data4                   |
+----------------------------------+

The ``_data4`` suffix identifies the fourth implementation of the batch layer. Earlier versions are deprecated.

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

State vectors use the following units. The sections below specify units for the other tables, including exceptions such as surface ground speeds in ``position_data4``:

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

``state_vectors_data4`` has unlimited retention since 2013, ``flights_data4`` since 2016. Other tables contain data for fewer years.

----

.. _trino-flights:

Flights
-------

``flights_data4`` contains one row per flight reconstructed from the state vectors, including a compact trajectory and estimated departure and arrival airports. These are inferred from received positions and coverage; the first and last observations are not necessarily the actual takeoff and landing times. An airport can remain unknown, and a callsign is not a unique flight identifier.

Inspect the schema before querying, especially when working with nested fields:

.. code-block:: sql

   DESCRIBE flights_data4;

Schema
^^^^^^

The types below use Trino names: ``integer`` corresponds to ``int`` and ``varchar`` to ``string`` in the state-vector schema above. ``row(...)`` denotes a nested record whose fields are listed in the description. Timestamps are Unix seconds, coordinates are WGS84 degrees, track altitudes are metres, and headings are degrees. Missing values can be null.

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``icao24``
        - ``varchar``
        - Aircraft transponder address as a lowercase hexadecimal string.
      * - ``firstseen``
        - ``integer``
        - Unix timestamp of the estimated start of the flight; may be null if departure was not observed.
      * - ``estdepartureairport``
        - ``varchar``
        - ICAO code of the departure airport estimated from the trajectory; null if no airport could be assigned.
      * - ``lastseen``
        - ``integer``
        - Unix timestamp of the estimated end of the flight. This determines the ``day`` partition.
      * - ``estarrivalairport``
        - ``varchar``
        - ICAO code of the arrival airport estimated from the trajectory; null if no airport could be assigned.
      * - ``callsign``
        - ``varchar``
        - Callsign most frequently observed during the flight.
      * - ``track``
        - ``array(row(...))``
        - Compact trajectory: waypoints with ``time integer``, ``latitude double``, ``longitude double``, ``altitude double``, ``heading real``, and ``onground boolean``.
      * - ``estdepartureairporthorizdistance``
        - ``integer``
        - Horizontal distance in metres from the first track point to the estimated departure airport.
      * - ``estdepartureairportvertdistance``
        - ``integer``
        - Vertical distance in metres from the first track point to the estimated departure airport.
      * - ``estarrivalairporthorizdistance``
        - ``integer``
        - Horizontal distance in metres from the last track point to the estimated arrival airport.
      * - ``estarrivalairportvertdistance``
        - ``integer``
        - Vertical distance in metres from the last track point to the estimated arrival airport.
      * - ``departureairportcandidatescount``
        - ``integer``
        - Number of candidate departure airports considered by the flight reconstruction.
      * - ``arrivalairportcandidatescount``
        - ``integer``
        - Number of candidate arrival airports considered by the flight reconstruction.
      * - ``otherdepartureairportcandidates``
        - ``array(row(...))``
        - Candidate airports, each with ``icao24 varchar``, ``horizdistance integer``, and ``vertdistance integer``. The nested ``icao24`` field holds an airport ICAO code, despite its name. Distances are in metres.
      * - ``otherarrivalairportcandidates``
        - ``array(row(...))``
        - Candidate arrival airports, with the same nested fields as the departure candidates.
      * - ``day``
        - ``integer``
        - **Partition column.** Unix timestamp at 00:00 UTC on the day containing ``lastseen``.

Example Query
^^^^^^^^^^^^^

Retrieve flights ending on 1 April 2026 (UTC):

.. code-block:: sql

   SELECT icao24, callsign, firstseen, lastseen,
          estdepartureairport, estarrivalairport
   FROM flights_data4
   WHERE day = 1775001600
   LIMIT 10;

For a departure-time search, include subsequent arrival-day partitions as necessary: a flight can end on the next UTC day. A filter on ``firstseen`` or ``lastseen`` alone does not replace the required ``day`` filter; see :ref:`trino-performance`.

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

The ``flights_data4`` dataset is described in :ref:`trino-flights`. It uses **day** partitions rather than **hour** partitions.

Example - all-call replies:

.. code-block:: sql

   SELECT *
   FROM allcall_replies_data4
   WHERE hour = 1478293200
   LIMIT 1;

ADS-C State Vectors (``readsb_adsc_sv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This table contains ADS-C (Automatic Dependent Surveillance–Contract) state vectors collected via `JAERO <https://github.com/jontio/JAERO>`_ and `Readsb <https://github.com/wiedehopf/readsb>`_. ADS-C is a satellite-based surveillance technology used on oceanic and polar routes where conventional ground-based receivers provide no coverage. JAERO decodes ADS-C messages from Inmarsat ACARS satellite links.

Unlike the ``_data4`` tables, this table does **not** contain ``mintime``, ``maxtime``, or ``msgcount`` columns.

Further reading: `OpenSky ADS-C dataset <https://opensky-network.org/data/scientific#d9>`_ and `OpenSky Report 2025: Improving Crowdsourced Flight Trajectories with ADS-C Data <https://arxiv.org/abs/2505.06254>`_.

+------------------+---------+------------------------------------------------------+
| Column           | Type    | Description                                          |
+==================+=========+======================================================+
| time             | double  | Unix timestamp the state vector was valid at.        |
+------------------+---------+------------------------------------------------------+
| icao24           | varchar | Unique 24-bit transponder address (hex).             |
+------------------+---------+------------------------------------------------------+
| callsign         | varchar | Flight identifier broadcast by the aircraft.         |
+------------------+---------+------------------------------------------------------+
| lat              | double  | Latitude in decimal degrees (WGS84).                 |
+------------------+---------+------------------------------------------------------+
| lon              | double  | Longitude in decimal degrees (WGS84).                |
+------------------+---------+------------------------------------------------------+
| velocity         | double  | Speed over ground in **metres per second**.          |
+------------------+---------+------------------------------------------------------+
| heading          | double  | Direction of movement in degrees from true north.    |
+------------------+---------+------------------------------------------------------+
| vertrate         | double  | Vertical speed in **m/s** (positive = climbing).     |
+------------------+---------+------------------------------------------------------+
| baroaltitude     | double  | Barometric altitude in **metres**.                   |
+------------------+---------+------------------------------------------------------+
| hour             | bigint  | **Partition column.** Unix timestamp of the start    |
|                  |         | of the hour this record belongs to.                  |
+------------------+---------+------------------------------------------------------+

MLAT State Vectors (``readsb_mlat_sv``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This table contains multilateration (MLAT) state vectors collected via `mlat-client <https://github.com/mutability/mlat-client>`_, `mlat-server <https://github.com/mutability/mlat-server>`_, and `Readsb <https://github.com/wiedehopf/readsb>`_. MLAT uses time-difference-of-arrival measurements from multiple ground receivers to locate aircraft that do not transmit ADS-B position messages. Coverage depends on the density of participating receivers.

Unlike the ``_data4`` tables, this table does **not** contain ``mintime``, ``maxtime``, or ``msgcount`` columns.

+------------------+---------+------------------------------------------------------+
| Column           | Type    | Description                                          |
+==================+=========+======================================================+
| time             | double  | Unix timestamp the state vector was valid at.        |
+------------------+---------+------------------------------------------------------+
| icao24           | varchar | Unique 24-bit transponder address (hex).             |
+------------------+---------+------------------------------------------------------+
| lat              | double  | Latitude in decimal degrees (WGS84).                 |
+------------------+---------+------------------------------------------------------+
| lon              | double  | Longitude in decimal degrees (WGS84).                |
+------------------+---------+------------------------------------------------------+
| hour             | integer | **Partition column.** Unix timestamp of the start    |
|                  |         | of the hour this record belongs to.                  |
+------------------+---------+------------------------------------------------------+

.. _trino-flarm:

Decoded FLARM Messages (``flarm_decoded``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``flarm_decoded`` contains decoded FLARM traffic received through the Open Glider Network (OGN), together with the original reception metadata. It supports research on gliders and other low-altitude traffic that may not appear in ADS-B state vectors. Further reading: `OpenSky Report 2023: Low Altitude Traffic Awareness for Light Aircraft with FLARM <https://doi.org/10.1109/DASC58513.2023.10311202>`_.

Each row represents a decoded reception, rather than a fused state vector or a Mode S de-duplication group. The table has no ``mintime``, ``maxtime``, or ``msgcount`` columns. Receptions failing the CRC check, lacking the raw message or receiver position, failing to decode, or yielding a position more than 150 km from the receiver are excluded. The identifier namespace differs from ADS-B: do not join on ``icao24`` alone without checking ``radioidentifiertype``.

.. code-block:: sql

   DESCRIBE flarm_decoded;

Schema
""""""

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``hour``
        - ``integer``
        - **Partition column.** Start of the UTC hour containing ``timeatplane``, in Unix seconds.
      * - ``sensortype``
        - ``varchar``
        - Receiving sensor type reported in the message envelope.
      * - ``sensorlatitude``
        - ``double``
        - Receiver latitude in WGS84 degrees.
      * - ``sensorlongitude``
        - ``double``
        - Receiver longitude in WGS84 degrees.
      * - ``sensoraltitude``
        - ``integer``
        - Receiver altitude in metres, if available.
      * - ``timeatserver``
        - ``double``
        - Unix timestamp when the ingestion server received the message.
      * - ``timeatsensor``
        - ``double``
        - Sensor receive timestamp from the envelope, if provided.
      * - ``timestamp``
        - ``double``
        - Additional timestamp from the raw envelope, if provided.
      * - ``timeatplane``
        - ``integer``
        - Estimated transmission time at the aircraft, in Unix seconds.
      * - ``rawmessage``
        - ``varchar``
        - Raw FLARM message in hexadecimal.
      * - ``crc``
        - ``varchar``
        - CRC field from the raw envelope.
      * - ``rawsoftmessage``
        - ``varchar``
        - Soft-bit representation of the received message and CRC, in hexadecimal, if available.
      * - ``sensorname``
        - ``varchar``
        - Receiver name reported by OGN.
      * - ``ntperror``
        - ``real``
        - Receiver clock error relative to NTP, in milliseconds.
      * - ``userfreqcorrection``
        - ``real``
        - User-configured receiver frequency correction, in ppm.
      * - ``autofreqcorrection``
        - ``real``
        - Additional automatic frequency correction, in ppm.
      * - ``frequency``
        - ``double``
        - Reception frequency in MHz.
      * - ``channel``
        - ``integer``
        - Reception channel.
      * - ``snrdetector``
        - ``double``
        - Signal-to-noise ratio reported by the detector.
      * - ``snrdemodulator``
        - ``double``
        - Signal-to-noise ratio reported by the demodulator.
      * - ``typeogn``
        - ``boolean``
        - Envelope flag distinguishing OGN-tracker messages (``true``) from FLARM messages (``false``).
      * - ``crccorrect``
        - ``boolean``
        - Whether the envelope CRC passed; failed CRCs are excluded from this table.
      * - ``rawudppacket``
        - ``varbinary``
        - Complete raw OGN UDP packet, if retained in the envelope.
      * - ``decodedtimestamp``
        - ``double``
        - Unix transmission timestamp used for decoding; currently the same value as ``timeatplane``.
      * - ``icao24``
        - ``varchar``
        - Raw 24-bit radio identifier as lowercase hexadecimal. Interpret it together with ``radioidentifiertype``; it is not always an ICAO transponder address.
      * - ``icao24num``
        - ``integer``
        - Numeric representation of the 24-bit radio identifier.
      * - ``messagetype``
        - ``integer``
        - Message type from the packet header.
      * - ``radioidentifiertype``
        - ``varchar``
        - Identifier type: ``RANDOM``, ``ICAO``, ``FLARM``, or ``FLARM_EXTENDED``.
      * - ``urgency``
        - ``varchar``
        - Reported urgency: ``Normal``, ``High``, ``PanPan``, or ``Mayday``.
      * - ``icaoext``
        - ``varchar``
        - Extended radio identifier field, in hexadecimal.
      * - ``messagetypeext``
        - ``integer``
        - Extended message-type field.
      * - ``isstealth``
        - ``boolean``
        - Stealth/privacy flag reported by the sender.
      * - ``isnotrack``
        - ``boolean``
        - No-track flag reported by the sender.
      * - ``version``
        - ``integer``
        - Protocol version used for transmission.
      * - ``versionmax``
        - ``integer``
        - Maximum receive protocol version reported by the sender.
      * - ``flarmtime``
        - ``integer``
        - Truncated protocol time field; not a complete Unix timestamp. Use ``decodedtimestamp`` for time filtering.
      * - ``aircrafttype``
        - ``varchar``
        - Reported aircraft or object category, such as glider, towplane, helicopter, or UAV.
      * - ``latitude``
        - ``double``
        - Decoded aircraft latitude in WGS84 degrees.
      * - ``longitude``
        - ``double``
        - Decoded aircraft longitude in WGS84 degrees.
      * - ``altitude``
        - ``double``
        - Decoded WGS84 altitude in metres.
      * - ``turnrate``
        - ``double``
        - Turn rate in degrees per second.
      * - ``speed``
        - ``double``
        - Ground speed in metres per second.
      * - ``climbrate``
        - ``double``
        - Vertical speed in metres per second; positive means climbing.
      * - ``track``
        - ``double``
        - Ground track in degrees.
      * - ``movementmode``
        - ``varchar``
        - Reported movement mode: ``Unknown``, ``OnGround``, ``Flying``, or ``Circling``.
      * - ``accposhor``
        - ``double``
        - Horizontal position accuracy estimate in metres (95% CEP).
      * - ``accposver``
        - ``double``
        - Vertical position accuracy estimate in metres (95% confidence).
      * - ``accvel``
        - ``double``
        - Velocity accuracy estimate in metres per second (95% confidence).
      * - ``sil``
        - ``varchar``
        - Source Integrity Level, stored as a decoder enumeration name.
      * - ``sda``
        - ``varchar``
        - System Design Assurance, stored as a decoder enumeration name.
      * - ``nic``
        - ``varchar``
        - Navigation Integrity Category, stored as a decoder enumeration name.
      * - ``payload``
        - ``varbinary``
        - Normalised 24-byte FLARM radio payload.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT decodedtimestamp, icao24, radioidentifiertype,
          latitude, longitude, altitude, speed, climbrate, sensorname
   FROM flarm_decoded
   WHERE hour = 1775001600
   LIMIT 10;

The ``hour`` partition follows transmission time, not ``timeatserver``. Always include it even when also filtering on a more precise timestamp.

.. _trino-message-columns:

Shared Decoded-Message Columns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The seven ``_data4`` message tables below share these columns. A row groups copies of the same message received by one or more sensors; ``msgcount`` counts receptions, not unique aircraft or distinct transmissions. The per-table schemas list the additional columns. SQL column names are shown in lowercase and types use Trino notation.

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``hour``
        - ``integer``
        - **Partition column.** Start of the UTC hour containing ``mintime``, in Unix seconds.
      * - ``sensors``
        - ``array(row(...))``
        - Receiving sensors. Each record has ``serial integer``, ``mintime double``, and ``maxtime double``: the receiver serial and its first/last receive timestamps in Unix seconds.
      * - ``rawmsg``
        - ``varchar``
        - Raw Mode S message as a hexadecimal string.
      * - ``mintime``
        - ``double``
        - Earliest receive timestamp across the sensors, in Unix seconds.
      * - ``maxtime``
        - ``double``
        - Latest receive timestamp across the sensors, in Unix seconds.
      * - ``msgcount``
        - ``bigint``
        - Total receptions represented by this row, including duplicate copies.
      * - ``icao24``
        - ``varchar``
        - Aircraft transponder address as a lowercase hexadecimal string.

Fields that are unavailable or do not apply to a message can be null. Encoded status and integrity fields must be interpreted for the relevant message format and ADS-B version; zero is not necessarily a valid measurement or a positive capability report.

.. _trino-acas-data4:

ACAS Messages (``acas_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded short (DF 0) and long (DF 16) Airborne Collision Avoidance System replies. ``islongformat`` distinguishes the formats. Cross-link capability is available only in short replies; resolution-advisory fields are available only in long replies.

.. code-block:: sql

   DESCRIBE acas_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``islongformat``
        - ``boolean``
        - ``true`` for a long ACAS reply; ``false`` for a short reply.
      * - ``isairborne``
        - ``boolean``
        - Airborne status reported by the aircraft.
      * - ``hascrosslinkcapability``
        - ``boolean``
        - Cross-link capability; short replies only.
      * - ``sensitivitylevel``
        - ``smallint``
        - ACAS sensitivity level code.
      * - ``replyinformation``
        - ``smallint``
        - Reply Information (RI) field.
      * - ``altitude``
        - ``double``
        - Decoded altitude in metres, when available.
      * - ``hasvalidrac``
        - ``boolean``
        - Validity of the Resolution Advisory Complement (RAC); long replies only.
      * - ``activeresolutionadvisories``
        - ``smallint``
        - Bitfield of active resolution advisories; long replies only.
      * - ``resolutionadvisorycomplement``
        - ``smallint``
        - Resolution Advisory Complement bitfield; long replies only.
      * - ``nopassbelow``
        - ``boolean``
        - Do-not-pass-below advisory-complement flag; long replies only.
      * - ``nopassabove``
        - ``boolean``
        - Do-not-pass-above advisory-complement flag; long replies only.
      * - ``noturnleft``
        - ``boolean``
        - Do-not-turn-left advisory-complement flag; long replies only.
      * - ``noturnright``
        - ``boolean``
        - Do-not-turn-right advisory-complement flag; long replies only.
      * - ``hasterminated``
        - ``boolean``
        - Resolution-advisory termination flag; long replies only.
      * - ``hasmultiplethreats``
        - ``boolean``
        - Multiple-threat flag; long replies only.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, islongformat, altitude, activeresolutionadvisories
   FROM acas_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-allcall-replies-data4:

All-Call Replies (``allcall_replies_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded Mode S all-call replies (DF 11), carrying the transponder address, capability information, and interrogator identifier.

.. code-block:: sql

   DESCRIBE allcall_replies_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``capabilities``
        - ``smallint``
        - Transponder Capability (CA) field.
      * - ``interrogatorid``
        - ``smallint``
        - Decoded interrogator identifier associated with the reply.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, capabilities, interrogatorid
   FROM allcall_replies_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-identification-data4:

Aircraft Identification Messages (``identification_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded ADS-B aircraft identification messages (type codes 1–4). These contain the broadcast callsign and emitter category, rather than a position or a flight-plan identifier. Interpret ``emittercategory`` together with ``ftc``.

.. code-block:: sql

   DESCRIBE identification_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``emittercategory``
        - ``smallint``
        - Emitter category within the category set selected by the type code.
      * - ``ftc``
        - ``smallint``
        - Format type code of the identification message.
      * - ``identity``
        - ``varchar``
        - Transmitted callsign / flight identification; may contain padding spaces.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, identity, ftc, emittercategory
   FROM identification_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-operational-status-data4:

Operational Status Messages (``operational_status_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded ADS-B operational-status messages, describing transponder capabilities, operating modes, and navigation quality. The schema combines ADS-B versions 0, 1, and 2 and both airborne and surface subtypes. Use ``version`` and ``subtypecode`` when interpreting the other fields. Nullable small-integer capability fields use 1 for true and 0 for false; null means unavailable. Some non-nullable fields retain default values when they are not populated for a particular version or subtype.

.. code-block:: sql

   DESCRIBE operational_status_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``subtypecode``
        - ``tinyint``
        - 0 for airborne, 1 for surface operational status.
      * - ``unknowncapcode``
        - ``boolean``
        - Decoder flag for an unrecognised capability code.
      * - ``unknownopcode``
        - ``boolean``
        - Decoder flag for an unrecognised operational-mode code.
      * - ``hasoperationaltcas``
        - ``smallint``
        - Whether TCAS/ACAS is operational; airborne status.
      * - ``has1090esin``
        - ``boolean``
        - 1090 MHz Extended Squitter receive capability.
      * - ``supportsairreferencedvelocity``
        - ``smallint``
        - Air-referenced velocity reporting capability; airborne status.
      * - ``haslowtxpower``
        - ``smallint``
        - Low-transmit-power indicator; surface status.
      * - ``supportstargetstatereport``
        - ``smallint``
        - Target-state reporting capability; airborne status.
      * - ``supportstargetchangereport``
        - ``smallint``
        - Target/trajectory-change reporting capability; airborne status.
      * - ``hasuatin``
        - ``boolean``
        - 978 MHz UAT receive capability.
      * - ``nacv``
        - ``tinyint``
        - Navigation Accuracy Category for velocity; surface status.
      * - ``nicsupplementc``
        - ``smallint``
        - NIC supplement C; surface status.
      * - ``hastcasresolutionadvisory``
        - ``boolean``
        - Active TCAS resolution-advisory flag.
      * - ``hasactiveidentswitch``
        - ``boolean``
        - Active IDENT switch flag.
      * - ``usessingleantenna``
        - ``boolean``
        - Single-antenna operation flag.
      * - ``systemdesignassurance``
        - ``tinyint``
        - System Design Assurance level.
      * - ``gpsantennaoffset``
        - ``tinyint``
        - Encoded GPS antenna-offset field; surface status.
      * - ``airplanelength``
        - ``integer``
        - Decoded aircraft-length bound in metres; surface status.
      * - ``airplanewidth``
        - ``double``
        - Decoded aircraft-width bound in metres; surface status.
      * - ``version``
        - ``tinyint``
        - ADS-B version number.
      * - ``nicsupplementa``
        - ``boolean``
        - NIC supplement A bit.
      * - ``positionnac``
        - ``double``
        - Navigation Accuracy Category for position, stored as a double.
      * - ``geometricverticalaccuracy``
        - ``integer``
        - Decoded geometric vertical-accuracy bound in metres; -1 indicates unknown in the decoder.
      * - ``sourceintegritylevel``
        - ``tinyint``
        - Source Integrity Level (SIL) code.
      * - ``barometricaltitudeintegritycode``
        - ``smallint``
        - Barometric-altitude integrity (NICbaro) flag; airborne status.
      * - ``trackheadinginfo``
        - ``smallint``
        - Track-angle/heading interpretation flag; surface status.
      * - ``horizontalreferencedirection``
        - ``boolean``
        - ``false`` for true north, ``true`` for magnetic north.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, version, subtypecode, positionnac, sourceintegritylevel
   FROM operational_status_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-position-data4:

Position Messages (``position_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded ADS-B airborne and surface position messages. These are individual decoded message groups, not regularly sampled state vectors. Latitude, longitude, and altitude can be null when the CPR (Compact Position Reporting) decoder cannot resolve or accept the position. Use ``surface`` and ``baroalt`` to interpret the fields.

.. code-block:: sql

   DESCRIBE position_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``nicsuppla``
        - ``boolean``
        - Navigation Integrity Category (NIC) supplement A bit.
      * - ``hcr``
        - ``double``
        - Horizontal containment radius in metres.
      * - ``nic``
        - ``smallint``
        - Navigation Integrity Category.
      * - ``survstatus``
        - ``smallint``
        - Surveillance status: 0 = no condition, 1 = permanent alert, 2 = temporary alert, 3 = SPI.
      * - ``nicsupplb``
        - ``boolean``
        - NIC supplement B bit.
      * - ``odd``
        - ``boolean``
        - CPR frame parity: ``true`` for odd, ``false`` for even.
      * - ``baroalt``
        - ``boolean``
        - For airborne messages, ``true`` means barometric altitude and ``false`` geometric altitude.
      * - ``lat``
        - ``double``
        - Decoded WGS84 latitude in decimal degrees.
      * - ``lon``
        - ``double``
        - Decoded WGS84 longitude in decimal degrees.
      * - ``alt``
        - ``double``
        - Decoded altitude in metres.
      * - ``nicsupplc``
        - ``boolean``
        - NIC supplement C bit.
      * - ``groundspeed``
        - ``double``
        - Surface ground speed in **knots**, as returned by the decoder.
      * - ``gsresolution``
        - ``double``
        - Surface ground-speed quantisation step in **knots**.
      * - ``heading``
        - ``double``
        - Surface heading/track angle in degrees, when valid.
      * - ``timeflag``
        - ``boolean``
        - ADS-B time (T) bit.
      * - ``surface``
        - ``boolean``
        - ``true`` for surface position messages; ``false`` for airborne messages.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, lat, lon, alt, baroalt
   FROM position_data4
   WHERE hour = 1775001600
     AND surface = false
     AND lat IS NOT NULL AND lon IS NOT NULL
   LIMIT 10;

.. _trino-rollcall-replies-data4:

Roll-Call Replies (``rollcall_replies_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded Mode S altitude and identity replies (DF 4/5) and Comm-B altitude and identity replies (DF 20/21). ``isid`` distinguishes identity replies from altitude replies. The raw Comm-B register payload is retained in ``message``; its BDS register contents are not decoded into separate columns.

.. code-block:: sql

   DESCRIBE rollcall_replies_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``message``
        - ``varchar``
        - Raw Comm-B register payload, when present.
      * - ``isid``
        - ``boolean``
        - ``true`` for an identity reply, ``false`` for an altitude reply.
      * - ``flightstatus``
        - ``tinyint``
        - Flight Status (FS) field.
      * - ``downlinkrequest``
        - ``tinyint``
        - Downlink Request (DR) field.
      * - ``utilitymsg``
        - ``tinyint``
        - Utility Message (UM) field.
      * - ``interrogatorid``
        - ``tinyint``
        - Interrogator identifier from the utility message.
      * - ``identifierdesignator``
        - ``tinyint``
        - Identifier designator from the utility message.
      * - ``valuecode``
        - ``smallint``
        - Encoded identity or altitude code, according to ``isid``.
      * - ``altitude``
        - ``double``
        - Decoded altitude in metres for altitude replies; otherwise null.
      * - ``identity``
        - ``varchar``
        - Decoded four-digit octal Mode A squawk for identity replies; otherwise null.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, isid, altitude, identity, message
   FROM rollcall_replies_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-velocity-data4:

Velocity Messages (``velocity_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoded ADS-B airborne ground-velocity messages. East–west and north–south components, ground speed, track, vertical rate, and geometric-minus-barometric altitude are stored where available. Surface ground speeds are in ``position_data4`` instead.

.. code-block:: sql

   DESCRIBE velocity_data4;

Schema
""""""

In addition to the :ref:`shared decoded-message columns <trino-message-columns>`:

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``supersonic``
        - ``boolean``
        - Whether the message uses the supersonic velocity encoding with a four-times-coarser step.
      * - ``intentchange``
        - ``boolean``
        - Intent-change flag.
      * - ``ifrcapability``
        - ``boolean``
        - IFR capability flag.
      * - ``nac``
        - ``smallint``
        - Legacy navigation-accuracy category for velocity. Decoder-version compatibility can leave this at 0; do not infer velocity accuracy from it without checking the data.
      * - ``ewvelocity``
        - ``double``
        - East–west ground-velocity component in metres per second (positive west, following the decoder convention).
      * - ``nsvelocity``
        - ``double``
        - North–south ground-velocity component in metres per second (positive south, following the decoder convention).
      * - ``baro``
        - ``boolean``
        - ``true`` if the vertical rate is barometric; ``false`` if geometric.
      * - ``vertrate``
        - ``double``
        - Vertical rate in metres per second; positive means climbing.
      * - ``geominurbaro``
        - ``double``
        - Geometric minus barometric altitude in metres. The column name retains this legacy spelling.
      * - ``heading``
        - ``double``
        - Ground track derived from the velocity components, in degrees from true north.
      * - ``velocity``
        - ``double``
        - Ground speed in metres per second.

Example Query
"""""""""""""

.. code-block:: sql

   SELECT mintime, icao24, velocity, heading, vertrate, geominurbaro
   FROM velocity_data4
   WHERE hour = 1775001600
   LIMIT 10;

.. _trino-df18-data4:

DF18 Messages (``df18_data4``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Downlink Format 18 (DF18) carries non-transponder ADS-B, Traffic Information Service–Broadcast (TIS-B), and ADS-B rebroadcast (ADS-R) messages. ``df18_data4`` combines these formats in one table, decoded with `lib1090 <https://github.com/SeRoSystems/lib1090>`_. Use ``cf`` (Control Field), ``addresstype``, and ``msgkind`` to distinguish their contents:

* ``cf`` 0 or 1: non-transponder ADS-B.
* ``cf`` 2, 3, or 5: TIS-B, including coarse position reports for ``cf`` 3.
* ``cf`` 6: ADS-R.
* ``cf`` 4 or 7: management/reserved formats that the decoder retains as reception metadata without decoded payload fields.

Each row groups duplicate receptions. The reception columns follow the :ref:`shared decoded-message columns <trino-message-columns>`, but this table uses ``address`` and ``addresstype`` instead of ``icao24``. The raw address can identify a non-ICAO target or a track file; do not join it to an aircraft's ICAO address without checking the address type and message format.

Payload fields that do not apply to the message kind are null. ``msgkind`` also identifies rows retained after an unsupported format or decoding failure: ``unsupported``, ``bad_format``, or ``decode_error``. Decoded coordinates are populated only after the position decoder accepts the fix; a null position does not necessarily mean that reception failed.

.. note::

   The scheduled DF18 decoding job is disabled in the documented batch configuration. The table definition alone does not establish continuous historical coverage.

.. code-block:: sql

   DESCRIBE df18_data4;

Schema
""""""

.. container:: wy-table-responsive

   .. list-table::
      :header-rows: 1
      :widths: 27 18 55

      * - Column
        - Type
        - Description
      * - ``sensors``
        - ``array(row(...))``
        - Receiving sensors, with ``serial integer``, ``mintime double``, and ``maxtime double`` for each receiver.
      * - ``rawmsg``
        - ``varchar``
        - Raw 112-bit DF18 message as a hexadecimal string.
      * - ``mintime``
        - ``double``
        - Earliest receive timestamp across the sensors, in Unix seconds.
      * - ``maxtime``
        - ``double``
        - Latest receive timestamp across the sensors, in Unix seconds.
      * - ``msgcount``
        - ``bigint``
        - Total receptions represented by this row, including duplicate copies.
      * - ``address``
        - ``varchar``
        - Raw 24-bit address field as lowercase hexadecimal; not necessarily an ICAO aircraft address.
      * - ``addresstype``
        - ``varchar``
        - Decoder classification of the address namespace; ``UNKNOWN`` for rows without a decoded payload.
      * - ``cf``
        - ``tinyint``
        - Control Field selecting the DF18 message format.
      * - ``imf``
        - ``boolean``
        - ICAO/Mode A Flag, where the message format carries one.
      * - ``msgkind``
        - ``varchar``
        - Decoded message kind in lowercase, or the decoding outcome described above.
      * - ``formattypecode``
        - ``smallint``
        - Extended Squitter format type code, where applicable.
      * - ``mepayload``
        - ``varchar``
        - Raw Extended Squitter ME payload in hexadecimal, where applicable.
      * - ``lat``
        - ``double``
        - Accepted decoded latitude in WGS84 degrees.
      * - ``lon``
        - ``double``
        - Accepted decoded longitude in WGS84 degrees.
      * - ``alt``
        - ``double``
        - Decoded altitude in **metres**; interpret using ``alttype``.
      * - ``alttype``
        - ``varchar``
        - Altitude reference reported by the decoder, such as barometric or geometric.
      * - ``surface``
        - ``boolean``
        - ``true`` for surface position messages; ``false`` for airborne position messages and coarse TIS-B reports (``cf`` 3).
      * - ``odd``
        - ``boolean``
        - CPR frame parity: ``true`` for odd, ``false`` for even.
      * - ``cprencodedlat``
        - ``integer``
        - Encoded CPR latitude before position decoding.
      * - ``cprencodedlon``
        - ``integer``
        - Encoded CPR longitude before position decoding.
      * - ``cprnumbits``
        - ``integer``
        - Number of bits in each encoded CPR coordinate.
      * - ``positionreasonable``
        - ``boolean``
        - Whether an extracted position passed the decoder's plausibility checks; null if no fix was extracted.
      * - ``nic``
        - ``smallint``
        - Navigation Integrity Category.
      * - ``nacp``
        - ``tinyint``
        - Navigation Accuracy Category for position.
      * - ``nacv``
        - ``tinyint``
        - Navigation Accuracy Category for velocity.
      * - ``sil``
        - ``tinyint``
        - Source Integrity Level.
      * - ``hcr``
        - ``double``
        - Horizontal containment radius limit in metres.
      * - ``survstatus``
        - ``smallint``
        - Surveillance status code, where available.
      * - ``nicsuppla``
        - ``boolean``
        - NIC supplement A bit, where available.
      * - ``nicsupplc``
        - ``boolean``
        - Additional NIC supplement: C for surface messages; airborne ADS-B version 2 rows store the B bit in this column.
      * - ``groundspeed``
        - ``double``
        - Ground speed in **knots**.
      * - ``heading``
        - ``double``
        - Heading or ground track in degrees, according to the message kind. ``ismagneticheading`` gives the reference when populated.
      * - ``ismagneticheading``
        - ``boolean``
        - ``true`` for magnetic heading and ``false`` for true heading, where the decoder supplies this distinction.
      * - ``airspeed``
        - ``double``
        - Airspeed in **knots**; interpret using ``istrueairspeed``.
      * - ``istrueairspeed``
        - ``boolean``
        - ``true`` for true airspeed; ``false`` for indicated airspeed.
      * - ``verticalrate``
        - ``double``
        - Vertical rate in **feet per minute**; positive means climbing.
      * - ``geominusbaro``
        - ``integer``
        - Geometric minus barometric altitude in **feet**, as returned by the decoder.
      * - ``issupersonic``
        - ``boolean``
        - Whether the velocity message uses the supersonic encoding.
      * - ``servicevolumeid``
        - ``smallint``
        - TIS-B site/service-volume identifier; coarse TIS-B reports only.
      * - ``groundtrackangle``
        - ``double``
        - Ground track in degrees clockwise from true north; coarse TIS-B reports only.
      * - ``mingroundspeed``
        - ``double``
        - Lower bound of the reported ground-speed interval in **knots**; coarse TIS-B reports only.
      * - ``maxgroundspeed``
        - ``double``
        - Upper bound of the reported ground-speed interval in **knots**; coarse TIS-B reports only.
      * - ``callsign``
        - ``varchar``
        - Transmitted callsign / flight identification, where available.
      * - ``emittercategory``
        - ``smallint``
        - Emitter category, where available.
      * - ``adsbversion``
        - ``tinyint``
        - ADS-B/ADS-R version tracked by the stateful decoder.
      * - ``hour``
        - ``integer``
        - **Partition column.** Start of the UTC hour containing ``mintime``, in Unix seconds.

Units
"""""

Unlike ``state_vectors_data4`` and ``velocity_data4``, DF18 speed fields remain in **knots**, ``verticalrate`` in **feet per minute**, and ``geominusbaro`` in **feet**. ``alt`` and ``hcr`` are in metres. Convert these units before combining datasets.

Example Query
"""""""""""""

Retrieve accepted decoded positions from one hour:

.. code-block:: sql

   SELECT mintime, address, addresstype, cf, msgkind,
          lat, lon, alt, alttype
   FROM df18_data4
   WHERE hour = 1775001600
     AND positionreasonable = true
     AND lat IS NOT NULL AND lon IS NOT NULL
   LIMIT 10;

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

   * ``hour`` - used by the state-vector and decoded-message tables described above, including ``flarm_decoded``.
   * ``day`` - used by ``flights_data4`` and ``flights_data5``.

   The partition value is the Unix timestamp at the start of the respective hour or day. Without this filter, Trino performs a full table scan across the entire dataset, which is extremely slow and degrades performance for all users. Note that this is now automatically enforced by Trino since upgrading to version 479 and violating queries will be rejected.

   .. code-block:: sql

      -- Correct: partition filter present
      SELECT * FROM state_vectors_data4
      WHERE hour = 1480762800
        AND icao24 = 'a0d724';

      -- WRONG: no partition filter - will scan the entire table
      SELECT * FROM state_vectors_data4
      WHERE icao24 = 'a0d724';

   .. note::
      For ``flights_data4`` and ``flights_data5``, always use ``WHERE day = <unix_day_timestamp>`` instead of ``hour``.
      Filtering on ``time`` alone is **not** sufficient - you must also include the partition column.

**2. Break large queries into smaller chunks.**

   Multiple targeted queries - each covering a short partition range - are faster and less resource-intensive than a single query spanning many days or weeks.

**3. Limit parallel queries.**

   The system is a shared resource. Each user is limited to **two concurrent queries** and **two queued queries**. Global limits also apply; if you receive a queue error, wait and retry.

**4. Avoid long-running queries.**

   The maximum query duration is **30 minutes**, including queuing time. If a query takes more than five minutes, reduce the time frame and/or split it into batches.

**5. Avoid large table scans.**

  If a query gets rejected with **Exceeded scan limit of 100GB**, reduce the time frame and/or split it into batches.

**6. Do not run large global bulk downloads via ad-hoc queries.**

   Downloading all data there is in a given table globally for a week or more is not the purpose of a database interface such as Trino and almost never needed for a research project, which typically focuses on specific areas and/or aircraft. If you truly need many full-day datasets, i.e. complete table snapshots like these examples https://opensky-network.org/data/scientific#d11, contact us for alternative bulk-download solutions. Note that this is truly a very rare need and possible only in very exceptional cases, not for general student work, and may require an extraction fee to cover our time investment.

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

Due to outages, some historical data was permanently lost. Exclude the periods below from your research to ensure accuracy (all times UTC):

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
| 2026-01-02 19:00             | 2026-01-03 18:00             |
+------------------------------+------------------------------+
| 2026-01-24 08:00             | 2026-01-24 17:00             |
+------------------------------+------------------------------+

----

You are now ready to query OpenSky's historical dataset. If you discover anything noteworthy or have suggestions for improving this guide, please reach out to us.
