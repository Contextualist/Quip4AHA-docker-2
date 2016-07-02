# -*- coding: utf-8 -*-  
'''
Adapt to fit Flask in GAE
NOTICE:  To update the broadcast structure or host list, go to quip4aha.py.

Main idea: 
  i. group sections into portions
  ii. then distribute the portions to each host, so that
      a. the STD of hosts' word counts is minimized *future feature
      b. the continuity is maximized
B_   block(column)
S_   section(paragraph)
P_   portion(read by a host)
_N   number, count
For those who are new to Python, remember, 
1. The index of a Python list starts with 0.
2. Variables in Python are pointers. So to copy a list but not the
   address of the list, use a=copy.deepcopy(b), instead of a=b.
Progress: Hope to improve efficiency of DISTRIBUTE
'''

from HTMLParser import HTMLParser
import re

class MyHTMLParser(HTMLParser):
    def __init__(self, KeyWord, BN):
        HTMLParser.__init__(self)
        self.__KeyWord = KeyWord
        self.__BN = BN
        self.__BNNow = -1
        self.__SNNow = 0
        self.__newline = 0 #when there are total two <p> and <br/> between two data, new section
        self.__SIDNow = ''
        self.SWordCount = []
        self.SID = []

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.__SIDNow = attrs[0][1] #extract the ID attr
            self.__newline += 1

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self.__newline += 1

    def handle_data(self, data):
        wordcount = len(re.findall(r"\b\w+\b", data))
        if wordcount == 0: return 0
        if (self.__BNNow+1<=self.__BN-1 and data.find(self.__KeyWord[self.__BNNow+1])!=-1):
            self.__BNNow += 1 #new block
            self.__SNNow = 0
            self.SWordCount += [[0]]
            self.SID += [[self.__SIDNow]]
        elif self.__newline>=2:
            self.__SNNow += 1 #new section
            self.SWordCount[self.__BNNow] += [0]
            self.SID[self.__BNNow] += [self.__SIDNow]
        self.SWordCount[self.__BNNow][self.__SNNow] += wordcount
        self.__newline = 0

from quip4aha import QuipClient4AHA, InvalidOperation
import copy

