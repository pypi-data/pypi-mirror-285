====================
PBS widget
====================

PBS widget is a CoSApp Lab widget allowing users to visualize the structure of CosApp system. Users can use PBS widget in notebook as a JupyterLab widget or use it in **SysExplorer**.

---------------------
Start PBS widget 
---------------------

To open **PBSWidget** inside **SysExplorer**, just select *PBS widget* in widget menu of any section. 

To use **PBSWidget** as a JupyterLab widget, users can import it from *cosapp_lab.widgets*, the required input parameter is an instance of CosApp system. In default mode, **PBSWidget** will be displayed as a notebook output, to modify the position of widget, user can user *anchor* keyword as **SysExplorer** widget.

.. code-block:: python  

    from cosapp_lab.widgets import PBSWidget
    demo = AnyCosappSystem("demo")
    a = PBSWidget(demo, anchor = "tab-after")


------------------------------
PBS widget main interface
------------------------------

**PBSWidget** contains a graph of CoSApp system structure. Users can change the layout of graph by using 2 buttons in the toolbar for *Flat layout* or *radial layout*

.. image:: ../img/Pbs_widget_main.png
   :width: 100%   




