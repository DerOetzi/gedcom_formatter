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
        print('    edge [dir = none, penwidth = 3.0]')
        print()

        nextGeneration = self.__tree.getRootGeneration()
        while nextGeneration:
            generation = []
            nextSibling = nextGeneration.getPrevSibling()
            while nextSibling:
                generation.append(nextSibling.getId())
                nextSibling = nextSibling.getNextSibling()

            print('    {rank = same; %s [style = invis, len=10, weight=1];};' % ' -> '.join(generation))

            if nextGeneration.hasChilds():
                nextGeneration = nextGeneration.getChilds()[0]
            else:
                break

            print()

        family = self.__tree.getRootFamily()
        self.__renderFamily(family)
     
        for individual in self.__tree.getIndividuals():
            id = individual.getId()
            gedcom = individual.getGedcom()
            label = '{}\\n{}\\n{}'.format(gedcom.getCallname(), gedcom.getBirthname(), gedcom.getBirthdate())
            print('    {id} [shape = doubleoctagon, label="{label}", penwidth=2.0];'.format(id = id, label = label))

            if individual.isChild():
                print('    {id}Child [shape = circle, label="", height = 0.0, width = 0.0];'.format(id = id))
                print('    {id}Child -> {id} [len = 0.25, weight=100];'.format(id = id))
            
            print()

        print('}')

    def __renderFamily(self, family):
        id = family.getId()
        partners = family.getPartners()
        print('    {rank = same; %s -> %s -> %s [len = 0.5, weight=100];};' % (partners[0].getId(), id, partners[1].getId()))
        print('    {id} [shape = circle, label = "", height = 0.0, width = 0.0];'.format(id = id))

        if family.hasChilds():
            childs = family.getChilds()
            childsIds = list(map(lambda x: x.getId(), childs))

            childNode = '%sChilds' % id                

            print('    {rank=same; %s;}' % ('; '.join(childsIds)))
            print('    {} -> {} [len = 0.5, weight = 80];'.format(id, childNode))
            print('    {} [shape = circle, label = "", height = 0.0, width = 0.0];'.format(childNode))

            print()

            for child in childs:
                print('    {} -> {} [len = 2, weight = 60];'.format(childNode, child.getId() + 'Child'))

                for childFamily in child.getFamilies():
                    self.__renderFamily(childFamily)

        print()
