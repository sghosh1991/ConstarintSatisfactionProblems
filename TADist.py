#from mx.DateTime import *
from datetime import *
import time
import copy
import getopt,sys

(CLASSTIME,RECITTIME,TANUM,TAREQCLASS,PREREQS,)=range(5);
(SCHEDULE,SKILLS)=range(2);
(DAY,TIME)=range(2);
(SUCCESS,ERROR)=range(2);
(FULLMATCH)=range(8,9);
assignAll=0;

assignList=[]

def buildTAReqs(TAReqs,courseDict):
    for key,value in courseDict.items():
        print "building TAReqs key : %s, value %s, number of TA is : %s\n" %(key,value,value[TANUM])
        TAReqs[key]=value[TANUM]
        print "*******TAReq*********"
        print TAReqs

def coursesLeft(TAReqs):
    sum=0
    for value in TAReqs.values():
        sum=sum+value
    return sum

def conflicts(Tvalue, Cvalue):

    #Take care of the various conflicts
    #1. Skill conflict
    #2. Recitation Time Conflict
    #3. Class Conflict

    #safeDiff = TimeDelta(minutes=90);
    safeDiffRecitation = timedelta(minutes=90);
    safeDiffClass = timedelta(minutes=80)
    # Consider if TA doesn't satisfy some of the prerequisites for the course
    #Here assumption is that TA must satisfy all the course requirements to be assigned.
    #print(Cvalue)
    for Citem in Cvalue[PREREQS]:
        if Citem not in Tvalue[SKILLS]:
            return "YES";
    
    for Titem in Tvalue[SCHEDULE]:
        T=Titem.split(" ")
        # Consider the conlicts between TA schedule and Recitation timings


        if not Cvalue[RECITTIME]=="NO_RECITATION":

            for Citem in Cvalue[RECITTIME]:
                #print "--citem now %s" %Citem;
                C=Citem.split(" ");
                #print "--c now %s" %C;
                if C[DAY] == T[DAY]:
                    if abs(datetime.strptime(C[TIME],"%H:%M")-datetime.strptime(T[TIME],"%H:%M")) < safeDiffRecitation:
                 #       print "C is %s" % C;
                  #      print "T is %s" % T;
                   #     print "Titem : %s" % Titem;
                    #    print "Citem : %s" % Citem;
                        return "YES"

        # Consider the conflicts between class meeting time and TA schedule if TA is required to attend classes                
        if Cvalue[TAREQCLASS]=="YES":
            for Citem in Cvalue[CLASSTIME]:
                C=Citem.split(" ");
                if C[DAY] == T[DAY]:
                    if abs(datetime.strptime(C[TIME],"%H:%M")-datetime.strptime(T[TIME],"%H:%M")) < safeDiffClass:
                 #       print "C is %s" % C;
                  #      print "T is %s" % T;
                   #     print "Titem : %s" % Titem;
                    #    print "Citem : %s" % Citem;
                        return "YES";
    return "NO";

    

def buildAvail(TADict,courseDict,availDict):

    print("In buildAvail")
    for Tkey,Tvalue in TADict.items():
        for Ckey,Cvalue in courseDict.items():
            #print(Ckey)
            if conflicts(Tvalue,Cvalue)=="NO":

                if Tkey not in availDict:
                    availDict[Tkey]=[Ckey]
                else:
                    availDict[Tkey].append(Ckey)

    for value in availDict.values():
        value.sort()

    print("*********AvailDict************")
    print availDict



    
