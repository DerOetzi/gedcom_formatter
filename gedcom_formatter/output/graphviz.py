from math import ceil
from ..tree import FamilyTree

class Graphviz():
    def __init__(self, tree: FamilyTree):
        self.__tree = tree

    def render(self):
        print('Digraph family_tree {')
        print('    engine = neato')
        print('    splines = ortho')
        print('    center = true')
        print('    edge [dir = none]')
        print()

        family = self.__tree.getRootFamily()

        self.__renderFamily(family)
     
        nextGeneration = self.__tree.getRootGeneration()
        while nextGeneration:
            generation = []
            nextSibling = nextGeneration.getPrevSibling()
            while nextSibling:
                generation.append(nextSibling.getId())
                nextSibling = nextSibling.getNextSibling()

            print('    {rank = same; %s [style = invis];};' % ' -> '.join(generation))

            if nextGeneration.hasChilds():
                nextGeneration = nextGeneration.getChilds()[0]
            else:
                break

        for individual in self.__tree.getIndividuals():
            id = individual.getId()
            gedcom = individual.getGedcom()
            label = '{}\\n{}\\n{}'.format(gedcom.getCallname(), gedcom.getBirthname(), individual.getId())
            print('    {id} [shape = doubleoctagon label="{label}"];'.format(id = id, label = label))

            if individual.isChild():
                print('    {id}Child [shape = circle, label="", height = 0.01, width = 0.0];'.format(id = id))
                print('    {id}Child -> {id} [headport = n];'.format(id = id))
            
            print()

        print('}')

    def __renderFamily(self, family):
        id = family.getId()
        partners = family.getPartners()
        print('    {id} [shape = circle, label = "", height = 0.01, width = 0.0];'.format(id = id))
        print('    {rank = same; %s -> %s -> %s;};' % (partners[0].getId(), id, partners[1].getId()))

        if family.hasChilds():
            childs = family.getChilds()
            childsIds = list(map(lambda x: x.getId(), childs))

            childNodes = list(map(lambda x: x + 'Child', childsIds))
            childCount = len(childNodes)

            if childCount % 2 == 0:
                childNode = '{id}Childs'.format(id = id)
                print('    {} [shape = circle, label = "", height = 0.01, width = 0.0];'.format(childNode))
                childNodes.insert(int(childCount / 2), childNode)
            else:
                childNode = childNodes[int(ceil(childCount / 2) - 1)]

            print('    {rank = same; %s;};' % (' -> '.join(childNodes)))
            print('    {rank=same; %s;}' % ('; '.join(childsIds)))
            print('    {} -> {};'.format(id, childNode))

            print()

            for child in childs:
                for childFamily in child.getFamilies():
                    self.__renderFamily(childFamily)

        print()
