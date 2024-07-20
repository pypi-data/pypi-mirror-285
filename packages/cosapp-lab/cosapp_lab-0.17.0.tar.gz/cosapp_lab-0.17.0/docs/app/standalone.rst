==================================
CoSApp Lab command-line interface
==================================

CoSApp Lab is shipped with a CLI tool *cosapp*. It brings project template, standalone interface management and deployment to terminal.

--------------------------------
Initialize a new CosApp project 
--------------------------------

.. code-block:: shell  

    cosapp init

This command allows users to create a new CoSApp project by using cookiecutter template from https://gitlab.com/cosapp/cosapp-utils/cookiecutter-cosapp-workspace 

--------------------------------
Standalone dashboard management 
--------------------------------

With CoSApp Lab, users can create a dashboard for existing CoSApp library and deploy it as a standalone web application. Suppose that users already created a CoSApp library by using *cosapp init* command and completed the implementation of library. This section will detail the process of adding a standalone dashboard into it. 


Create dashboard in notebook
=============================

Say our library is named **cosapp_demo**, and the main system from which we want to create a dashboard is of type **DemoSystem**.

The first step is to :doc:`create a dashboard <../lab/extension>` with **SysExplorer** in JupyterLab. The code to start **SysExplorer** in notebook for our system is:

.. code-block:: python  

    from cosapp_lab.widgets import SysExplorer
    from cosapp_demo.systems import DemoSystem

    system = DemoSystem("demo")
    app = SysExplorer(system)

Once the dashboard layout is finished, we save it into a *json* configuration file by using the save button in the **SysExplorer** window. Next, copy or move the *json* configuration file into the **resources** folder of **cosapp_demo** library. 

Configure your library for CoSApp Lab
=======================================

We now have to implement two hook functions inside the top level *__init__.py* file of **cosapp_demo**:

* **_cosapp_lab_load_module** : this function is called by CoSApp Lab to start the dashboard, so it typically contains the code we used in notebook to start **SysExplorer**. Since we want to load the configuration from the **resources** folder, we will use function **find_resources**, normally already included in the *__init__.py* file of your project.

The implementation for our example is:

.. code-block:: python  

    # file cosapp_demo/__init__.py
    ....

    def _cosapp_lab_load_module() -> None:
        from cosapp_lab.widgets import SysExplorer
        from cosapp_demo.systems import DemoSystem
        system = DemoSystem("demo")
        # Add drivers, or do any kind of pre-processing on your system
        SysExplorer(system, template = find_resources("name_of_configuration_file.json"))

    ...

* **_cosapp_lab_module_meta** :  CoSApp Lab will call this function to get metadata of dashboard. It must return a dictionary with keys:

    - 'title' : Title of dashboard, as will appear in top bar of dashboard interface.
    - 'version': Version of dashboard
    - 'description': A short description of dashboard; it will be shown in library page.

The implementation for our example is:

.. code-block:: python  

    # file cosapp_demo/__init__.py
    ....

    def _cosapp_lab_module_meta() -> Dict:
        return {"title": "A CoSApp project ", "description": "A CoSApp demo project for CoSApp Lab", "version": "0.1.0"}
    
    ...

Your dashboard is now ready to be registered as a standalone application!

Register dashboard to CoSApp Lab
====================================

*cosapp* command has a sub-command *module* to manage the dashboard.

* To register our **cosapp_demo** to CoSApp Lab:

.. code-block:: shell  

    cosapp module register cosapp_demo

output is:

.. code-block:: shell  

    cosapp_demo is successfully registered as CoSApp standalone module

* To get the list of registered dashboards:

.. code-block:: shell  

    cosapp module list

output is:

.. code-block:: shell  

    cosapp_demo v0.1.0 - A CoSApp demo project for CoSApp Lab

* To remove **cosapp_demo** from registered list:

.. code-block:: shell  

    cosapp module remove cosapp_demo

output is:

.. code-block:: shell  

    cosapp_project is successfully removed from standalone module list

Now our dashboard is ready to use.

Start dashboard from CoSApp Lab
====================================

*cosapp* command has a sub-command *load* start one or several dashboards.

* To start **cosapp_demo** dashboard:

.. code-block:: shell  

    cosapp load cosapp_demo

CoSApp web server will be started and the application is server at URL *http://127.0.0.1:6789*. We can use a specific port, with the *--port* option:

.. code-block:: shell  

    cosapp load cosapp_demo --port 8888

* To start CoSApp Lab dashboard library:

.. code-block:: shell  

    cosapp load -a

Library page is available at *http://127.0.0.1:6789*

.. image:: ../img/cosapp_lab_all.gif
    :width: 800
