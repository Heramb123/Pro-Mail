from styleformer import Styleformer
from textblob import TextBlob
import nltk


nltk.download('punkt')

styleformer_c_t_f = Styleformer(style=0)

def style(msg):
    blob=TextBlob(msg)
    result_list = []


    for sent in blob.sentences:
        temp_result = styleformer_c_t_f.transfer(sent.string)
        result_list.append(temp_result)
  
    result= "  ".join(result_list)
    #print("Respected Sir/Madam,\n\n "+result+"\n\n Thanks & Regards")
    #result_1 = styleformer_c_t_f.transfer(msg)
   
    return result



