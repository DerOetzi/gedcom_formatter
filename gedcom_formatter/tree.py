from .gedcom.model import GedcomIndividual, GedcomFamily

class Node():
    def __init__(self, id, level):
        self._id = id
        self._level = level

        self.__parent = None
        self._childs = []
        self.__prevSibling = None
        self.__nextSibling = None

    def getId(self):
        return self._id

    def getLevel(self):
        return self._level

    def hasChilds(self):
        return len(self._childs) > 0

    def addChild(self, child):
        child.setParent(self)
        if self.hasChilds():
            last = self._childs[-1]
            last.setNextSibling(child)
            child.setPrevSibling(last)

        self._childs.append(child)

    def getChilds(self):
        return self._childs

    def setParent(self, parent):
        self.__parent = parent

    def getParent(self):
        return self.__parent

    def isChild(self):
        return self.__parent is not None

    def setPrevSibling(self, prevSibling):
        self.__prevSibling = prevSibling

    def getPrevSibling(self):
        return self.__prevSibling

    def setNextSibling(self, nextSibling):
        self.__nextSibling = nextSibling

    def getNextSibling(self):
        return self.__nextSibling

class Generation():
    def __init__(self, level):
        self._id = 'G%d' % level 
        self.__level = level

        self.__first = None
        self.__last = None

        self.__prevGeneration = None
        self.__nextGeneration = None

    def getId(self):
        return self._id

    def isInitialized(self):
        return self.__first is not None

    def append(self, individuals):
        if self.isInitialized():
            firstIndividual = individuals[0]
            while firstIndividual.getPrevSibling() is not None:
                firstIndividual = firstIndividual.getPrevSibling()

            self.__last.setNextSibling(firstIndividual)
            firstIndividual.setPrevSibling(self.__last)

            lastIndividual = individuals[-1]
            while lastIndividual.getNextSibling() is not None:
                lastIndividual = lastIndividual.getNextSibling()

            self.__last = lastIndividual
            

        else:
            self.__first = individuals[0]
            self.__last = individuals[-1]

    def fixFirst(self):
        while self.__first.getPrevSibling() is not None:
            self.__first = self.__first.getPrevSibling()

    def setPrevGeneration(self, generation):
        self.__prevGeneration = generation

    def addNextGeneration(self, generation):
        self.__nextGeneration = generation
        generation.setPrevGeneration(self)

    def getNextGeneration(self):
        return self.__nextGeneration

    def getIndividuals(self):
        individuals = []

        current = self.__first
        while current is not None:
            individuals.append(current)
            current = current.getNextSibling()

        return individuals

class Individual(Node):
    def __init__(self, gedcom: GedcomIndividual, level):
        Node.__init__(self, gedcom.getId(), level)
        self.__gedcom = gedcom
        self.__families = {}

    def getGedcom(self):
        return self.__gedcom

    def hasFamilies(self):
        return len(self.__families) > 0

    def addFamily(self, family):
        self.__families[family.getId()] = family

    def getFamilies(self):
        return self.__families.values()

    def isMale(self):
        return self.__gedcom.isMale()

    def getBirthYear(self):
        return self.__gedcom.getBirthYear()

    def __str__(self):
        return self._id

class Family(Node):
    def __init__(self, gedcom: GedcomFamily, level):
        Node.__init__(self, gedcom.getId(), level)
        self.__gedcom = gedcom
        self.__partners = []

    def addPartners(self, partners):
        revert = False

        for partner in partners:
            gFamilies = partner.getGedcom().getFamilies()
            if len(gFamilies) == 2 and gFamilies.index(self._id):
                revert = True

            if partner.isMale():
                self.__partners.insert(0, partner)
            else:
                self.__partners.append(partner)

            partner.addFamily(self)

        if revert:
            self.__partners.reverse()

        prevPartner1 = self.__partners[1].getPrevSibling()
        if prevPartner1 is not None:
            prevPartner1.setNextSibling(self.__partners[0])
            self.__partners[0].setPrevSibling(prevPartner1)

        nextPartner0 = self.__partners[0].getNextSibling()
        if nextPartner0 is not None:
            nextPartner0.setPrevSibling(self.__partners[1])
            self.__partners[1].setNextSibling(nextPartner0)

        self.__partners[0].setNextSibling(self.__partners[1])
        self.__partners[1].setPrevSibling(self.__partners[0])

    def getPartners(self):
        return self.__partners

    def addChilds(self, childs):
        childsSorted = sorted(childs, key = lambda x: x.getBirthYear()) 

        for child in childsSorted:
            self.addChild(child)

        return childsSorted

    def __str__(self):
        return '%s: %s %s' % (self._id, self.__partners, self._childs)

class FamilyTree():
    def __init__(self, gedcom):
        self.__gedcom = gedcom
        self.__rootFamily = None
        self.__generations = {}
        self.__individuals = {}

    def build(self, rootFamily, maxDepth = 1):
        gFamily = self.__gedcom.getFamily(rootFamily) 
        
        self.__rootFamily = self.__addFamily(gFamily, maxDepth, maxDepth)

    def getRootGeneration(self):
        return self.__generations[0]

    def __addFamily(self, gFamily, maxDepth, depth):

        level = maxDepth - depth

        family = Family(gFamily, level)

        partners = list(map(lambda x: self.__getIndividual(x, level), gFamily.getCouple()))
        family.addPartners(partners)

        generation = self.__getGeneration(level)
        if not generation.isInitialized():
            partners = family.getPartners()
            generation.append(partners)

        if depth <= 1:
            return family

        childs = self.__addChildsToFamily(family, gFamily.getChildren(), level + 1)
        
        if len(childs) > 0:
            childGeneration = self.__getGeneration(level + 1)
            childGeneration.append(childs)

            for child in childs:
                families = child.getGedcom().getFamilies()
                for familyId in families:
                    familyChild = self.__gedcom.getFamily(familyId)
                    self.__addFamily(familyChild, maxDepth, depth - 1)

            childGeneration.fixFirst()

        return family

    def __getGeneration(self, level):
        if level not in self.__generations:
            generation = Generation(level)
            if level - 1 in self.__generations:
                self.__generations[level - 1].addNextGeneration(generation)
            self.__generations[level] = generation
        
        return self.__generations[level]

    def getRootFamily(self):
        return self.__rootFamily

    def getIndividuals(self):
        return self.__individuals.values()

    def __getIndividual(self, id, level):
        if id not in self.__individuals:
            gIndividual = self.__gedcom.getIndividual(id)
            self.__individuals[id] = Individual(gIndividual, level)

        return self.__individuals[id]

    def __addChildsToFamily(self, family, gChildren, level):
        childs = []
        for childId in gChildren:
            childs.append(self.__getIndividual(childId, level))
        
        if len(childs) > 0:
            return family.addChilds(childs)

        return []

    def __str__(self):
        return 'Individuals: %d, generations: %s' % (len(self.__individuals), len(self.__generations))