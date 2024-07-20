====================
Geometry widget
====================

Geometry widget is a CoSApp Lab widget allowing users to visualize Opencascade shape objects inside CoSApp system. Users can use geometry widget in notebook as a JupyterLab widget or use it in **SysExplorer**.

---------------------
Start geometry widget 
---------------------

To open **GeometryWidget** inside **SysExplorer**, just select *Geometry widget* in widget menu of any section. 

To use **GeometryWidget** as a JupyterLab widget, users can be import it from *cosapp_lab.widgets*, the required input parameter is an instance of CoSApp system.

By default, **GeometryWidget** will be opened on a side panel of JupyterLab interface, to modify position of widget, user can user *anchor* keyword as **SysExplorer** widget.

.. code-block:: python  

    from cosapp_lab.widgets import GeometryWidget
    demo = AnyCosappSystem("demo")
    a = GeometryWidget(demo, anchor = "tab-after")

* **Default method to extract OCC shape from system**: **GeometryWidget** will search for all ports named *GeometryPort* inside the CoSApp system to get shapes, this port need to contain 2 variable *visible* and *shape*. A typical implementation of *GeometryPort* is:

.. code-block:: python  

   from cosapp.ports import Port 
   class GeometryPort(Port):
      def setup(self):
         self.add_variable("visible", True, desc="Should this geometry be shown?")
         self.add_variable("shape", None, desc="Geometrical object")

The *shape* variable of *GeometryPort* can be a OCC shape, list of OCC shape or a dict with following format:

.. code-block:: python

  {
    "shape" : Union[TopoDS_Shape, List[TopoDS_Shape]], # shapes to be drawn in viewer
    "color" : Optional[str] # Color of shapes, default value is 0x156289
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

Points and vectors can be drawn in *GeometryViewer* by defining the related data in *misc_data* key of  *GeometryPort.shape*.

In this default mode, **GeometryWidget** will save the geometry of system in each time step, so user does not need to specify a recorder to store the geometry. In order to capture all data, **GeometryWidget** need to be started before running drivers.


* **User defined method to extract OCC shape from system**: If CoSApp system does not use *GeometryPort*, user needs to defined a method to extract shapes from system by passing a function reference to *get_shapes* parameter of **GeometryWidget** constructor. The custom add shape function needs to satisfy 2 requirements:

1. It takes a CoSApp system as single input parameter. 
2. It returns a list of shape data (*TopoDS_Shape*, list of *TopoDS_Shape* or a dictionary). 

A typical implementation of this function looks like this:

.. code-block:: python

  def custom_get_shapes(system: System) -> List[Any]:
      """Custom `get_shapes` function collecting geometric
      data throughout `system`, from output ports of type
      `CustomGeometryPort`.
      """
      output = []
      criterion = lambda port: isinstance(port, CustomGeometryPort)

      # Recursive loop over entire sub-system tree
      # using method `system.tree()`
      for elem in system.tree():
          for port in filter(criterion, elem.outputs.values()):
              output.append(port.custom_port_variable)
      
      return output

  from cosapp_lab.widgets import GeometryWidget

  demo = AnyCosappSystem("demo")
  widget = GeometryWidget(demo, get_shapes=custom_get_shapes)

In this mode **GeometryWidget** still needs to be started before running any driver.

* **Get shape data from recorder**: if shape data is already stored in a recorder, user can specify *source* parameter of **GeometryWidget** constructor in order to get shape from recorder instead of system variable. In this mode, **GeometryWidget** can be started after running drivers. The format of data for *source* parameter is following:

.. code-block:: python  

    from cosapp_lab.widgets import GeometryWidget
    demo = AnyCosappSystem("demo")
    a = GeometryWidget(demo, source = {"recorder": "solver", "variables": ["mass.dyn.geom.shape","arm.dyn.geom.shape"]})

Here *recorder* key is path to the solver which holds the recorder, this path is defined by concatenating contextual name of system with driver name, for example: *system_1.system_2...system_n.driver_name*. The *variables* key is the column of recorder which holds shape data.


To open **GeometryWidget** inside **SysExplorer**, just select *Geometry widget* in widget menu of any section, to use a customized *get_shapes*  function or using recorder data with **SysExplorer**, user can use the same method as **GeometryWidget**

------------------------------
Geometry widget main interface
------------------------------

*GeometryViewer* contains a large viewer window and a toolbar at the bottom of widget.

.. image:: ../img/Geometry_widget_main.png
   :width: 100%   

Toolbar
=====================

The toolbar at the bottom of interface contains selectors and buttons to configure the viewer window.

* **Camera mode selector**: Switch camera view between 2D/3D mode (default is 3D).

* **Vertical direction**: Set the vertical direction of viewer to one of 3 axis X, Y, Z (default is Z).

* **Time step**: For transient simulation, geometry of each time step is stored and can be accessed by this selector.

* **Animation control**: Button to start/stop animation.
