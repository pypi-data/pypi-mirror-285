*************
History
*************

0.17.0 (2024-07-18)
======================

Major changes:
--------------

- Support `jupyterlab` 4 and `ipywidgets` 8.


0.16.0 (2023-02-22)
======================

Major changes:
--------------

- Dependency to `cosapp` 0.13, following a change in data structure affecting `StructureWidget`.
- Support `occt` 7.6.
- Support `jupyter_server` 2.

**Note:** `ipywidgets` 8 is not supported yet in this version of CoSApp Lab.

Minor changes:
--------------

- Clarify exception handling logic in `module register`.
- Skip tentative pickle dump for non-jsonable objects in `CosappObjectParser`, which used to crash `SysExplorer`.


0.15.5 (2021-09-23)
======================

Major changes:
--------------

- Hook function `add_shape` in `GeometryWidget` and `SysExplorer` replaced by `get_shapes`, with new signature.
  Function `get_shapes` takes a system as sole argument, and returns a list of objects interpretable as OCC shapes.

Minor changes:
--------------

- New option `--open_browser` option in command line interface (`True` by default).
  Setting `--open_browser False` allows one to launch CoSApp Lab standalone mode on headless servers.

- Faster retrieval of recorder data in geometry widget.


0.15.4 (2021-06-25)
======================

Major changes:
--------------

- Support multiple kernels in standalone mode.

Minor changes:
--------------

- Highlight information fluxes in `StructureWidget`.

- New option `--url_prefix` option in command line interface.


0.15.3 (2021-05-17)
======================

Major changes:
----------------

- Backend/frontend implementations of widgets are now moved out of `SysExplorer`, each widget has it own backend and frontend implementation. `SysExplorer` will only import the necessary parts.

