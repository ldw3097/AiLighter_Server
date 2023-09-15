# KorBertSum 원본 데이터에서 학습까지

이 코드는 기존 Korbertsum 코드에 aihub 자연어 데이터를 POS태깅하는 부분을 추가했습니다. 

참고
Korbertsum : https://velog.io/@raqoon886/KorBertSum-SummaryBot
POS태깅 관련 : https://velog.io/@shoveling42/KorBertSum

## 실행 환경
* Local
* WSL Ubuntu
* CUDA for WSL

* pyrouge
* pytorch_pretrained_bert
* tensorboardX

## 실행 방법

### 1. 데이터 다운받기
aihub 문서요약 텍스트를 다운받습니다.
https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=realm&dataSetSn=97

### 2. 데이터에 POS 태깅을 한다.
학습시킬 json 파일을 raw_data 폴더에 넣고 src 폴더에서 아래 명령어를 실행합니다.

    python article2json.py {파일 이름}

kiwi 형태소 분석이 오래걸릴수 있기 때문에 50개 단위로 테스트할것을 추천합니다.

### 3. POS 태깅된 데이터를 임베딩한다.

    python preprocess.py -mode format_to_bert -raw_path ../pos_data -save_path ../bert_data -vocab_file_path "{etri bert config path}"

etri bert config path 는 vocab.korean_morp.list 파일의 경로입니다.
위 코드를 실행하면 bert_data 폴더 밑에 새로운 .pt파일이 생성됩니다.

### 4. 코드를 학습시킨다.
Newsdata_extractive_summ.ipynb를 실행시키면서 코드를 학습시킵니다.
경로는 본인에 맞게 변경해주셔야 됩니다.