def assign(searchType,inputFile):
    global assignList
    global assignAll
    stringList=[]
    courseDict = {}
    availDict={}
    TADict = {}
    tempList=[]
    count = 0
    prevCount = -1
    f = open(inputFile, 'r')
    assignCourse={}
    assignTA={}

    print "In assign"

    for line in f:
        #print line
        if line=='\n':
            count = count + 1
            continue

        if count>prevCount:
            count = prevCount+1
            prevCount = count

        stringList = line.split(',')
        #print stringList

        #for class times
        if count==0:
            courseDict[stringList[0]] = []
            for i in range(1, len(stringList)-1, 2):
                #tempList.append((stringList[i] + " " + stringList[i+1]).strip().replace('\n',''));
                tempList.append((stringList[i].strip()+ " " + stringList[i+1].strip()).replace('\n',''))
            courseDict[stringList[0]].append(tuple(tempList))
            tempList = []

        #for recitation times
        if count==1:
            for i in range(1, len(stringList)-1, 2):
                #tempList.append((stringList[i] + " " + stringList[i+1]).strip().replace('\n',''));
                tempList.append((stringList[i].strip()+ " " + stringList[i+1].strip()).replace('\n',''))
            courseDict[stringList[0]].append(tuple(tempList));
            tempList = []

        #for number of students and whether ta has to attend
        if count==2:
            noOfStd = int(stringList[1].strip().replace('\n',''))
            if noOfStd<25:
                tempTANum = 0
            if noOfStd>=25 and noOfStd<40:
                tempTANum = 1
            if noOfStd>=40 and noOfStd<60:
                tempTANum = 3
            if noOfStd>=60:
                tempTANum = 4

            #courseDict[stringList[0]].append(int(stringList[1].strip().replace('\n','')));
            courseDict[stringList[0]].append(tempTANum)
            courseDict[stringList[0]].append(stringList[2].strip().replace('\n',''))
            tempList = []


        #for pre requisites
        if count==3:
            for i in range(1, len(stringList), 1):
                tempList.append((stringList[i]).strip().replace('\n',''))
            courseDict[stringList[0]].append(tuple(tempList))
            tempList = []

        #for ta responsibility
        if count==4:
            #print("In count 4")
            #print(stringList)
            TADict[stringList[0]+"0"] = []
            TADict[stringList[0]+"1"] = []
            for i in range(1, len(stringList)-1, 2):
                #tempList.append((stringList[i] + " " + stringList[i+1]).strip().replace('\n',''));
                tempList.append((stringList[i].strip()+ " " + stringList[i+1].strip()).replace('\n',''))
            TADict[stringList[0]+"0"].append(tuple(tempList))
            TADict[stringList[0]+"1"].append(tuple(tempList))
            tempList = []

        #for ta skills
        if count==5:
            for i in range(1, len(stringList), 1):
                tempList.append((stringList[i]).strip().replace('\n',''))
            TADict[stringList[0]+"0"].append(tuple(tempList))
            TADict[stringList[0]+"1"].append(tuple(tempList))
            tempList = []
    f.close()

    #print "After file Parsing"
    #print "course dictionary ......"

    for key,value in courseDict.items():
        if(len(value)==4):
            value.insert(1,"NO_RECITATION")


    #print courseDict

    #print "TA Dictionary"
    #print TADict
    

    TAReqs={}
    TADistDict={}
    timeTaken=0
    buildAvail(TADict,courseDict,availDict)
    assignAll=len(availDict)
    buildTAReqs(TAReqs,courseDict)
    #print TAReqs
    t1=time.clock()
    if searchType=="BT":
        #pass
        SatBT(availDict,TAReqs,TADistDict,1)
    elif searchType=="FC":
        SatBTFC(availDict,TAReqs,TADistDict)
    elif searchType=="CP":
        SatBTFCCP(availDict,TAReqs,TADistDict)
    else:
        return "Invalid Argument specified. Give BT/FC/CP"
    t2=time.clock()
    print "Final Assignments:"
    for item in assignList:
        print item
    timeTaken=t2-t1
    print "time taken :"
    print timeTaken

    addedToTAList = False

    print ("\n+++++++Assign List+++++\n" )

    for item in assignList:
        print item


    i=0
    for item in assignList:
        addedToTAList = False
        addedToCourseList = False
        for key,value in item.items():
            name=key.rstrip('10')
            #print name
            #print(value)
            #print(assignTA.keys())
            if name not in assignTA:
                assignTA[name]=[[value,.5]]
            else:
                for taAssignment in assignTA[name]:

                    if value == taAssignment[0]:

                        #print("Adding to assignTA")
                        taAssignment[1]+=.5
                        addedToTAList = True
                        break

                if(not addedToTAList):
                    assignTA[name].append([value,.5])

            if value not in assignCourse:
                assignCourse[value]=[[name,.5]]
            else:

                for courseAssignment in assignCourse[value]:

                    if name == courseAssignment[0]:

                        #print("Adding to assignTA")
                        courseAssignment[1]+=.5
                        addedToCourseList = True
                        break

                if(not addedToCourseList):
                    assignCourse[value].append([name,.5])



                # if name not in assignCourse[value]:
                #     assignCourse[value].append([name,.5])
                # else:
                #     print("Adding to assignCourse")
                #     assignCourse[value][1]+=.5


        print("Assignment " + str(i))
        print assignTA
        print assignCourse
        print


        i += 1
        assignTA={}
        assignCourse={}

            