- All `SysExplorer` widgets are now also available as Jupyter widgets, user can import these widgets from `cosapp_lab.widgets`, a detailed description about these widgets is available [here](https://cosapp-lab.readthedocs.io/en/latest/lab/extension.html#sysexplorer-widgets-list)

- New widget :

  - *Structure widget* : A widget to show both the hierarchical structure and the connection network of a CoSApp system.
  - *System info widget* : A widget to show the detailed documentation of a CoSApp system and its children.

Minor changes and bug fixes:
-----------------------------

- `SysExplorer` now will start with a default section instead of an empty page.
- Add default template for custom widget code.
- Remove unused id string in custom widget and document widget name.


0.15.2 (2021-03-16)
======================

Changelog:

- Add CoSApp shortcut to start Jupyter Lab in Chrome application mode.
- Add readthedocs configuration.

0.15.0 (2021-03-10)
======================

This patch introduces two major changes to CoSApp Lab:

The JupyterLab widgets is now fully compatible with JupyterLab 3, the support for version 1 and 2 is dropped. User can now install the widgets directly with conda or pip.

A new application mode is added to allow users deploy the CoSApp widgets to a standalone web application. A new CLI tool is also added for managing and deploying the CoSApp module as a web app.

Changelog:

1. The main widget now is **SysExplorer** instead of **ChartViewer**, the old name will be used for a standalone charting widget in the future.  

2. New widget :

 - *Custom widget* : A widget to show the user defined ipywidget, if the javascript part of widget is available on *npm*, the standalone mode can also display the widget.
 - *Connection widget* : A widget to show the connection between sub-systems of current CoSApp system.
 - *Document widget* : A widget to render markdown document, the content of widget can be saved and display in standalone mode.
 - *Data widget* : A widget to visualize the value of variables in ports of system with valid range and limits check.

3. Minor changes and bug fixes:

 - Add syntax highlight to *Chart widget* advanced editor.
 - Use custom plotly build to reduce bundle size.
 - Add restart kernel button to web interface.
 - Auto set range for contourcarpet plot.
 - Add lock/unlock button to enable/disable tab close
 - Improve interface style.
 - Re-render 3D view and graph view  on tab change.
 - Use cookiecutters template from gitlab.com as a submodule.
 - **SysExplorer** save function now overwrites json file instead of incrementing file name.
 - Description of variable is shown in controller.
 - Remove slider in controller for variables without valid ranges or limits.


0.14.0 (2024-01-20)
======================

This patch add three new features to *ChartViewer*:

1. Contour plot : draw the contour lines and filled contours, user needs to configure 3 axes X, Y and Z. The data of all three axes must both be 2-D array with the same shape.
 
2. Advanced trace editor :  a new button allows user to modify directly the trace configuration JSON. 

3. Add axis range configuration: user can fix the axis range in layout configuration dialog.

0.13.0 (2020-12-16)
======================

This patch introduces a new widget *ChartViewer* for *cosapp_lab*, this widget allows users to create the plots with data from a CosApp system. 

*ChartViewer* can be imported from *cosapp_lab*, the required input parameter is an instance or a list of instance of CosApp system.

.. code-block:: python

  from cosapp_lab import ChartViewer
  demo = AnyCosappSystem("demo")
  a = ChartViewer(demo)


A more detailed user guide can be built from *docs* folder with *sphinx*

.. code-block::

  sphinx-build -b html -d _build/doctrees . _build


0.12.0 (2020-09-30)
======================

Feature:

This patch introduces the first client-server communication method for cosapp systems. An instance of cosapp system in local kernel can be shared with external user outside notebook environment via REST api.

Once the server is started with **START SERVER** button, required information to access the server is shown in the log dialog : address of server (**BASE_URL**) and user access token (**USER_TOKEN**). Other user need to have these information in order to connect to current CosApp instance.

There are two APIs for interacting with a system:

Get system information

* Method : *POST* 
* Address : *BASE_URL/cosapp/server/info*
* Request body :*{"token": USER_TOKEN}* 
* Success response : *{"children_list": List, "children_port" : Dict, "children_drive" : Dict}* 
* Error response : -1 

Run system with new parameters

* Method : *POST* 
* Address : *BASE_URL/cosapp/server/run* 
* Request body : *{"token": USER_TOKEN, "data" :{"parameters" : Dict, "result" : List}}*  
* Success response : *{"error": None, "result" : Dict, "log" : string}*
* Error response : *{"error": List", "result" : None, "log" : None}*

0.11.0 (2020-07-22)
======================

Feature:

This patch introduces a new tab for *System architecture* panel. This panel is now contains 3 views:

* **Tree view** : This panel shows the structure of systems in tree graph, uses can filter a selections of nodes to show in the 2 other views.
* **PBS view**: this tab shows the structure of system in the from of hierarchy diagram, with 2 layout possible : flat layout and radial layout.
* **Connection view** this tab show the connections between the the ports of all systems, the position of nodes in this tab is synchronized with the nodes in **PBS View**

Bugs and code quality:

* Fix bug in *Dashboard panel* when a slider is initialized with very small starting value.

0.10.7 (2020-06-10)
======================

- Update threejs and react-diagram to latest version.

0.10.6 (2020-05-12)
======================

Feature:

* Points and vectors now can be drawn in the 3D viewer by defining the related data in the *shape* variable of a *GeometryPort*.Now *GeometryPort.shape* can be a OCC shape, list of OCC shape or a dict with following format:

.. code-block:: python

  {
    "shape" : Union[TopoDS_Shape, List[TopoDS_Shape]], # the shapes to be drawn in viewer
    "color" : Optional[str] # Color of the shapes, default value is 0x156289
    "transparent" : Optional[bool] # Transparent of shapes, default is False
    "edge" : Optional[bool] # Show or hide edge shape, default is False
    "misc_data" : Optional[{
                    "points": Optional[List[{"position": Iterable[float],
                                            "color": Optional[Union[str,int]], # default value is yellow
                                            "radius": Optional[float] # default value is 0.1
                                            }]],
                    "vectors": Optional[List[{"position": Iterable[float],
                                              "direction": Iterable[float]
                                              "color": Optional[Union[str,int]], # default value is 0x3900f2
                                            }]],
                  }] # data to draw point and vector in the viewer
  }


Bugs and code quality:

* Update pyoccad version from 1.10.0dev to 0.3.0rc1

0.10.5
======================


- Fix some bugs on the widgets
- Add Jest tests on frontend code.

0.10.4
======================

- Introduce SysExplorer and GeometryViewer

0.10.3
======================

- sysplot integration

0.10.2
======================

- Correct unit no more present in column name
- Correct filtering on reference value

0.10.1
======================

- _Reference_ is now a classical column in the DataframeRecorder.

0.10.0
======================

- Python compatible with cosapp 0.10.0

0.9.2
======================

- Port to Jupyterlab v1

0.9.0
======================

- First version as a separate package
