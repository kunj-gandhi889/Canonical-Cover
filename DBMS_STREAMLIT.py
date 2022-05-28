import time
import streamlit as st
import re

st. set_page_config(layout="wide")

data = """ Finding Canonical Cover involves 4 Steps  
1.  Decomposition --> (Ex. AB->CDE  transforms into AB->C AB->D and AB->E) 
2.  Removing Extra/Redundant FDs (redundant FD --> present and absent of FD do not affect closure)
3.  Removing Extra/Redundant Attributes from Leftside (If composite attribute on left side of FD , then check if lesser attribute can identify the right side attribute )
4.  Composition --> (Ex. A->C A->D and A->E transforms into A->CDE) """

# 1) removing duplicate FD
def duplicate(newList):
    new = []
    for i in newList:
        if(i not in new):
            new.append(i)
    return new 

# 2) decomposition function
def decomposition(newList):
    decomposedList = []
    for i in newList:
        splitfd = i.split("->")
        if(len(splitfd[1])>1):
            extra = list(splitfd[1])
            for j in extra:
                decomposedList.append("->".join([splitfd[0],j]))
        else:
            decomposedList.append(i)
    return decomposedList

# 3) finding Closure of FD
def closure(fd,fdList):  # fdList -> containing all FDs ,fd -> particular FD (attribute or set of attributes)
    fd = fd.split("->")
    attrClosure = []
    leftSide = []
    rightSide = []
    attrClosure+=list(fd[0])   # every set of attribute can determine itself
    # attrClosure.append(fd[1]) 
    # print("initial attrClosure : ",attrClosure)
    for i in fdList:
        leftSide.append(i.split("->")[0])
    # print("leftside attr : ",leftSide)
    for i in fdList:
        rightSide.append(i.split("->")[1])
    while(True):   # for queue like
        prevClosure = attrClosure.copy()
        for value in range(len(leftSide)):  # all value of leftside in attrClosure
            if(all(item in attrClosure  for item in list(leftSide[value]))):
                attrClosure.append(rightSide[value])
        attrClosure = duplicate(attrClosure)
        # print("prevattrClosure : ",prevClosure)
        # print("newattrClosure : ",attrClosure)
        if(prevClosure == attrClosure):
            return duplicate(attrClosure)

# 4) finding extraneous FD and removing it --> (i.e. only considering essential FD in final FDs)
def removeExtraFD(fdList):  # fdlist --> decomposed list
    for _ in fdList:
        for j in fdList:
            tempList=fdList.copy()
            tempList.remove(j)
            if(sorted(closure(j,tempList))==sorted(closure(j,fdList))): # if the closure changes by removing the FD , then it is essential otherwise redundant
                fdList.remove(j)
    return fdList

# 5) removing extra attributes
def removeExtraAttribute(fdList):
    for i in range(len(fdList)):
        fd = fdList[i].split("->")[0]   # leftside of FDs
        fd_value = fdList[i].split("->")[1]   # rightside of FDs
        if(len(fd)>1):
            for j in range(len(fd)):
                tempAttr=fd[:j]+fd[j+1:]
                # print(tempAttr)
                a = "->".join([tempAttr,fd_value])
                # print(closure(tempAttr,fdList))
                if((fd[j] in closure(tempAttr,fdList)) and (fdList[i] in fdList)):
                    fdList.append(a)
                    fdList.remove(fdList[i])
    return fdList


# 6) Composition
def composition(fdList):
    for i in fdList:
        fd=i.split('->')
        tempList=[]
        for j in fdList:
            fdTemp=j.split('->')
            if(fd[0]==fdTemp[0] and (j not in tempList)):
                tempList.append(j)
        
        if(len(tempList)>1):
            for t in tempList:
                fdList.remove(t)
            tempAttr = ""
            for i in tempList:
                temp = i.split("->")
                tempAttr+= temp[1]
            new = temp[0] +"->"+ tempAttr
            fdList.append(new)
    
    return fdList


# MAIN PROGRAM --> GUI 
# title
st.markdown("<h2 align='Center' style='color:red;font-family:Segoe UI'>CANONICAL COVER / IRREDUCIBLE FORM OF FD</h2>",unsafe_allow_html=True)
# no. of attribute
n = st.number_input("• Enter No. of Attribute in Relational Schema",min_value=0,max_value=100)

st.info("Note : Enter Single Character Attributes Only")


# getting attribute list
AttrList = st.text_input("• Enter Comma Seperated Attribute").split(",")
# remove duplicate
AttrList = duplicate(AttrList)
if(n==0):
    pass
