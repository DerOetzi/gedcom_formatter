import re as regex
from parser.element import RawElement
from element.individual import Individual
from element.family import Family

LEVEL_REGEX = '^(0|[1-9]+[0-9]*) '

POINTER_REGEX = '(@[^@]+@ |)'

TAG_REGEX = '([A-Za-z0-9_]+)'

VALUE_REGEX = '( [^\n\r]*|)'

EOL_REGEX = '[\r\n]{0,2}'

LINE_REGEX = LEVEL_REGEX + POINTER_REGEX + TAG_REGEX + VALUE_REGEX + EOL_REGEX

class Gedcom():
    def __init__(self):
        self.individuals = {}
        self.families = {}

    def parseFile(self, filename):
        with open(filename, 'rb') as fp:
            lineNumber = 1
            rootElement = RawElement(-1, '', 'ROOT', '')
            lastElement = rootElement
            for line in fp:
                lastElement = self.__parseLine(lineNumber, line.decode('utf-8-sig'), lastElement)
                lineNumber += 1

        for element in rootElement.getChildren():
            if element.getTag() == Individual.TAG:
                individual = Individual(element)
                self.individuals[individual.getId()] = individual
                print('%s' % individual)

        for element in rootElement.getChildren():
            if element.getTag() == Family.TAG:
                family = Family(element, self.individuals)
                self.families[family.getId()] = family
                print('%s' % family)

    def __parseLine(self, lineNumber, line, lastElement):
        matches = regex.match(LINE_REGEX, line)
        if matches is None:
            errorMessage = "Line <%d:%s> of document violates GEDCOM" % (lineNumber, line)
            raise Exception(errorMessage)

        else:
            level, pointer, tag, value = matches.groups()
            level = int(level)

            if level > lastElement.getLevel() + 1:
                errorMessage = "Line <%d:%d> level violation" % (lineNumber, level)
                raise Exception(errorMessage)

            element = RawElement(level, pointer, tag, value)

            parent = lastElement

            while parent.getLevel() > level - 1:
                parent = parent.getParent()

            parent.addChild(element)

            return element

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    gedcom = Gedcom()
    gedcom.parseFile(filename)