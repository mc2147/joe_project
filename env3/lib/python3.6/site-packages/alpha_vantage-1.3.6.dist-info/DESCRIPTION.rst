alpha\_vantage
==============

*Python module to get stock data from the Alpha Vantage API*

Alpha Vantage delivers a free API for real time financial data and most
used finance indicators in a simple json format. This module implements
a python interface to the free API provided by Alpha Vantage
(http://www.alphavantage.co/). It requires a free API, that can be
requested on http://www.alphavantage.co/support/#api-key.

Install
-------

To install the package use:

.. code:: shell

    pip install alpha_vantage

If you want to install from source, then use:

.. code:: shell

    git clone https://github.com/RomelTorres/alpha_vantage.git
    pip install -e alpha_vantage

Usage
-----

To get data in a python, simply import the library and call the object
with your api key and get ready for some awesome free realtime finance
data.

.. code:: python

    from alpha_vantage.timeseries import TimesSeries
    ts = TimesSeries(key='YOUR_API_KEY')
    # Get json object with the intraday data and another with  the call's metadata
    data, meta_data = ts.get_intraday('GOOGL')

Internally there is a retries counter, that can be used to minimize
connection errors (in case that the api is not able to respond in time),
the default is set to 5 but can be increased or decreased whenever
needed.

.. code:: python

    ts = TimesSeries(key='YOUR_API_KEY',retries='YOUR_RETRIES')

Finally the library supports giving its results as json dictionaries
(default) or as pandas dataframe, simply pass the parameter
output\_format='pandas' to change the format of the output for all the
api calls.

.. code:: python

    ts = TimesSeries(key='YOUR_API_KEY',output_format='pandas')

Plotting
--------

Using pandas support we can plot the intra-minute value for 'MSFT' stock
quite easily:

.. code:: python

    from alpha_vantage.timeseries import TimesSeries
    import matplotlib.pyplot as plt

    ts = TimesSeries(key='YOUR_API_KEY', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    data['close'].plot()
    plt.title('Intraday Times Series for the MSFT stock (1 min)')
    plt.show()

Giving us as output: |alt text|

The same way we can get pandas to plot technical indicators like
Bolliger Bands®

.. code:: python

    from alpha_vantage.techindicators import TechIndicators
    import matplotlib.pyplot as plt

    ti = TechIndicators(key='YOUR_API_KEY', output_format='pandas')
    data, meta_data = ti.get_bbands(symbol='MSFT', interval='60min', time_period=60)
    data.plot()
    plt.title('BBbands indicator for  MSFT stock (60 min)')
    plt.show()

Giving us as output: |alt text|

Finally we can also plot sector performance just as easy:

.. code:: python

    from alpha_vantage.sectorperformance import SectorPerformances
    import matplotlib.pyplot as plt

    sp = SectorPerformances(key='YOUR_API_KEY', output_format='pandas')
    data, meta_data = sp.get_sector()
    data['Rank A: Real-Time Performance'].plot(kind='bar')
    plt.title('Real Time Performance (%) per Sector')
    plt.tight_layout()
    plt.grid()
    plt.show()

Giving us as output: |alt text|

Tests
-----

In order to run the tests you have to first export your API key so that
the test can use it to run.

.. code:: shell

    export API_KEY=YOUR_API_KEY
    cd alpha_vantage
    nosetests

Documentation
-------------

To find out more about the available api calls, visit the alpha-vantage
documentation at http://www.alphavantage.co/documentation/


.. |alt text| image:: images/docs_ts_msft_example.png?raw=True
.. |alt text| image:: images/docs_ti_msft_example.png?raw=True
.. |alt text| image:: images/docs_sp_rt_example.png?raw=True


