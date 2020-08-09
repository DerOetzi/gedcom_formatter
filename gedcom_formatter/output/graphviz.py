import os

from graphviz import Digraph
from ..tree import FamilyTree

class Graphviz(object):
    def __init__(self, tree: FamilyTree):
        self.__tree = tree

    def render(self):
        g = Digraph(
            name = 'family_tree', format = 'svg', engine = 'dot',
            graph_attr = {'splines': 'line', 'center': 'true', 'nodesep': '1.0', 'ranksep': '3.2'},
            node_attr = {'shape': 'circle', 'height': '0.0', 'width': '0.0'},
            edge_attr = {'dir': 'none', 'penwidth': '30.0'}
        )

        rootFamily = self.__tree.getRootFamily()
        g.attr(root = rootFamily.getId())
        g.attr(center = 'true')

        curGeneration = self.__tree.getRootGeneration()
        while curGeneration is not None:
            with g.subgraph(name = curGeneration.getId()) as gen:
                gen.attr(rank = 'same')

                curInd = curGeneration.getFirst()
                nextInd = curInd.getNextSibling()
                while nextInd is not None:
                    betweenNode = '%sBetween%s' % (curInd.getId(), nextInd.getId())

                    gen.node(betweenNode, label = '', style = 'invis')

                    gen.edge(
                        curInd.getId(), betweenNode, 
                        label = None, style = 'invis'
                    )

                    gen.edge(
                        betweenNode, nextInd.getId(), 
                        label = None, style = 'invis'
                    )

                    curInd = nextInd
                    nextInd = nextInd.getNextSibling()
        
            curGeneration = curGeneration.getNextGeneration()

        self.__renderFamily(rootFamily, g)

        for individual in self.__tree.getIndividuals():
            id = individual.getId()
            g.node(
                id, label = self.__renderLabel(individual), 
                shape = 'invhouse', width = '10', height = '25',
                penwidth = '2.0', style = 'filled', fillcolor = 'lightgrey:antiquewhite',
                gradientangle = '135'
                #image = './shield2.png', width = '10', height = '10', align = 'center'
            )

            if individual.isChild():
                g.node('%sChild' % id, label = '')

                g.edge('%sChild' % id, id, label = None, weight = '10')

        g.save()

    def __renderFamily(self, family, graph):
        id = family.getId()
        partners = family.getPartners()
        with graph.subgraph(name = 'Family%s' % id) as f:
            with f.subgraph(name = 'Partners%s' % id) as p:
                p.attr(rank = 'same')
                
                p.node(id, label = '')    

                p.edge(partners[0].getId(), id, label = None, weight = '10')
                p.edge(id, partners[1].getId(), label = None, weight = '10')
                    
            if family.hasChilds():
                childs = family.getChilds()
                childsIds = list(map(lambda x: x.getId(), childs))

                childNode = '%sChilds' % id

                with f.subgraph(name = 'Childs%s' % id) as c:
                    c.attr(rank = 'same')
                    for childId in childsIds:
                        c.node(childId)

                f.node(childNode, label = '')

                f.edge(id, childNode, label = None, weight = '10')

                for child in childs:
                    f.edge(
                        childNode, '%sChild' % child.getId(), label = None, weight = '2'
                    )

                    for childFamily in child.getFamilies():
                        self.__renderFamily(childFamily, f)

    def __renderLabel(self, individual):
        gedcom = individual.getGedcom()

        label = '<<table border="0" cellborder="0" cellpadding="0" align="center">'

        if gedcom.isFile():
            imgSrc = os.path.realpath('./Media/%s' % gedcom.getFile())
        else:
            if individual.isMale():
                imgSrc = './male.png'
            else:
                imgSrc = './female.png'

        callname = gedcom.getCallname()
        if len(callname) > 10:
            callnameSize = 92
        elif len(callname) > 8:
            callnameSize = 104
        else:
            callnameSize = 128

        birthdate = ''
        if gedcom.isBirthdate():
            birthdate = '&#x2733; ' + gedcom.getBirthdateFormatted()
        
        deathdate = ''
        if gedcom.isDeathdate():
            deathdate = '&#x271D; ' + gedcom.getDeathdateFormatted()

        label += '<tr><td><img src="%s" scale="TRUE"/></td></tr>' % imgSrc
        label += '<tr><td> </td></tr>'
        label += '<tr><td><FONT POINT-SIZE="%d" FACE="Parisienne">%s</FONT></td></tr>' % (callnameSize, callname)
        label += '<tr><td><FONT POINT-SIZE="80" FACE="Parisienne">%s</FONT></td></tr>' % gedcom.getBirthname()
        label += '<tr><td> </td></tr>'
        label += '<tr><td><FONT POINT-SIZE="64" FACE="Sacramento">%s </FONT></td></tr>' % birthdate
        label += '<tr><td><FONT POINT-SIZE="64" FACE="Sacramento">%s </FONT></td></tr>' % deathdate
        label += '</table>>'

        return label