class AssignHost(object):

    def __init__(self, KeyWord=QuipClient4AHA.KEYWORD, BWeight=QuipClient4AHA.B_WEIGHT,
                 Host=QuipClient4AHA.HOST, PNperB=QuipClient4AHA.PN_PER_B):
        '''
        ==================INITIALIATION==================
        '''
        #--------------------Block----------------------
        self.KeyWord = KeyWord
        self.BN = len(self.KeyWord)
        self.BWeight = BWeight # B[]
        #--------------------Section----------------------
        self.SWordCount = []
        self.SID = []
        self.SNperB = []     # B[SN]
        #---------------------Host----------------------
        self.Host = Host if not Host[0] else QuipClient4AHA.HOST
        import random
        random.shuffle(self.Host)
        self.HostN = len(self.Host)
        self.HostWordCount = [0.00] * self.HostN
        self.Ans_HostWordCountSTD = 1000.00
        #--------------------Portion----------------------
        self.PNperB = PNperB # B[PN]
        self.CutSign = [[0]*pn for pn in self.PNperB]
        self.PWordCount = [[0]*pn for pn in self.PNperB]
        self.PAssign = [[0]*pn for pn in self.PNperB]
        self.IsBetterPDivision = 0
        #self.Continuity = 0
        self.Ans_CutSign = []
        self.Ans_PAssign = []
        #self.Ans_Continuity = 0
        #----------------------DOC----------------------
        self.client = QuipClient4AHA()

    def _std(self, d):
        m = 0.00
        for x in d: m += x
        m = m / len(d)
        s = 0.00
        for x in d: s += ( x - m ) ** 2
        return (s / len(d)) ** 0.5

    def _AssignP(self, b, p):
        op = set(range(self.HostN))
        if p == 0: #forbid the host to cross a block
            op -= {self.PAssign[b-1][self.PNperB[b-1]-1]}
        for i in op:
            self.PAssign[b][p] = i
            self.HostWordCount[i] += self.PWordCount[b][p]
            #if (p!=0)&&(i!=self.PAssign[b][p-1]): self.Continuity += 1
            if p == self.PNperB[b]-1:
                if b == self.BN-1:
                    t = self._std(self.HostWordCount)
                    if t < self.Ans_HostWordCountSTD:
                        self.Ans_HostWordCountSTD = t
                        self.Ans_PAssign = copy.deepcopy(self.PAssign)
                        self.IsBetterPDivision = 1
                else:
                    self._AssignP(b+1,0)
            else:
                self._AssignP(b,p+1)
            self.HostWordCount[i] -= self.PWordCount[b][p]

    def _GenerateP(self, b, p): #block 'b' from 'CutSign[b,p]+1' to the end start dividing the 'p'th sections
        if p == self.PNperB[b]-1:
            self.PWordCount[b][self.PNperB[b]-1] = sum(self.SWordCount[b][self.CutSign[b][p]:])
            if b < self.BN-1:
                self.CutSign[b+1][0] = 0
                self._GenerateP(b+1,0)   #next B
            else:
                self.IsBetterPDivision = 0
                self.HostWordCount = [0] * self.HostN
                self.PAssign[0][0] = 0
                self.HostWordCount[0] += self.PWordCount[0][0]
                if self.PNperB[0]>1:
                    self._AssignP(0, 1)
                else: 
                    self._AssignP(1, 0) #start assigning hosts
                if self.IsBetterPDivision: 
                    self.Ans_CutSign = copy.deepcopy(self.CutSign)
        else:
            self.PWordCount[b][p] = 0
            for i in xrange(self.CutSign[b][p]+1,self.SNperB[b]):
                self.PWordCount[b][p] += self.SWordCount[b][i-1]
                self.CutSign[b][p+1] = i
                self._GenerateP(b,p+1)


    def do(self):
        #raise InvalidOperation("The page is under construction. . .")
        '''
        ====================DOC CATCHER====================
        '''
        self.docID = self.client.get_latest_script_ID()
        self.thread = self.client.get_thread(id=self.docID)
        '''
        #docURL = "Z0R5AhbLjUxu" # test doc 0309-c
        docURL = "YHb8AyYLNgvi" # test doc 0309-cc
        self.thread = self.client.get_thread(id=docURL)
        self.docID = self.thread['thread']['id']
        '''
        '''
        ====================DOC PRE-PROCESSOR====================
        extract SWordCount and SID
        '''
        if self.thread["html"].find(r'<i>//')!=-1:
            raise InvalidOperation("Redundancy Warning: The script has already been divided and assigned!")
        self.docHTML = self.thread["html"].decode('utf-8').encode('ascii', 'ignore') #clear all non-ascii
        self.docHTML = re.sub(r'<h1.+<\/h1>', '', self.docHTML, count=1) #delete the header
        
        parser = MyHTMLParser(self.KeyWord, self.BN)
        parser.feed(self.docHTML)
        
        '''
        =====================SETTINGS====================
        '''    
        self.SWordCount = parser.SWordCount
        self.SWordCount = [[swc*self.BWeight[b] for swc in self.SWordCount[b]] for b in xrange(self.BN)] # B[S[]], weighted
        self.SID = parser.SID
        self.SNperB = [len(b) for b in self.SWordCount]     # B[SN]
        for i in xrange(self.BN):
            if self.PNperB[i] > self.SNperB[i]: self.PNperB[i] = self.SNperB[i]
        self.CutSign[0][0] = 0
        
        '''
        ====================DISTRIBUTE(S->P)====================
        '''
        self._GenerateP(0, 0)
        #    CutSign =   [[0],   [0],     [],       , []] # B[P[SN]] generated first
        #    PWordCount =[ ,      ,   [],       , []] # B[P[]] generated first
        #        PAssign =   [[0],   [1],     [],       , []] # B[P[Host]] subsequent
        
        '''
        ====================POST DIVISIONS====================
        '''
        for b in xrange(self.BN):
            for p in xrange(self.PNperB[b]):
                if (p==0 or self.Ans_PAssign[b][p]!=self.Ans_PAssign[b][p-1]): #need not to care about cross block
                    self.client.edit_document(thread_id=self.docID, content=r"<i>//%s</i>" % (self.Host[self.Ans_PAssign[b][p]]), format="html",
                                         operation=self.client.BEFORE_SECTION, section_id=self.SID[b][self.Ans_CutSign[b][p]])
        return "Done!"
        
if __name__=="__main__":
    AssignAction = AssignHost()
    AssignAction.do()
