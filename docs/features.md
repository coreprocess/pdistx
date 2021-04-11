**Pyscriptpacker** provide the following:

## Single file distribution

Pyscriptpacker will go through all the source files within the requested module and pack them into a single file. The user can place the file anywhere, under any module and the result file still work pretty well thanks to **our custom loader code**.

You can take a look at some examples in [here](/example).

## Extending the libraries

You can also pack external Python modules to your packed file as well by installing it in your Python environment and then provide the **site-packages** path to the Pyscriptpacker.

For example:

``` console
$ pip install pyscriptpacker, toposort
$ pyscriptpacker toposort <path_to_site-packages> output.py
```

Another way to do this without installing the external package manually is to use the `-k` and the `-p` flags.

``` console
$ pip install pyscriptpacker
$ pyscriptpacker -k toposort -p <python_path> toposort ..... output.py
```

**Pyscriptpacker** will automatically create a temporary virtual environment and install the desired packages (identify with `-k` flag) to that virtual environment, it also add the **site-packages** path of that environment to the search path when Pyscriptpacker trying to find the module to pack.

The `-p python_path, --python=python_path` is an optional way to tell **Pyscriptpacker** use custom python path as the interpreter which virtual environment is created based on.

!!! note
    If the user does not define the `-p python_path`, Pyscriptpacker will use the default python path in the current environment (`sys.executable`).

## Compressing & Minifying

Pyscriptpacker does have an option to compress the source code using the [bz2](https://docs.python.org/3/library/bz2.html) method, so it will add a security layer to your source file and still can be imported as module and working correctly.

Take the above **toposort** module source code as an example, here is the packing result from Pyscriptpacker with and without the compression option.

`-c, --compress`

`-i, --minify`
:   Furthermore, Pyscriptpacker does implement the **pyminifier** package's functionality to help minify the source code. See [here](https://github.com/liftoff/pyminifier) for more information about pyminifier package.

## Zipping output

`-z zip_file, --zip=zip_file`  and `-r path, --resources=path,...`

These two options allow Pyscriptpacker instead of just output into a single file, it will add the result file into the desired zip file and also includes all the resource files/folders (if any).

Moreover, the resource flag does have a support for custom path, where PyscriptPacker will structure the resource file as you wish by using color `:` as an annotation and then define your custom path.

For example:

=== "-r README.md:Folder/README.md"
    ```
    zip_file.zip
    ├─ Folder/
    │  └─ README.md
    └─ other_file.py
    ```
=== "-r README.md"
    ```
    zip_file.zip
    ├─ README.md
    └─ other_file.py
    ```
