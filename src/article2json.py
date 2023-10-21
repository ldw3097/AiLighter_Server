import json
from kiwipiepy import Kiwi
import sys
import os

def get_src(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file, strict=False)
    
        src_list = list()
        num_of_arts = len(data["documents"])
        kiwi = Kiwi(num_workers=12)
        # create src_list
        for i in range(num_of_arts):
            article = data["documents"][i]["text"]
            
            for sentence in article:
                if len(sentence) == 0:
                    del article[article.index(sentence)]

            # analyze morphs via Kiwi tokenizer
            # article = 한 기사의 text
            output_docs = list()
            for j in range(0, len(article)):
                
                
                for idx in range(len(article[j])):
                    
                    output_doc = list()
                    tokenize_list = kiwi.tokenize(article[j][idx]["sentence"])[:-1]
                    for z in range(len(tokenize_list)):
                        token = tokenize_list[z].form + '/' + tokenize_list[z].tag
                        output_doc.append(token)
                    output_docs.append(output_doc)
            src_list.append(output_docs)

        with open('src.json', 'w', encoding='utf-8') as file:
            json.dump(src_list, file, ensure_ascii=False)

        return src_list





        
    
def get_extra_indices(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file, strict=False)
        num_of_arts = len(data["documents"])

        extra_indices_set = list()
        for i in range(num_of_arts):
            extractive = data["documents"][i]["extractive"]
            extra_indices_set.append(extractive)
        
        print(extra_indices_set)
        print("extraction completed")

        return extra_indices_set
    
def get_tgt(file_path, src_list: list, extra_indices_set: list):
    # print('source:', src_list)
    # print(type(src_list))
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file, strict=False)
    
        num_of_arts = len(data["documents"])
        # create tgt_list
        tgt_list = list()
        for i in range(num_of_arts):
            article = data["documents"][i]["text"]
            # add extractive's morphs
            empty_list = list()
            #print('article:', src_list[i])
            for idx in extra_indices_set[0]:
                
                empty_list.append(src_list[i][idx])
                #print('target list: ', empty_list)
            tgt_list.append(empty_list)
            # update extra_indices_set
            del extra_indices_set[0]

            if len(extra_indices_set) == 0:
                break
        print("tgt completed")

        return tgt_list

def make_json(file_path, src_list, tgt_list, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file, strict=False)
        num_of_arts = len(data["documents"])

        list_dic = list()
        for i in range(num_of_arts):
            mydict = {}
            mydict['src'] = src_list[i]
            mydict['tgt'] = tgt_list[i]
            list_dic.append(mydict)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(list_dic, f, ensure_ascii=False)

def json_loader(file_name):
    # 인풋 파일
    input_path = f'../raw_data/{file_name}'
    # 아웃풋 파일
    output_path = f"../pos_data/{file_name}"
    print("opening file:", input_path)
    src_txt = get_src(input_path)
    extra_indices_set = get_extra_indices(input_path)
    tgt_txt = get_tgt(input_path, src_txt, extra_indices_set)
    make_json(input_path, src_txt, tgt_txt, output_path)


def main():
    if(len(sys.argv) <2 ):
        file_names = os.listdir("../raw_data")
        file_names = [file for file in file_names if file.endswith("json")]
        for file_name in file_names:
            json_loader(file_name)
    else:
        json_loader(sys.argv[1])
    print("All completed")
    

if __name__ == '__main__':
    main()