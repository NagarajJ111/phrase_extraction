from tkinter import Button
from unittest import result
import pandas as pd
import streamlit as st
from samples import texts
import re
import nltk
from tkinter import Button
from nltk.tokenize import RegexpTokenizer
cap= "([A-Z]*)"
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](a-b)"
digits = "([0-9])"

@st.cache(allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def readdata(data):
    # fp = open("text.txt")
    #data = fp.read()
    sec=split(data)
    wc,w,j=[],[],0
    for i in range(len(sec)):
    #print(i,end='\n')
        for word in sec[i].split():
            w.append(word)
            j=j+1 
        wc.append(j)
        j=0
    return sec,w,wc


def split(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"",text)
    if "..." in text: text = text.replace("...","")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+alphabets,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+alphabets+"[.] "+alphabets," \\1<stop> \\2",text)
    text = re.sub(" "+alphabets+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    text = re.sub(r'\d', "", text) 
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    for i in ['[]','()','[',']','(',')','.',',',';',':','?','!','%']:
        text = text.replace(i,"<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = [s.strip() for s in sentences]
    sentences = [s for s in sentences if len(s)>5]
    sentences = [s for s in sentences if s.__contains__(" ")]
    return sentences

 

def createNgram (data,wordSecCounts):
    listOfNgrams = []
    trigramCounts = {}
    bigramCounts = {}
    c=0
    for k in wordSecCounts:
        for i in range(k-1):
            if(i<k-2):
                listOfNgrams.append((data[c+i],data[c+i+1],data[c+i+2]))
                if (data[c+i],data[c+i+1],data[c+i+2]) in trigramCounts:
                    trigramCounts[(data[c+i],data[c+i+1],data[c+i+2])] += 1
                else:
                    trigramCounts[(data[c+i],data[c+i+1],data[c+i+2])] = 1 
            listOfNgrams.append((data[c+i], data[c+i+1]))
            if (data[c+i], data[c+i+1]) in bigramCounts:
                bigramCounts[(data[c+i], data[c+i+1])] += 1
            else:
                bigramCounts[(data[c+i], data[c+i+1])] = 1
        c=c+k
    return listOfNgrams,trigramCounts,bigramCounts

def sen_pharse(grammar_np,sent_tokens,top):
    chunk_parser=nltk.RegexpParser(grammar_np)
    chunk_parser=chunk_parser.parse(sent_tokens)
    
    for i in chunk_parser:
        text=' '.join(str(i).split(')'))
        text=''.join(text.splitlines())
        text = re.sub("[/]" +cap,"",text)
        text1=re.sub("[(]" + cap ,"",text)
        if(text[1:]!=text1) and len(text1.split())>1:
            s=re.sub(' +', ' ', text1)
            s=s.strip()
            
            if not top:
                #print(top,s)
                top.append(s)   
            else:    
                for i in top:
                    if i in s and i!=s:
                        top.remove(i)
                        top.append(s) 
                if(any(s in sub for sub in top)==False):
                    top.append(s)
    return top

def g_rule(sent):
    grammar_np={r"""NP:{<DT|PP>?<JJ>*<NN>+}
                      {<NNP>+}
                    PP:{<NP><IN|TO><NP>}
                       {<IN|TO><NP>}
                       {<NP><NP>}""",
                r"""NP:{<NN><NNS>}
                      {<NN>+}
                      {<NNS>+}
                      {<NNP>+}
                   PP:{<NP><IN|TO><NP>}
                      {<NP><NP>}
                      """,
                r"""VP:{<MD>|<VBZ>|<VBD>|<VBP>}
                       {<RB>*}
                       {<VB>+|<VBN>+|<VBG>+}
                    PP:{<VP><VP>+}"""}
    top=[]
    result=[]
    for se in range(len(sent)):
        sent_tokens= nltk.pos_tag(re.split("\s", sent[se]))
        for g in grammar_np:
            top=sen_pharse(g,sent_tokens,top)
        top=[i for n, i in enumerate(top) if i not in top[:n]] 
        result+=top
        top=[]   
    #print(len(set(result)),result)
    return result 
      
placeholder = st.empty()
text_input = placeholder.text_area("Type in some text you want to analyze", height=300)

sample_text = st.selectbox(
    "Or pick some sample texts", [f"sample {i+1}" for i in range(len(texts))]
)
sample_id = int(sample_text.split(" ")[-1])
text_input = placeholder.text_area(
    "Type in some text you want to analyze", value=texts[sample_id - 1], height=300
)
But=st.button("compute")
sen,word,wordSecCounts=readdata(text_input)
# print(type(sen[0]))
# for i in range(len(sen)):
#     print(sen[i]+"-"+str(wordSecCounts[i]))
listOfNgrams,trigramCounts,bigramCounts= createNgram(word,wordSecCounts)
l=nltk.pos_tag(word)
c=0
pos=[]
for wc in wordSecCounts:
    for i in range((2*wc)-3):
        pos.append(nltk.pos_tag(listOfNgrams[c+i]))
    c=c+wc 
l=[' '.join(i) for i in listOfNgrams ]    
#print(l)
result1=g_rule(sen)
result2=g_rule(l)
result=result1+result2
result=[i for n, i in enumerate(result) if i not in result[:n]] 
#print(len(result),result)

top_n = st.sidebar.slider("Select number of Phrases to extract", 5, 100, 30, 1)

params = {
    "docs": text_input,
    "top_n": top_n,
}
if But:
    if result != []:
        st.info("top "+str(top_n)+" Phrases")
        keywords = pd.DataFrame(result[:top_n], columns=["Phrase"])
        keywords.index = keywords.index + 1
        st.table(keywords)
