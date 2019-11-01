import glob,nltk,os,re,code,traceback
import pdftotext
from pprint import pprint

class exportToFile:
    def __init__(self, fileName='results.txt', resetFile=False):
        headers = ['NAME','EMAIL', 'Mobile']
        if not os.path.isfile(fileName) or resetFile:
            # Will create/reset the file as per the evaluation of above condition
            fOut = open(fileName, 'w')
            fOut.close()
        fIn = open(fileName)  ########### Open file if file already present
        inString = fIn.read()
        fIn.close()
        if len(inString) <= 0:  ######### If File already exsists but is empty, it adds the header
            fOut = open(fileName, 'w')
            fOut.write(','.join(headers) + '\n')
            fOut.close()

    def write(self, infoDict):
        fOut = open('resultsCSV.txt', 'w')
        # Individual elements are dictionaries
        writeString = ''
        try:
            writeString += str(infoDict['name']) + ','

            if infoDict['email']:
                writeString += str(','.join(infoDict['email'][:4]))
            if infoDict['phone']:
                writeString += str(','.join(infoDict['phone'][:4]))

            fOut.write(writeString)
        except:
            fOut.write('FAILED_TO_WRITE\n')
        fOut.close()

class Parse():
    information = []
    inputString = ''
    tokens = []
    lines = []
    sentences = []

    def __init__(self, verbose=False):
        print('Starting Programme')
        fields = ["name","email", "mobile",]

        # Glob module matches certain patterns
        pdf_files = glob.glob("test.pdf")

        files = set(pdf_files)
        files = list(files)
        print("%d files identified" % len(files))

        info = {}

        self.inputString = self.readFile()
        print("----------------------")
        print(self.inputString)
        self.tokenize(self.inputString)

        self.getEmail(self.inputString, info)

        self.getPhone(self.inputString, info)

        self.getName(self.inputString, info)

        csv = exportToFile()
        csv.write(info)
        self.information.append(info)
        print(info)

    def readFile(self):
        return pdftotext.convertPDFToText()


    def preprocess(self, document):
        # Try to get rid of special characters
        try:
            document = document.decode('ascii', 'ignore')
        except:
            document = document.encode('ascii', 'ignore')
        try:
            document = str(document)
            lines = [el.strip() for el in document.split("\n") if len(el) > 0]
            lines = [nltk.word_tokenize(el) for el in lines]
            lines = [nltk.pos_tag(el) for el in lines]

            sentences = nltk.sent_tokenize(document)
            sentences = [nltk.word_tokenize(sent) for sent in
                         sentences]
            tokens = sentences
            sentences = [nltk.pos_tag(sent) for sent in
                         sentences]
            dummy = []
            for el in tokens:
                dummy += el
            tokens = dummy

            return tokens, lines, sentences
        except Exception as e:
            print(e)

    def tokenize(self, inputString):
        try:
            self.tokens, self.lines, self.sentences = self.preprocess(inputString)
            return self.tokens, self.lines, self.sentences
        except Exception as e:
            print("Bhlbla bal")
            print (e)

    def getEmail(self, inputString, infoDict, debug=False):

        email = None
        try:
            pattern = re.compile(r'\S*@\S*')
            matches = pattern.findall(inputString)  # Gets all email addresses as a list
            email = matches
        except Exception as e:
            print (e)

        infoDict['email'] = email

        if debug:
            print("\n", pprint(infoDict), "\n")
            code.interact(local=locals())
        return email

    def getPhone(self, inputString, infoDict, debug=False):
        number = None
        try:
            pattern = re.compile(
                r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
            match = pattern.findall(inputString)
            match = [re.sub(r'[,.]', '', el) for el in match if len(re.sub(r'[()\-.,\s+]', '', el)) > 6]
            # Taking care of years, eg. 2001-2004 etc.
            match = [re.sub(r'\D$', '', el).strip() for el in match]
            # $ matches end of string. This takes care of random trailing non-digit characters. \D is non-digit characters
            match = [el for el in match if len(re.sub(r'\D', '', el)) <= 15]
            # Remove number strings that are greater than 15 digits
            try:
                for el in list(match):
                    # Create a copy of the list since you're iterating over it
                    if len(el.split('-')) > 3: continue  # Year format YYYY-MM-DD
                    for x in el.split("-"):
                        try:
                            # Error catching is necessary because of possibility of stray non-number characters
                            # if int(re.sub(r'\D', '', x.strip())) in range(1900, 2100):
                            if x.strip()[-4:].isdigit():
                                if int(x.strip()[-4:]) in range(1900, 2100):
                                    # Don't combine the two if statements to avoid a type conversion error
                                    match.remove(el)
                        except:
                            pass
            except:
                pass
            number = match
        except:
            pass

        infoDict['phone'] = number


    def getName(self, inputString, infoDict, debug=False):
        Names = open("allNames.txt", "r").read().lower()
        Names = set(Names.split())
        otherNameHits = []
        nameHits = []
        name = None
        tokens, lines, sentences = self.tokens, self.lines, self.sentences
        grammar = r'NAME: {<NN.*><NN.*><NN.*>*}'
        chunkParser = nltk.RegexpParser(grammar)
        all_chunked_tokens = []
        for tagged_tokens in lines:
            if len(tagged_tokens) == 0: continue  # Prevent it from printing warnings
            chunked_tokens = chunkParser.parse(tagged_tokens)
            all_chunked_tokens.append(chunked_tokens)
            for subtree in chunked_tokens.subtrees():
                if subtree.label() == 'NAME':
                    for ind, leaf in enumerate(subtree.leaves()):
                        if leaf[0].lower() in Names and 'NN' in leaf[1]:
                            hit = " ".join([el[0] for el in subtree.leaves()[ind:ind + 3]])
                            if re.compile(r'[\d,:]').search(hit): continue
                            nameHits.append(hit)
                                # Need to iterate through rest of the leaves because of possible mis-matches
            # Going for the first name hit
        if len(nameHits) > 0:
            nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in nameHits]
            name = " ".join([el[0].upper() + el[1:].lower() for el in nameHits[0].split() if len(el) > 0])



        infoDict['name'] = name
        infoDict['otherNameHits'] = otherNameHits

        if debug:
            print
            "\n", pprint(infoDict), "\n"
            code.interact(local=locals())
        return name, otherNameHits