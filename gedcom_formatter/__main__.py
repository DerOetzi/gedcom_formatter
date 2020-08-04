import click
from gedcom_formatter.gedcom.model import Gedcom
from gedcom_formatter.tree import FamilyTree
from gedcom_formatter.output.graphviz import Graphviz

@click.command()
@click.option(
    '--info', 
    'format', 
    flag_value = 'info', 
    help = 'Outputs the information about Gedcom content', 
    default = True
)
@click.option(
    '--graphviz', 
    'format', 
    flag_value = 'graphviz',
    help = 'Outputs dot-Format for graphviz'
)
@click.option(
    '--root',
    '-r',
    required = True,
    help = 'Define the family which is root of tree FXX'
)
@click.option(
    '--depth',
    '-d',
    required = False,
    type = int,
    default = 1,
    help = 'Maximal depth of generations'
)
@click.argument("filename", type = click.Path(exists = True))
def cli(**kwargs):
    _cli_internal(**kwargs)

def _cli_internal(filename, format, root, depth):
    gedcom = Gedcom()
    gedcom.parseFile(filename)

    tree = FamilyTree(gedcom)
    tree.build(root, depth)

    if format == 'info':
        print(tree)
    elif format == 'graphviz':
        renderer = Graphviz(tree)
        renderer.render()

cli(prog_name='python3 -m gedcom_formatter')