## Qt app

![](./assets/qt_example_app.png)

_A small qt app to demonstrate the usage of Pyscriptpacker_

---

Here is a simple qt app, using Pyscriptpacker to pack a custom [:octicons-file-code-24: widget library](https://github.com/3dninjas/pyscriptpacker) (`my_lib`) and then use it as a separate module for other projects.  

Packer command line:

``` console
$ pyscriptpacker -c custom_widgets ./unpacked ./packed/my_lib.py
```

## Blender addon

![](./assets/blender_example_addon.png)

_Blender addon using Pyscriptpacker for packing into a zip file_

---

Here is a simple example, using Pyscriptpacker to pack this blender [:octicons-file-code-24: example addon](https://github.com/3dninjas/pyscriptpacker). 

Packer command line:

``` console
$ pyscriptpacker -m ./unpacked/__init__.py addon ./unpacked ./example_addon/__init__.py
```

In this example, we use a flag `-m main_file, --main=main_file` which helps the user to determine the main script (the ==highlight== part in the above codes) which need to be executed when import that module, also a requirement for addon to be regconized by Blender (*bl_info* in `__init__.py`).

**Pyscriptpacker** will go through all the files in the module and add the source codes into the _**virtual_module**_ variable, then use the custom loader whenever we call to the packed file.