def findMRV(availDict):

    #Calculate the TA with the least number of available allocations

    minVal=99999
    minKey="XXXXX"
    for key,value in availDict.items():
        if len(value)<minVal:
            minVal=len(value)
            minKey=key
    return minKey


def SatBTP(availDict,TAReqs,TADistDict,level):
    global assignList
    global assignAll
    assigned=0
    TAReqsNext={}
    availDictNext={}
    TADistDictNext={}
    print "inside BTSat"
    print "\n\n******Available Dict is******"
    print availDict

    maxLen = max([len(i) for i in availDict])

    print(availDict.keys())

    for minKey in availDict.keys():

        print("\n\n*****TRYING with minKey = " + str(minKey) + " Level is :" + str(level))
        #minKey=findMRV(availDict,i)
        print "The minimum key is : " + minKey
        for Ckey in availDict[minKey]: #TAReqs.keys():
            print "minKey : %s, Ckey : %s" %(minKey,Ckey)
            print availDict[minKey];
            if Ckey in TAReqs.keys(): #availDict[Tkey]:
                TADistDict[minKey]=Ckey
                availDictNext=copy.deepcopy(availDict)
                del availDictNext[minKey]
                print "TADistDict is:"
                print TADistDict
                TAReqsNext=copy.deepcopy(TAReqs)
                TAReqsNext[Ckey]-=1
                if TAReqsNext[Ckey]<=0:
                    del TAReqsNext[Ckey]

                assigned=len(TADistDict)
                if len(availDictNext)<=0 or len(TAReqsNext)<=0:
                    print "End of tree reached"
                    print "--------------------------------------------------------------------"
                    print TADistDict
                    #print "assigned is :%d and assignAll is %d" %(assigned,assignAll);
                    if assigned==assignAll:#FULLMATCH:
                        print ("Appending : \n" + str(TADistDict))
                        x = copy.deepcopy(TADistDict)
                        assignList.append(x)
                        print ("Assignlist till now\n" + str(assignList))
                        print "Success Finally"
                        print "--------------------------------------------------------------------"
                    continue
                    #return SUCCESS;
                    #else:
                        #availDictNext=copy.deepcopy(availDict);
                        #if Tkey in availDictNext.keys():
                            #TAListNext.remove(Tkey);
                            #del availDictNext[Tkey];


                print "Calling satbt for :"
                print availDictNext
                print TAReqsNext
                TADistDictNext=copy.deepcopy(TADistDict)
                SatBT(availDictNext,TAReqsNext,TADistDictNext,level+1)
                del TADistDict[minKey]


                #if SatBTFC(availDictNext,TAReqsNext,TADistDictNext)== SUCCESS:
                    #return SUCCESS;#continue;

            else:
                print "No Solution Found..... "
                #print TADistDict;
                #return ERROR;




