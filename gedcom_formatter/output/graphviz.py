from math import ceil
from ..tree import FamilyTree, Node

class Graphviz():
    def __init__(self, tree: FamilyTree):
        self.__tree = tree
        self.__childsNodeLayers = {}

    def render(self):
        self.__childsNodeLayers.clear()

        print('Digraph family_tree {')
        print('    engine = neato')
        print('    splines = line')
        print('    center = true')
        #print('    rankdir = BT')
        print('    edge [dir = none, penwidth = 3.0]')
        print()

        nextGeneration = self.__tree.getRootGeneration()
        while nextGeneration is not None:
            generation = list(map(lambda x: x.getId(), nextGeneration.getIndividuals()))
            
            if len(generation) > 1:
                print('    {rank = same; %s [style = invis];};' % ' -> '.join(generation))

            nextGeneration = nextGeneration.getNextGeneration()

            print()

        family = self.__tree.getRootFamily()
        self.__renderFamily(family)
     
        for individual in self.__tree.getIndividuals():
            id = individual.getId()
            label = self.__renderLabel(individual)
            print('    {id} [shape = doubleoctagon,'.format(id = id)) 
            print('          label={label},'.format(label = label))
            print('          width=3.5, height=1.5,') 
            print('          penwidth=2.0, style = filled, fillcolor = antiquewhite];')

            if individual.isChild():
                print('    {id}Child [shape = circle, label="", height = 0.0, width = 0.0];'.format(id = id))
                print('    {id}Child -> {id} [len = 0.25, weight=10];'.format(id = id))
            
            print()

        print('}')

    def __renderLabel(self, individual):
        gedcom = individual.getGedcom()

        label = '<<table border="0" cellborder="0">'

        if individual.isMale():
            imgSrc = './male.png'
        else:
            imgSrc = './female.png'

        label += '<tr><td><img src="%s"/></td></tr>' % imgSrc
        label += '<tr><td>%s</td></tr>' % gedcom.getCallname()
        label += '<tr><td>%s</td></tr>' % gedcom.getBirthname()
        label += '<tr><td>%s</td></tr>' % gedcom.getBirthdate()
        label += '</table>>'

        return label

    def __renderFamily(self, family):
        id = family.getId()
        partners = family.getPartners()
        print('    subgraph Family%s {' % id) 
        print('    {rank = same; %s -> %s -> %s [len = 0.5, weight=10];};' % (partners[0].getId(), id, partners[1].getId()))
        print('    {id} [shape = circle, label = "", height = 0.0, width = 0.0];'.format(id = id))

        if family.hasChilds():
            childs = family.getChilds()
            childsIds = list(map(lambda x: x.getId(), childs))

            childNode = '%sChilds' % id                

            print('    {rank=same; %s;}' % ('; '.join(childsIds)))
            print('    {} -> {} [len = 0.5, weight = 10];'.format(id, childNode))
            print('    {} [shape = circle, label = "", height = 0.0, width = 0.0];'.format(childNode))

            print()

            for child in childs:
                print('    {} -> {} [len = 2, weight = 6];'.format(childNode, child.getId() + 'Child'))

                for childFamily in child.getFamilies():
                    self.__renderFamily(childFamily)

        print('}')
        print()
