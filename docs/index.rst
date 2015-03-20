Seth User Documentation
================================

**Seth** is a set of utilities for working with Pyramid framework. It provides
components such as: class-based-views, pagination, custom renderers, uploading utility,
command utility, filtering utility and couple of tweens. To install run:

.. code-block:: console

    $ pip install -U seth

Seth's components also have some additional dependencies

1. Pdf renderer requires **xhtml2pdf** and for instance **pyramid_jinja2** to work properly:

.. code-block:: console

    $ pip install -U xhtml2pdf==0.0.5 && pip install -U reportlab==2.7 && pip install -U pyramid_jinja2==2.3.3

2. You may want to replace marshmallow with colander, so:

.. code-block:: console

    $ pip install -U colander

:doc:`tutorial`
  A quick **Seth** tutorial & overview.


:doc:`api`
  The complete API documentation.


.. toctree::
    :maxdepth: 1
    :numbered:
    :hidden:

    tutorial
    api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