def SatBT(availDict,TAReqs,TADistDict,level):
    global assignList
    global assignAll
    assigned=0
    TAReqsNext={}
    availDictNext={}
    TADistDictNext={}
    #print "inside BTSat"
    #print "\n\n******Available Dict is******"
    #print availDict

    maxLen = max([len(i) for i in availDict])

    print("***** LEVEL " + str(level) + "*****")
    minKey=findMRV(availDict)
    print "The minimum key is : " + minKey
    for Ckey in availDict[minKey]: #TAReqs.keys():
        #print "minKey : %s, Ckey : %s" %(minKey,Ckey)
        #print availDict[minKey];
        if Ckey in TAReqs.keys(): #availDict[Tkey]:
            TADistDict[minKey]=Ckey
            availDictNext=copy.deepcopy(availDict)
            del availDictNext[minKey]
            print "TADistDict is:"
            print TADistDict
            TAReqsNext=copy.deepcopy(TAReqs)
            TAReqsNext[Ckey]-=1
            if TAReqsNext[Ckey]<=0:
                del TAReqsNext[Ckey]

            assigned=len(TADistDict)
            if len(availDictNext)<=0 or len(TAReqsNext)<=0:
                print "End of tree reached"
                print "--------------------------------------------------------------------"
                print TADistDict
                #print "assigned is :%d and assignAll is %d" %(assigned,assignAll);
                if assigned==assignAll:#FULLMATCH:
                    print ("Appending : \n" + str(TADistDict))
                    x = copy.deepcopy(TADistDict)
                    assignList.append(x)
                    print ("Assignlist till now\n" + str(assignList))
                    print "Success Finally"
                    print "--------------------------------------------------------------------"
                continue
                #return SUCCESS;
                #else:
                    #availDictNext=copy.deepcopy(availDict);
                    #if Tkey in availDictNext.keys():
                        #TAListNext.remove(Tkey);
                        #del availDictNext[Tkey];


            print "Calling satbt for :"
            print availDictNext
            print TAReqsNext
            TADistDictNext=copy.deepcopy(TADistDict)
            SatBT(availDictNext,TAReqsNext,TADistDictNext,level+1)
            del TADistDict[minKey]


            #if SatBTFC(availDictNext,TAReqsNext,TADistDictNext)== SUCCESS:
                #return SUCCESS;#continue;

        else:
            print "No Solution Found..... "
            #print TADistDict;
            #return ERROR;



def SatBTFC(availDict,TAReqs,TADistDict):
    global assignList
    global assignAll
    assigned=0
    TAReqsNext={}
    availDictNext={}
    TADistDictNext={}
    print "\n\n"
    print "inside SatBTFC"
    print availDict
    minKey=findMRV(availDict)
    print minKey
    for Ckey in availDict[minKey]: #TAReqs.keys():
        print "minKey : %s, Ckey : %s" %(minKey,Ckey)
        #print availDict[minKey];
        if Ckey in TAReqs.keys(): #availDict[Tkey]:
            TADistDict[minKey]=Ckey
            availDictNext=copy.deepcopy(availDict)
            del availDictNext[minKey]
            print "TADistDict is:"
            print TADistDict
            TAReqsNext=copy.deepcopy(TAReqs)
            TAReqsNext[Ckey]-=1
            if TAReqsNext[Ckey]<=0:
                del TAReqsNext[Ckey]
                for key,value in availDictNext.items():
                    #Forward checking will remove the used value from the domain of all the remaining nodes
                    print "availDictNext:[%s]=%s" % (key,value)
                    if Ckey in value:
                        if len(value)>1:
                            value.remove(Ckey)
                        else:
                            print "removing from list element %s" %key
                            del availDictNext[key]
                    
            assigned=len(TADistDict)
            if len(availDictNext)<=0 or len(TAReqsNext)<=0:
                print "End of tree reached"
                print "--------------------------------------------------------------------"
                print TADistDict;
                #print "assigned is :%d and assignAll is %d" %(assigned,assignAll);
                if assigned==assignAll:#FULLMATCH:
                    x = copy.deepcopy(TADistDict)
                    assignList.append(x)
                    print "Success Finally"
                    print "--------------------------------------------------------------------"
                continue
                #return SUCCESS;
                #else:
                    #availDictNext=copy.deepcopy(availDict);
                    #if Tkey in availDictNext.keys():
                        #TAListNext.remove(Tkey);
                        #del availDictNext[Tkey];
                
                
            print "Calling satbtfc for :"
            print availDictNext
            print TAReqsNext
            TADistDictNext=copy.deepcopy(TADistDict)
            SatBTFC(availDictNext,TAReqsNext,TADistDictNext)
            #if SatBTFC(availDictNext,TAReqsNext,TADistDictNext)== SUCCESS:
                #return SUCCESS;#continue;
                
        else:
            print "No Solution Found..... "
            print TADistDict
            #return ERROR;

                
