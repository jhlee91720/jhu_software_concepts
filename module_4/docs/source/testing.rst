Testing Guide
=============

Run marked tests
----------------

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

Markers
-------

- ``web``: page load and HTML structure tests
- ``buttons``: endpoint behavior and busy-state handling
- ``analysis``: answer labels and percentage formatting
- ``db``: schema/inserts/select checks
- ``integration``: end-to-end flows
