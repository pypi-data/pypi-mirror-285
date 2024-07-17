import os.path


def getFilteredFileLines(path):
    if (os.path.isfile(path)):
        with open(path, "r") as file:

            filteredLines = []

            for line in file:
                if (len(line) > 1 and line[0] != "#"):

                    line = line.replace("\n", "")
                    line = line.lstrip(' ')
                    line = line.rstrip(' ')

                    filteredLines.append(line)

            return filteredLines

    return None
