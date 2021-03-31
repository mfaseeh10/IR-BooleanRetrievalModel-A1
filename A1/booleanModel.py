from tkinter import ttk
from tkinter import messagebox
import tkinter


# This function will do casefolding .
def case_folding(w):
    return (w.lower())

# This function will remove punctuations from  words


def remove_punctuation(w):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~‘’“”'''
    no_punct = ""
    for char in w:
        if char not in punctuations:
           # print(char)
            no_punct = no_punct + char
    w = no_punct

    return (w)

# This function will stemming using PorterStemmer algorithm using nltk library


def stemming(w):
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    return (ps.stem(w))

# A caller function to invoke all preprocessing functions


def pre_processing(w):
    w = case_folding(w)
    w = remove_punctuation(w)
    w = stemming(w)
    return (w)

# This function will return list of all stop words .


def read_stopwords():
    stopword = []
  #  f = open("D:/faseeh/SEMESTER 6/IR/A1/Stopwords/Stopword-List.txt", "r")
    f = open('C:/Users/Saleem/Documents/GitHub/IR-BooleanRetrievalModel-A1/A1/Stopwords/Stopword-List.txt', 'r')
    stopwordlist = f.readlines()
    f.close()
    for l in stopwordlist:
        stopword = stopword + l.split()
    return (stopword)


# function to break string into list of words
def make_word_list(word_list):
    W = []
    w = ''
    for word in word_list:
        if ((word != ' ') and (word != '.') and (word != ']') and (word != '\n') and (word != '-') and (
                word != '—') and (word != '?') and (word != '"') and (word != '…') and (word != '/')):
            w = w + word
        elif ((w != '')):
            W = W + [w]
            w = ''
    if ((w != '')):
        W = W + [w]
    return (W)

# Function to return an id for a given document


def get_doc_id(fn):
    if (fn[1] == '.'):
        return (fn[0])
    else:
        return (fn[0] + fn[1])


# This function will read all documents and will make Inverted and Position Index .
def indexingDocs():
    import os
    directory = os.getcwd()

    invertedIndex = {}
    positional_Indexes = {}
    stopwordsList = read_stopwords()
    # print(stopwordsList)

    for filename in os.listdir(directory):
        if (filename.endswith(".txt")):
            i = -1  # to maintain position of words in positional indexes
            # print(filename)
            lines = []  # to store each line in file as a list
            f = open(filename, encoding="utf8")
            lines = f.readlines()
            f.close()

            wordlist = []  # to store file as a list of words
            for line in lines:
                wList = make_word_list(line)
                wordlist.extend(wList)

            # print(wordlist)
            wordlist.sort()
            for word in wordlist:
                i = i + 1
                if (word == ''):
                    continue

            #   word = pre_processing(word)

                word = case_folding(word)
                word = remove_punctuation(word)

                if word not in stopwordsList:
                    word = stemming(word)

                # to genrate an INVERTED INDEX for the terms
                    if word not in invertedIndex:
                        invertedIndex[word] = []
                    if get_doc_id(filename) not in invertedIndex[word]:
                        invertedIndex[word] = invertedIndex[word] + \
                            [get_doc_id(filename)]

                # to genrate an Positional INDEX for the terms
                    if word not in positional_Indexes:
                        positional_Indexes[word] = {get_doc_id(filename): [i]}
                    elif get_doc_id(filename) in positional_Indexes[word]:
                        positional_Indexes[word][get_doc_id(filename)] += [i]
                    else:
                        positional_Indexes[word][get_doc_id(filename)] = [i]

        else:
            continue

    # writing indexes to files in order to save and retrive later for quicker query processing
    try:
        ii_file = open(
            'D:/faseeh/SEMESTER 6/IR/A1/Indexes/invertedIndex.txt', 'wt')
        ii_file.write(str(invertedIndex))
        ii_file.close()
    except:
        print("Unable to write to file")

    try:
        pi_file = open(
            'D:/faseeh/SEMESTER 6/IR/A1/Indexes/positionIndex.txt', 'wt')
        pi_file.write(str(positional_Indexes))
        pi_file.close()
    except:
        print("Unable to write to file")

    return (invertedIndex, positional_Indexes)


# This function will handle single word query
def simple_query(w, invertedIndex):
    result = []
    w = pre_processing(w)
    # print(w)
    if w in invertedIndex:
        result = invertedIndex[w]
    return (result)


# function to read invertedIndex into memory
def read_InvertedIndex_file():
    import ast

    invertedindex = {}
    #infile = open('D:/faseeh/SEMESTER 6/IR/A1/Indexes/invertedIndex.txt', "r")
    infile = open(
        'C:/Users/Saleem/Documents/GitHub/IR-BooleanRetrievalModel-A1/A1/Indexes/invertedIndex.txt', "r")
    contents = infile.read()
    invertedindex = ast.literal_eval(contents)

    infile.close()

    return invertedindex


# function to read positional into memory
def read_PositionIndex_file():
    import ast

    posIndex = {}
   # infile = open('D:/faseeh/SEMESTER 6/IR/A1/Indexes/positionIndex.txt', "r")
    infile = open(
        'C:/Users/Saleem/Documents/GitHub/IR-BooleanRetrievalModel-A1/A1/Indexes/positionIndex.txt', "r")
    contents = infile.read()
    posIndex = ast.literal_eval(contents)

    infile.close()

    return posIndex


# Function to solve both simple and boolean queries
def boolean_query(w, invertedIndex, positional_Indexes):
    operands = ['and', 'or', 'not']
    inv = invertedIndex
    #opCount = 0
    # for op in w:

    # -------- queries can be in different forms but they have some common patterns with different lengths-------

    # len = 3  has queries such has '' a AND b ''
    if(len(w) == 3):
        if(w[1] == 'and'):
            t1 = pre_processing(w[0])
            t2 = pre_processing(w[2])
            result = intersection(t1, t2, False, inv)
        else:
            t1 = pre_processing(w[0])
            t2 = pre_processing(w[2])
            result = union(t1, t2, False, inv)

    # len = 4 has queries like "a AND not b" and its combinations with " OR "
    elif(len(w) == 4):
        if(w[0] == 'not'):
            w[1] = pre_processing(w[1])
            tempResult = complement(w[1], inv)
            if(w[2] == 'and'):
                w[4] = pre_processing(w[4])
                result = intersection(tempResult, w[4], False, inv)
            else:
                w[4] = pre_processing(w[4])
                result = union(tempResult, w[4], False, inv)
        else:
            w[3] = pre_processing(w[3])
            tempResult = complement(w[3], inv)
            if(w[1] == 'and'):
                w[0] = pre_processing(w[0])
                result = intersection(w[0], tempResult, False, inv)
            else:
                w[0] = pre_processing(w[0])
                result = union(w[0], tempResult, False, inv)
        print('len 4 case')

    # len = 5 handles queries such as 'a and b and c' and variations
    # it also handle queries such as 'not a and not b'
    elif(len(w) == 5):
        if((w[1] and w[3]) in operands and (w[1] == w[3])):
            w[0] = pre_processing(w[0])
            w[2] = pre_processing(w[2])
            w[4] = pre_processing(w[4])
            # print(w[0])
            if(w[1] == 'and'):
                result = intersection(w[0], w[2], w[4], inv)
            #    result= []
            # for or condition
            if(w[1] == 'or'):
                result = union(w[0], w[2], w[4], inv)
        elif(((w[1] in operands) and (w[3] in operands)) and (w[1] != w[3])):
            if(w[1] == 'or' and w[3] == 'and'):  # to hand queries like 'a and b or c'
                print('a or b and c')
                w[0] = pre_processing(w[0])
                w[2] = pre_processing(w[2])
                w[4] = pre_processing(w[4])
                # implement some logic for this query
                tempRes = intersection(w[2], w[4], False, inv)
                result = union(w[0], tempRes, False, inv)
            else:
                w[0] = pre_processing(w[0])
                w[2] = pre_processing(w[2])
                w[4] = pre_processing(w[4])
                print('a and b or c')
                tempRes = intersection(w[0], w[2], False, inv)
                result = union(tempRes, w[4], False, inv)
        else:  # to hand queries like 'not a and not b'
            print('not a and not b')
            w[1] = pre_processing(w[1])
            w[4] = pre_processing(w[4])
            notA = complement(w[1], inv)
            notB = complement(w[4], inv)
            result = intersection(notA, notB, False, inv)

    elif(len(w) == 6):
        andCount = 0
        orCount = 0
        notIndex = 0
        for sword in w:
            notIndex = w.index('not')

            if(sword == 'and'):
                andCount += 1
            elif(sword == 'or'):
                orCount += 1
            else:
                continue

        if(andCount == 2):
            if(notIndex == 0):
                w[1] = pre_processing(w[1])
                w[3] = pre_processing(w[3])
                w[5] = pre_processing(w[5])
                res1 = complement(w[1], inv)
                res2 = intersection(res1, w[3], False, inv)
                result = intersection(res2, w[5], False, inv)
            elif(notIndex == 2):
                w[1] = pre_processing(w[0])
                w[3] = pre_processing(w[3])
                w[5] = pre_processing(w[5])
                res1 = complement(w[3], inv)
                res2 = intersection(w[0], res1, False, inv)
                result = intersection(res2, w[5], False, inv)
            else:
                w[1] = pre_processing(w[0])
                w[3] = pre_processing(w[2])
                w[5] = pre_processing(w[5])
                res1 = complement(w[5], inv)
                res2 = intersection(w[0], w[3], False, inv)
                result = intersection(res2, res1, False, inv)

        elif(orCount == 2):
            if(notIndex == 0):
                w[1] = pre_processing(w[1])
                w[3] = pre_processing(w[3])
                w[5] = pre_processing(w[5])
                res1 = complement(w[1], inv)
                res2 = union(res1, w[3], False, inv)
                result = union(res2, w[5], False, inv)
            elif(notIndex == 2):
                w[1] = pre_processing(w[0])
                w[3] = pre_processing(w[3])
                w[5] = pre_processing(w[5])
                res1 = complement(w[3], inv)
                res2 = union(w[0], res1, False, inv)
                result = union(res2, w[5], False, inv)
            else:
                w[1] = pre_processing(w[0])
                w[3] = pre_processing(w[2])
                w[5] = pre_processing(w[5])
                res1 = complement(w[5], inv)
                res2 = union(w[0], w[3], False, inv)
                result = union(res2, res1, False, inv)
        else:
            if(notIndex == 0):
                if(w[2] == 'and'):
                    w[1] = pre_processing(w[1])
                    w[3] = pre_processing(w[3])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[1], inv)
                    res2 = intersection(res1, w[3], False, inv)
                    result = union(res2, w[5], False, inv)
                else:
                    w[1] = pre_processing(w[1])
                    w[3] = pre_processing(w[3])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[1], inv)
                    res2 = intersection(w[3], w[5], False, inv)
                    result = union(res1, res2, False, inv)

            elif(notIndex == 2):
                if(w[1] == 'and'):
                    w[0] = pre_processing(w[0])
                    w[3] = pre_processing(w[3])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[3], inv)
                    res2 = intersection(w[0], res1, False, inv)
                    result = union(res2, w[5], False, inv)
                else:
                    w[0] = pre_processing(w[0])
                    w[3] = pre_processing(w[3])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[3], inv)
                    res2 = intersection(w[3], w[5], False, inv)
                    result = union(w[0], res2, False, inv)

            else:
                if(w[1] == 'and'):
                    w[0] = pre_processing(w[0])
                    w[2] = pre_processing(w[2])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[5], inv)
                    res2 = intersection(w[0], w[2], False, inv)
                    result = union(res2, res1, False, inv)
                else:
                    w[0] = pre_processing(w[0])
                    w[2] = pre_processing(w[2])
                    w[5] = pre_processing(w[5])
                    res1 = complement(w[5], inv)
                    res2 = intersection(w[2], w[5], False, inv)
                    result = union(w[0], res2, False, inv)
    else:
        if(len(w) == 8):
            if (w[2] and w[5]) == 'and':
                w[1] = pre_processing(w[1])
                w[4] = pre_processing(w[4])
                w[7] = pre_processing(w[7])
                res1 = complement(w[1], inv)
                res2 = complement(w[4], inv)
                res3 = complement(w[7], inv)
                result = intersection(res1, res2, res3, inv)

            elif(w[2] and w[5]) == 'or':
                w[1] = pre_processing(w[1])
                w[4] = pre_processing(w[4])
                w[7] = pre_processing(w[7])
                res1 = complement(w[1], inv)
                res2 = complement(w[4], inv)
                res3 = complement(w[7], inv)
                result = union(res1, res2, res3, inv)

            else:
                if(w[2] == 'and'):
                    w[1] = pre_processing(w[1])
                    w[4] = pre_processing(w[4])
                    w[7] = pre_processing(w[7])
                    res1 = complement(w[1], inv)
                    res2 = complement(w[4], inv)
                    res3 = complement(w[7], inv)
                    resultTemp = intersection(res1, res2, False, inv)
                    result = union(resultTemp, res3, False, inv)
                else:
                    w[1] = pre_processing(w[1])
                    w[4] = pre_processing(w[4])
                    w[7] = pre_processing(w[7])
                    res1 = complement(w[1], inv)
                    res2 = complement(w[4], inv)
                    res3 = complement(w[7], inv)
                    resultTemp = intersection(res1, res2, False, inv)
                    result = union(resultTemp, res3, False, inv)

    return result


# This function will solve proximity query
def proximity_query(w, Inverted_Index, Position_Index):
    result = []
    k = w[-1]
    for i in range(0, len(w)):
        w[i] = pre_processing(w[i])

    if ((w[0] in Inverted_Index) and (w[1] in Inverted_Index)):
        print('yes')
    #incomplete code
    return result


#  Intersection algorithm to intersect two or three lists
def intersection(w1, w2, w3, invertedIndex):
    l1 = l2 = l3 = result = []
    # print(w1)
    # print(w2)

    if (type(w1) is str):
        if (len(invertedIndex[w1]) == 0):
            invertedIndex[w1] = []
        l1 = invertedIndex[w1]
    else:
        l1 = w1
    if (type(w2) is str):
        # print(invertedIndex[w2])
        if (len(invertedIndex[w2]) == 0):
            invertedIndex[w2] = []
        l2 = invertedIndex[w2]
    else:
        l2 = w2
    if (type(w3) is str):
        if (len(invertedIndex[w3]) == 0):
            invertedIndex[w3] = []
        l3 = invertedIndex[w3]
    elif (type(w3) is list):
        l3 = w3
    if (type(w3) is bool):
        for i in l1:
            if i in l2:
                result.append(i)
    else:
        for i in l1:
            if ((i in l2) and (i in l3)):
                result.append(i)
    return (result)


# Union algorithm to get union of two or three  lists
def union(w1, w2, w3, invertedIndex):
    l1 = l2 = l3 = result = []
    if (type(w1) is str):
        if (len(invertedIndex[w1]) == 0):
            invertedIndex[w1] = []
        l1 = invertedIndex[w1]
    else:
        l1 = w1
    if (type(w2) is str):
        if len(invertedIndex[w2]) == 0:
            invertedIndex[w2] = []
        l2 = invertedIndex[w2]
    else:
        l2 = w2
    if (type(w3) is str):
        if len(invertedIndex[w3]) == 0:
            invertedIndex[w3] = []
        l3 = invertedIndex[w3]
    elif (type(w3) is list):
        l3 = w3
    if (type(w3) is bool):
        for i in l1:
            result.append(i)
        for i in l2:
            if i not in result:
                result.append(i)
    else:
        for i in l1:
            result.append(i)
        for i in l2:
            if i not in result:
                result.append(i)
        for i in l3:
            if i not in result:
                result.append(i)
    return (result)


# Function to return a complement of a list
def complement(w, invertedIndex):
    result = []
    if (type(w) is str):
        if(w not in invertedIndex):
            for i in range(51):
                # print(str(i))
                result.append(str(i))
        else:
            if(len(invertedIndex[w]) == 0):
                invertedIndex[w] = []

            for i in range(1, 51):
                if str(i) not in invertedIndex[w]:
                    result.append(str(i))
    else:
        for i in range(1, 51):
            if str(i) not in w:
                result.append(str(i))
    return (result)

# utility function to identify type of the query
def query_handler(query, invIndexes, posiIndex):

    qList = make_word_list(query)
    qListProx = query.split()
    print(qListProx)
    if(len(qList) == 1):
        res = simple_query(qList[0], invIndexes)
    elif ("/" in qListProx[2]):
        #print('prox')
        res = proximity_query(qList, invIndexes, posiIndex)
    else:
        #print('boolean')
        res = boolean_query(qList, invIndexes, {})
    return res


# ----------------------------------- Driver code to run the program ------------------------------------------------
invIndexes1 = read_InvertedIndex_file()
posIndexes1 = read_PositionIndex_file()


# ----------- To implement a UI for an easy interaction with the program -------------------------
window = tkinter.Tk()
window.title("Boolean Retrieval Model")
window.geometry('550x50')

labelone = ttk.Label(window, text="Enter Query : ", anchor='center')
labelone.grid(row=0, column=0)

inp = tkinter.StringVar()

userentry = ttk.Entry(window, width=50, textvariable=inp)
userentry.grid(row=0, column=1)


def action():
    result = query_handler(inp.get(), invIndexes1, posIndexes1)
    if(len(result) == 0):
        messagebox.showinfo('Retrieved Documents', 'No Result Found')
    else:
        messagebox.showinfo('Retrieved Documents', result)


btn = ttk.Button(window, text="Submit", command=action)
btn.grid(row=0, column=2)

window.mainloop()
