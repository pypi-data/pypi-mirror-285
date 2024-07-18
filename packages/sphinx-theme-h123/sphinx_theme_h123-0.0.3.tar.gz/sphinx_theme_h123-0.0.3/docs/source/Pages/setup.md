# Setup

## Instruction

Install the theme and its dependencies.

**Requirements**

    Python > 3.8

Install sphinx and the theme

```sh
python -m pip install sphinx
python -m pip install sphinx_theme_h123
```

Create the new project

```sh
sphinx-quickstart .
```

Edit conf.py

```py
# conf.py
html_theme = 'sphinx_theme_h123'  #changed
```

Add theme package to the extensions list

```py
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'myst_parser',
    'sphinx_theme_h123',   # this
]
```

## Recommended Tools

### build automation

```sh
python -m pip install sphinx-autobuild
```

run, then open the browser (defaults to localhost:8000)

```sh
sphinx-autobuild -E <source> <build/html>
# -E: fresh build (no-cache)
```


### markdown

Install the markdown parser, and add to the extensions list.


```sh
# markdown parser
python -m pip install myst_parser
```

```py
extensions = [
    'myst_parser',          # this
]
```

### mathjax

(TBD)

Edit conf.py to set `mathjax_path` to the javascript URL. 

```py
#conf.py
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
```

Download the javascript for local distribution. For offline environment, you might need to use `file://` URL.

```py
pip install sphinx-mathjax-offline
```