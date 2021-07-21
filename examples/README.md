# Examples

## Blender Addon

```sh
# vendor packages
pvendor examples/blender_addon/vendor

# generate PRO as zip
pvariant \
    -d __VARIANT__=PRO                 \
    -f '**/free.bip'                   \
    -z $HOME/Desktop/blender_addon.zip \
    examples/blender_addon             \
    blender_addon

# generate FREE as folder
pvariant \
    -d __VARIANT__=FREE    \
    -f '**/pro.bip'        \
    examples/blender_addon \
    $HOME/.config/blender/2.93/scripts/addons/blender_addon
```

## QT App

```sh
# vendor packages
pvendor examples/qt_app/vendor

```
