# Pretty Print

## Usage

```Python
import pretty_print_dmeurer as pp
pp.color_demo()
pp.text_demo()

print(f"{pp.Colors.BG.aqua_bright}Hello World{pp.reset}")
```


## Build 

```PowerShell
py -m build
py -m twine upload --repository pypi dist/*
```