def SatBTFCCP(availDict,TAReqs,TADistDict):
    global assignList
    global assignAll
    assigned=0
    TAReqsNext={}
    availDictNext={}
    TADistDictNext={}
    print "\n\n";
    print "inside SatBTFC"
    print availDict
    minKey=findMRV(availDict)
    print minKey;
    for Ckey in availDict[minKey]: #TAReqs.keys():
        print "minKey : %s, Ckey : %s" %(minKey,Ckey)
        #print availDict;
        if Ckey in TAReqs.keys(): #availDict[Tkey]:
            TADistDict[minKey]=Ckey;
            availDictNext=copy.deepcopy(availDict);
            del availDictNext[minKey];
            print "TADistDict is:";
            print TADistDict;
            TAReqsNext=copy.deepcopy(TAReqs)
            TAReqsNext[Ckey]-=1
            if TAReqsNext[Ckey]<=0:
                del TAReqsNext[Ckey]
                for key,value in availDictNext.items():
                    print "availDictNext:[%s]=%s" % (key,value)
                    if Ckey in value:
                        if len(value)>1:
                            value.remove(Ckey)
                        else:
                            print "removing from list elemet %s" %key
                            del availDictNext[key]
            assigned=len(TADistDict)
            if len(availDictNext)<=0 or len(TAReqsNext)<=0:
                print "End of tree reached"
                print "--------------------------------------------------------------------"
                print TADistDict
                #print "assigned is :%d and assignAll is %d" %(assigned,assignAll);
                if assigned==assignAll:#FULLMATCH:
                    x = copy.deepcopy(TADistDict)
                    assignList.append(x)
                    print "Success Finally";
                    print "--------------------------------------------------------------------"
                continue
                #return SUCCESS;
            # Constraint check for the next level of the tree    
            if assigned+coursesLeft(TAReqsNext)<assignAll:
                print("\nConstraint Continuing....\n")
                continue
                
            print "Calling satbtfc for :"
            print availDictNext
            print TAReqsNext;
            TADistDictNext=copy.deepcopy(TADistDict);
            SatBTFCCP(availDictNext,TAReqsNext,TADistDictNext)
            #if SatBTFC(availDictNext,TAReqsNext,TADistDictNext)== SUCCESS:
                #return SUCCESS;#continue;
                
        else:
            print "No Solution Found..... "
            print TADistDict;
            #return ERROR;


def main(argv):

    inputFile = ''
    algorithm = ''


    try:
        opts, args = getopt.getopt(argv,"i:a:",["ifile=","algorithm="])
    except getopt.GetoptError:
        print "test.py -i <inputfile> -a <algorithm>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-a':
            algorithm = arg
            #print algorithm

        elif opt in ("-i", "--ifile"):
            inputFile = arg
            if inputFile =="":
                print "test.py -i <inputfile> -o <outputfile>"
                sys.exit(2)


    assign(algorithm,inputFile)


if __name__ == "__main__":
    main(sys.argv[1:])