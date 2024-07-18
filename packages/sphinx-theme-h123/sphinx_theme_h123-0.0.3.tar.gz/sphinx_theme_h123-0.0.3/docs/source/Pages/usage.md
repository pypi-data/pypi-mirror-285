
# Usage

sphinx-theme-h123 is a static theme with a python script bundled. The usage should be straightforward.

## Foldable navtree

The content of sidebar navtree is generated from the sphinx's toctree. Use `toctree::` directive to detect files.

```rst
..  toctree::
    :maxdepth: 1
    :titlesonly:

    page1.md
    page2.md
    page3.md
```

A document usually contains one or more subsections. This toctree cache (a tree-structured information) will show up in the sidebar navtree. A document can contain another toctree directive (nested toctree). This toctree will be merged to the parent toctree.

Typical options for the navtrees are: `numbered`, `titlesonly` and `caption`. For more details, check this page: [](./usage_nav.md)











```{toctree}
:hidden:

usage_nav.md
usage_myst.md
```