elif(len(AttrList) != n):
    st.error(f"No. of Attributes not equal to {int(n)}")
else:
    for i in range(len(AttrList)):
        if(AttrList[i]==""):
            st.error(f"Empty Attribute {i+1}")
            break
        if(len(AttrList[i])!=1):
            st.error(f"Multi Charactered Attribute {i+1}")
            break
    else:
        st.markdown(f"<h3>Relational Schema -> R({','.join(AttrList)})</h3>",unsafe_allow_html=True)



# getting all the functional dependency

def stripList(list):
    for i in range(len(list)):
        list[i] = list[i].strip()
    return list

fdList =[]
pattern = r"^[A-Za-z]+.*->.*[A-Za-z]+$"
st.markdown("<h4 align='center' style='color:green'>Enter Functional Dependencies<h4>",unsafe_allow_html=True)
fd = ""
st.info("Note : Enter end to finalize your FD")
count = 1
while(True):
    fd = st.text_input(f"Enter FD {count} (end to exit) : ",key=count).strip()
    if(fd.lower()=="end"):
        break
    if(re.match(pattern,fd,flags=re.MULTILINE)):
        tempAttr = fd.split("->")
        tempAttr = stripList(tempAttr)
        allAttr = list(set("".join(tempAttr)))
        check = all(item in AttrList for item in allAttr)
        if(check):
            final_fd = "->".join(tempAttr)
            if(final_fd in fdList):
                st.error("FD Already Present!")
                continue
            count+=1
            fdList.append(final_fd)
        else:
            st.error("Attribute in FD is not in Relation!")
    else:
        if(fd==""):
            pass
        else:
            st.error("Invalid Syntax For FD (it should be like α->β )")
        continue

tempList = fdList.copy()

st.markdown(f"<h3 align='center' style='color:green'>F꜀ -> {{ {' , '.join(fdList)} }}</h3>",unsafe_allow_html=True)

# now applying all steps of canonical cover

st.info(data)

col1,col2,col3 = st.columns([43,20,37])
if(col2.button("Find Canonical Cover")):
    col3,col4,col5 = st.columns([45,20,35])
    with col4:
        with st.spinner("Solving..."):
            time.sleep(2)

    # step 1

    st.markdown("<h4 align='center' style='text-decoration:underline;color:red'>Step 1 : After Decomposing F꜀</h4>",unsafe_allow_html=True)
    fdList = duplicate(decomposition(fdList))
    st.markdown(f"<h3 align='center' style='color:green'>F꜀ -> {{ {' , '.join(fdList)} }}</h3>",unsafe_allow_html=True)

    # step 2

    st.markdown("<h4 align='center' style='text-decoration:underline;color:red'>Step 2 : After Removing Extraneous FDs</h4>",unsafe_allow_html=True)
    fdList = duplicate(removeExtraFD(fdList))
    st.markdown(f"<h3 align='center' style='color:green'>F꜀ -> {{ {' , '.join(fdList)} }}</h3>",unsafe_allow_html=True)

    # step 3

    st.markdown("<h4 align='center' style='text-decoration:underline;color:red'>Step 3 : After Removing Extra Attributes</h4>",unsafe_allow_html=True)
    fdList = duplicate(removeExtraAttribute(fdList))
    st.markdown(f"<h3 align='center' style='color:green'>F꜀ -> {{ {' , '.join(fdList)} }}</h3>",unsafe_allow_html=True)

    # step 4

    st.markdown("<h4 align='center' style='text-decoration:underline;color:red'>Step 4 : After Composition</h4>",unsafe_allow_html=True)
    fdList = duplicate(composition(fdList))
    st.markdown(f"<h3 align='center' style='color:green'>F꜀ -> {{ {' , '.join(fdList)} }}</h3>",unsafe_allow_html=True)

    # st.success(f"FD = {{ {' , '.join(fdList)} }} is Canonical Cover of FD = {{ {' , '.join(tempList)} }}")
    st.markdown(f"<h2 align='center' style='border:2px solid red;border-radius:25px;background-color:#fcf4d7;color:black;padding:30px;margin-top:20px'>FD = {{ {' , '.join(fdList)} }} is Canonical Cover of FD = {{ {' , '.join(tempList)} }}</h2>",unsafe_allow_html=True)

    st.markdown("<br><br><h3 align='right'>PREPARED BY</h3>",unsafe_allow_html=True)
    st.markdown("<h4 align='right' style='font-family:Segoe UI;color:grey;'>RAJDEEP BODAR 20BCE032<br>DIVYRAJ CHUDASAMA 20BCE046<br>KUNJ GANDHI 20BCE073</h4>",unsafe_allow_html=True)