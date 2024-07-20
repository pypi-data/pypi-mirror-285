====================
Connection widget
====================

Connection widget is a CoSApp Lab widget allowing users to visualize the connection between ports of CosApp system. Users can use Connection widget in notebook as a JupyterLab widget or use it in **SysExplorer**.

-----------------------
Start Connection widget 
-----------------------

To open **ConnectionWidget** inside **SysExplorer**, just select *Connection widget* in widget menu of any section. 

To use **ConnectionWidget** as a JupyterLab widget, users can import it from *cosapp_lab.widgets*, the required input parameter is an instance of CosApp system. In default mode, **ConnectionWidget** will be displayed as a notebook output, to modify the position of widget, user can user *anchor* keyword as **SysExplorer** widget.

.. code-block:: python  

    from cosapp_lab.widgets import ConnectionWidget
    demo = AnyCosappSystem("demo")
    a = ConnectionWidget(demo, anchor = "tab-after")


--------------------------------
Connection widget main interface
--------------------------------

**ConnectionWidget** contains a graph of connections in CoSApp system. 

.. image:: ../img/Connection_widget_main.png
   :width: 100%   




