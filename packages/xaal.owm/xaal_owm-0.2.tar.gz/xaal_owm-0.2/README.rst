xaal.owm
========
This package is a OpenWeatherMap gateway for xAAL. It provides a way to get weather information from OpenWeatherMap and send it to xAAL network.


Config & Run
------------
Edit the configuration file `owm.ini` to set your OpenWeatherMap API key and the city you want to get weather information from.

.. code-block:: ini

    [config]
    api_key   = xxxx
    place     = "Brest,FR"
    temperature   = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    humidity      = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    pressure      = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
