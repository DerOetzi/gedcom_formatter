# gedcom_formatter

Resize all pictures in Media directory to maximal 768x768

```
convert '*.png[768x768]' -set filename:base "%[basename]" "%[filename:base].png"
convert '*.jpg[768x768]' -set filename:base "%[basename]" "%[filename:base].jpg"
convert '*.JPG[768x768]' -set filename:base "%[basename]" "%[filename:base].JPG"
```

Run with GEDCOM File with ID of family and convert to svg.

```
python3 -m gedcom_formatter -r <FAMILY_ID> -d 5 --graphviz tree.ged
dot -Tsvg family_tree.gv > tree.svg
```
