#  Copyright (C)  2021 Rage Uday Kiran
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PAMI.coveragePatterns.basic import abstract as _ab


_maxPer = float()
_minSup = float()
_lno = int()


class CPPG(_ab._coveragePatterns):
    """ CPPG  algorithm discovers coverage patterns in a transactional database.

    Reference:
    --------
        Gowtham Srinivas, P.; Krishna Reddy, P.; Trinath, A. V.; Bhargav, S.; Uday Kiran, R. (2015).
        Mining coverage patterns from transactional databases. Journal of Intelligent Information Systems, 45(3), 423–439.
        https://link.springer.com/article/10.1007/s10844-014-0318-3

    Attributes:
    ----------
        iFile : file
            Name of the Input file or path of the input file
        oFile : file
            Name of the output file or path of the output file
        minSup: int or float or str
            The user can specify minSup either in count or proportion of database size.
            If the program detects the data type of minSup is integer, then it treats minSup is expressed in count.
            Otherwise, it will be treated as float.
            Example: minSup=10 will be treated as integer, while minSup=10.0 will be treated as float
        maxPer: int or float or str
            The user can specify maxPer either in count or proportion of database size.
            If the program detects the data type of maxPer is integer, then it treats maxPer is expressed in count.
            Otherwise, it will be treated as float.
            Example: maxPer=10 will be treated as integer, while maxPer=10.0 will be treated as float
        sep : str
            This variable is used to distinguish items from one another in a transaction. The default seperator is tab space or \t.
            However, the users can override their default separator.
        memoryUSS : float
            To store the total amount of USS memory consumed by the program
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        Database : list
            To store the transactions of a database in list
        mapSupport : Dictionary
            To maintain the information of item and their frequency
        lno : int
            To represent the total no of transaction
        tree : class
            To represents the Tree class
        itemSetCount : int
            To represents the total no of patterns
        finalPatterns : dict
            To store the complete patterns

    Methods:
    -------
        startMine()
            Mining process will start from here
        getPatterns()
            Complete set of patterns will be retrieved with this function
        save(oFile)
            Complete set of periodic-frequent patterns will be loaded in to a output file
        getPatternsAsDataFrame()
            Complete set of periodic-frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingItemSets(fileName)
            Scans the dataset and stores in a list format
        coverageOneItem()
            Extracts the one-coverage patterns from database
        updateDatabases()
            Update the database by removing aperiodic items and sort the Database by item decreased support
        buildTree()
            After updating the Database, remaining items will be added into the tree by setting root node as null
        convert()
            to convert the user specified value

    Executing the code on terminal:
    -------
        Format:
        ------
            python3 CPPG.py <inputFile> <outputFile> <minRF> <minCS> <maxOR> <'\t'>

        Examples:
        --------
            python3 CPPG.py sampleTDB.txt patterns.txt 0.4 0.7 0.5 ','

        Sample run of importing the code:
        -------------------

            from PAMI.coveragePattern.basic import CPPG as alg

            obj = alg.CPPG(iFile, minRF, minCS, maxOR)

            obj.startMine()

            coveragePatterns = obj.getPatterns()

            print("Total number of coverage Patterns:", len(coveragePatterns))

            obj.save(oFile)

            Df = obj.getPatternsAsDataFrame()

            memUSS = obj.getMemoryUSS()

            print("Total Memory in USS:", memUSS)

            memRSS = obj.getMemoryRSS()

            print("Total Memory in RSS", memRSS)

            run = obj.getRuntime()

            print("Total ExecutionTime in seconds:", run)

    Credits:
    -------
        The complete program was written by P.Likhitha  under the supervision of Professor Rage Uday Kiran.

    """
    _startTime = float()
    _endTime = float()
    _minRF = str()
    _maxOR = str()
    _minCS = str()
    _finalPatterns = {}
    _iFile = " "
    _oFile = " "
    _sep = " "
    _memoryUSS = float()
    _memoryRSS = float()
    _Database = []
    _rank = {}
    _rankedUp = {}
    _lno = 0

    def _creatingItemSets(self):
        """
            Storing the complete transactions of the database/input file in a database variable


        """
        self._Database = []
        if isinstance(self._iFile, _ab._pd.DataFrame):
            data, ts = [], []
            if self._iFile.empty:
                print("its empty..")
            i = self._iFile.columns.values.tolist()
            if 'TS' in i:
                ts = self._iFile['TS'].tolist()
            if 'Transactions' in i:
                data = self._iFile['Transactions'].tolist()
            for i in range(len(data)):
                tr = [ts[i][0]]
                tr = tr + data[i]
                self._Database.append(tr)

        if isinstance(self._iFile, str):
            if _ab._validators.url(self._iFile):
                data = _ab._urlopen(self._iFile)
                for line in data:
                    line.strip()
                    line = line.decode("utf-8")
                    temp = [i.rstrip() for i in line.split(self._sep)]
                    temp = [x for x in temp if x]
                    self._Database.append(temp)
            else:
                try:
                    with open(self._iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line.strip()
                            temp = [i.rstrip() for i in line.split(self._sep)]
                            temp = [x for x in temp if x]
                            self._Database.append(temp)
                except IOError:
                    print("File Not Found")
                    quit()


    def _coverageOneItem(self):
        """ Calculates the support of each item in the database and assign ranks to the items
            by decreasing support and returns the frequent items list

            :returns: return the one-length periodic frequent patterns
        """
        data = {}
        count = 0
        for tr in self._Database:
            count += 1
            for i in range(len(tr)):
                if tr[i] not in data:
                    data[tr[i]] = [count]
                else:
                    data[tr[i]].append(count)
        data = {k: v for k, v in data.items() if len(v)/len(self._Database) >= self._minRF}
        pfList = [i for i in sorted(data, key=lambda k: len(data[k]), reverse=True)]
        return data, pfList

    def _updateDatabases(self, dict1):
        """ Remove the items which are not frequent from database and updates the database with rank of items

            :param dict1: frequent items with support
            :type dict1: list
            :return: Sorted and updated transactions
            """
        list2 = []
        for tr in self._Database:
            list1 = []
            for i in range(len(tr)):
                if tr[i] in dict1:
                    list1.append(tr[i])
            list2.append([i for i in dict1 if i in list1])
        return list2

    def _buildProjectedDatabase(self, data, info):
        """ To construct the projected database for each prefix
        """
        proData = {}
        for i in range(len(info)):
            prefix = info[i+1:]
            proData[info[i]] = []
            for j in data:
                te = []
                if info[i] not in j:
                    for k in j:
                        if k in prefix:
                            te.append(k)
                if len(te) > 0:
                    proData[info[i]].append(te)
        for x, y in proData.items():
            print(x, y)
        return proData

    def _generateFrequentPatterns(self,  uniqueItems):
        """It will generate the combinations of frequent items

        :param uniqueItems :it represents the items with their respective transaction identifiers

        :type uniqueItems: list

        :return: returning transaction dictionary

        :rtype: dict
        """
        new_freqList = []
        for i in range(0, len(uniqueItems)):
            item1 = uniqueItems[i]
            i1_list = item1.split()
            for j in range(i + 1, len(uniqueItems)):
                item2 = uniqueItems[j]
                i2_list = item2.split()
                if i1_list[:-1] == i2_list[:-1]:
                    interSet = set(self._finalPatterns[item1]).intersection(set(self._finalPatterns[item2]))
                    union = set(self._finalPatterns[item1]).union(set(self._finalPatterns[item2]))
                    if len(union)/len(self._Database) >= self._minCS and len(interSet)/len(self._finalPatterns[item1]) <= self._maxOR:
                        newKey = item1 + " " + i2_list[-1]
                        self._finalPatterns[newKey] = interSet
                        new_freqList.append(newKey)
                else:
                    break

        if len(new_freqList) > 0:
            self._generateFrequentPatterns(new_freqList)

    def _savePeriodic(self, itemSet):
        """ To convert the ranks of items in to their original item names

            :param itemSet: frequent pattern
            :return: frequent pattern with original item names
        """
        t1 = str()
        for i in itemSet:
            t1 = t1 + self._rankedUp[i] + "\t"
        return t1

    def _convert(self, value):
        """
        To convert the given user specified value

        :param value: user specified value
        :return: converted value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = value
        if type(value) is str:
            if '.' in value:
                value = float(value)
                value = value
            else:
                value = int(value)
        return value

    def startMine(self):
        """ Mining process will start from this function
        """

        #global _minSup, _maxPer, _lno
        self._startTime = _ab._time.time()
        if self._iFile is None:
            raise Exception("Please enter the file path or file name:")
        if self._minRF is None:
            raise Exception("Please enter the Relative Frequency")
        if self._maxOR is None:
            raise Exception("Please enter the Overlap Ratio")
        if self._minCS is None:
            raise Exception("Please enter the Coverage Ratio")
        self._creatingItemSets()
        self._minRF = self._convert(self._minRF)
        self._maxOR = self._convert(self._maxOR)
        self._minCS = self._convert(self._minCS)
        if self._minRF > len(self._Database) or self._minCS > len(self._Database) or self._maxOR > len(self._Database):
            raise Exception("Please enter the constraints in range between 0 to 1")
        generatedItems, pfList = self._coverageOneItem()
        self._finalPatterns = {k: v for k, v in generatedItems.items()}
        updatedDatabases = self._updateDatabases(pfList)
        proData = self._buildProjectedDatabase(updatedDatabases, pfList)
        for x, y in proData.items():
            uniqueItems = [x]
            for i in y:
                for j in i:
                    if j not in uniqueItems:
                        uniqueItems.append(j)
            self._generateFrequentPatterns(uniqueItems)
        self._endTime = _ab._time.time()
        process = _ab._psutil.Process(_ab._os.getpid())
        self._memoryUSS = float()
        self._memoryRSS = float()
        self._memoryUSS = process.memory_full_info().uss
        self._memoryRSS = process.memory_info().rss
        print("Coverage patterns were generated successfully using CPPG algorithm ")

    def getMemoryUSS(self):
        """Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process
        :rtype: float
        """

        return self._memoryUSS

    def getMemoryRSS(self):
        """Total amount of RSS memory consumed by the mining process will be retrieved from this function

        :return: returning RSS memory consumed by the mining process
        :rtype: float
        """

        return self._memoryRSS

    def getRuntime(self):
        """Calculating the total amount of runtime taken by the mining process


        :return: returning total amount of runtime taken by the mining process
        :rtype: float
        """

        return self._endTime - self._startTime

    def getPatternsAsDataFrame(self):
        """Storing final periodic-frequent patterns in a dataframe

        :return: returning periodic-frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataFrame = {}
        data = []
        for a, b in self._finalPatterns.items():
            data.append([a.replace('\t', ' '), b[0], b[1]])
            dataFrame = _ab._pd.DataFrame(data, columns=['Patterns', 'Support', 'Periodicity'])
        return dataFrame

    def save(self, outFile):
        """Complete set of periodic-frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self._oFile = outFile
        writer = open(self._oFile, 'w+')
        for x, y in self._finalPatterns.items():
            s1 = x.strip() + ":" + str(len(y))
            writer.write("%s \n" % s1)

    def getPatterns(self):
        """ Function to send the set of periodic-frequent patterns after completion of the mining process

        :return: returning periodic-frequent patterns
        :rtype: dict
        """
        return self._finalPatterns

    def printResults(self):
        print("Total number of Coverage Patterns:", len(self.getPatterns()))
        print("Total Memory in USS:", self.getMemoryUSS())
        print("Total Memory in RSS", self.getMemoryRSS())
        print("Total ExecutionTime in ms:",  self.getRuntime())


if __name__ == "__main__":
    _ap = str()
    if len(_ab._sys.argv) == 6 or len(_ab._sys.argv) == 7:
        if len(_ab._sys.argv) == 7:
            _ap = CPPG(_ab._sys.argv[1], _ab._sys.argv[3], _ab._sys.argv[4], _ab._sys.argv[5], _ab._sys.argv[6])
        if len(_ab._sys.argv) == 6:
            _ap = CPPG(_ab._sys.argv[1], _ab._sys.argv[3], _ab._sys.argv[4], _ab._sys.argv[5])
        _ap.startMine()
        print("Total number of Coverage Patterns:", len(_ap.getPatterns()))
        _ap.save(_ab._sys.argv[2])
        print("Total Memory in USS:",  _ap.getMemoryUSS())
        print("Total Memory in RSS", _ap.getMemoryRSS())
        print("Total ExecutionTime in ms:", _ap.getRuntime())
    else:
        _ap = CPPG('sample.txt', 0.4, 0.7, 0.5, ' ')
        _ap.startMine()
        print("Total number of Coverage Patterns:", len(_ap.getPatterns()))
        _ap.save('output.txt')
        _ap.printResults()
        print("Error! The number of input parameters do not match the total number of parameters provided")
