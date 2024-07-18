
# Usage - NavTree

```rst
..  toctree::
    :caption: Index
    :maxdepth: 1
    :titlesonly:
    :numbered:

    page1.md
    page2.md
    page3.md
```

## Directives

**caption (Text)**

Set the title of the toctree. Title is printed above the toc (both page and navtree).

**numbered**

Add chapter numbers to each section.

**titlesonly**

For each subdocuments, only the top level header is included in the toctree, and all subsections are ignored. 

Set this flag if you prefer simpler navtree (no subsections listed!). Don't set this flag if you want a complete list of headers.

The `:titlesonly:` option must be used with care. When this option is set, The navtree becomes simple and looks better, but you will lose the complete toctree info. It also have the risk of having clumsy navtree. The nested toctrees inside the subsections are still discovered and merged to the parent. Avoid parent toctree with `:titlesonly:` + nested toctree directive in subsection. 

**maxdepth (N)**

Limits the toctree depth printed in the page. This value is ignored in the navtree. Check theme variable `h123_navtree_maxdepth` for that purpose.

**hidden**

Hides this toctree from the page. This flag is ignored in the navtree.


**etc**

See [official documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree) for more. 


## Multiple TocTree

By defining toctree multiple times, all contents are added to the sidebar navtree. 

Although this is useful, multiple toctree results in strage output when you use non-HTML output. 