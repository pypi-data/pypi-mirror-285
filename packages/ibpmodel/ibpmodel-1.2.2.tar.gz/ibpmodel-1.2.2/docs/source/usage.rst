Usage
=====

Calculation of IBP Index
------------------------

To calculate the IBP index use :py:func:`ibpmodel.ibpforward.calculateIBPindex()` function. It returns a pandas.DataFrame:

.. runblock:: pycon

   >>> from ibpmodel import calculateIBPindex
   >>> calculateIBPindex(day_month=15, longitude=0, local_time=20.9, f107=150)                           

.. runblock:: pycon

   >>> from ibpmodel import calculateIBPindex
   >>> calculateIBPindex(day_month=['Jan','Feb','Mar'], local_time=22)

.. runblock:: pycon

   >>> from ibpmodel import calculateIBPindex
   >>> calculateIBPindex(day_month=[1,15,31], longitude=[-170,175,170], local_time=0, f107=120)


Read coefficient file
---------------------

You can load the coefficient file. :py:func:`ibpmodel.ibpcalc.read_model_file()`:

.. runblock:: pycon

   >>> from ibpmodel import read_model_file
   >>> c = read_model_file()
   >>> c.keys()

   >>> c['Intensity']


Plotting of the probability
---------------------------

There are two functions to plot IBP index. function :py:func:`ibpmodel.ibpforward.plotIBPindex()` and :py:func:`ibpmodel.ibpforward.plotButterflyData()`.
By default, the plot is displayed immediately. If you want to make changes or additions, the parameter getFig must be set equal to ``True``. 
Then you get matplat.axis as return value:

.. code-block:: python
   
   >>> import ibpmodel as ibp
   >>> ibp.plotIBPindex(doy=349)

.. image:: _static/example_plotIBP.png
   :alt: Contour plot of the IBP index for the given day
   :align: center
.. code-block:: python

   >>> ibp.plotButterflyData(f107=150)

.. image:: _static/example_plotButterfly.png
   :alt: Contour plot of result from function ButterflyData() 
   :align: center

.. code-block:: python
   
   >>> import ibpmodel as ibp
   >>> import matplotlib.pyplot as plt
   >>> doys = [349, 15]
   >>> fig, axes = plt.subplots(len(doys),1, layout='constrained',figsize=(9, 7))
   >>> for d, ax in zip(doys, axes):
   ...     ax, scalarmap = ibp.plotIBPindex(d, ax=ax)
   >>> ibp.ibpforward.setcolorbar(scalarmap, fig, axes, fraction=0.05)
   >>> plt.show()

.. image:: _static/example_subplot.png
   :alt: Subplot of IBP index
   :align: center
   