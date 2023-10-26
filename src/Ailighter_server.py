from fastapi import FastAPI
from pydantic import BaseModel
import logging
import easydict
import torch
from pytorch_pretrained_bert import BertConfig
from models import data_loader
from models.model_builder import Summarizer
from prepro.data_builder import format_to_dict
from others.logging import logger
from others.logging import logger
from models.trainer import build_trainer
import logging

# 로깅을 위한 부분
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Debug_logger")

# bertsum을 위한 파라미터 지정
args = easydict.EasyDict(
    {
        "encoder": "classifier",
        "mode": "summary",
        "bert_data_path": "../bert_data/korean",
        "model_path": "../models/bert_classifier",
        "bert_model": "../../001_bert_morp_pytorch",  # etri로부터 받은 언어모델
        "result_path": "../results/korean",
        "temp_dir": ".",
        "bert_config_path": "../../001_bert_morp_pytorch/bert_config.json",
        "batch_size": 1000,
        "use_interval": True,
        "hidden_size": 128,
        "ff_size": 512,
        "heads": 4,
        "inter_layers": 2,
        "rnn_size": 512,
        "param_init": 0,
        "param_init_glorot": True,
        "dropout": 0.1,
        "optim": "adam",
        "lr": 2e-3,
        "report_every": 1,
        "save_checkpoint_steps": 5,
        "block_trigram": True,
        "recall_eval": False,
        "accum_count": 1,
        "world_size": 1,
        "visible_gpus": "-1",
        "gpu_ranks": "0",
        "log_file": "../logs/bert_classifier",
        "test_from": "../models/bert_classifier/model_step_40000.pt",  # 사용할 fine-tuning된 모델 지정
    }
)


def summary(args, b_list, device_id, pt, step):
    model_flags = [
        "hidden_size",
        "ff_size",
        "heads",
        "inter_layers",
        "encoder",
        "ff_actv",
        "use_interval",
        "rnn_size",
    ]
    device = "cpu" if args.visible_gpus == "-1" else "cuda"
    if pt != "":
        test_from = pt
    else:
        test_from = args.test_from
    logger.info("Loading checkpoint from %s" % test_from)
    checkpoint = torch.load(test_from, map_location=lambda storage, loc: storage)
    opt = vars(checkpoint["opt"])
    for k in opt.keys():
        if k in model_flags:
            setattr(args, k, opt[k])
    print(args)

    config = BertConfig.from_json_file(args.bert_config_path)
    model = Summarizer(args, device, load_pretrained_bert=False, bert_config=config)
    model.load_cp(checkpoint)
    model.eval()

    test_iter = data_loader.Dataloader(
        args,
        _lazy_dataset_loader(b_list),
        args.batch_size,
        device,
        shuffle=False,
        is_test=True,
    )
    trainer = build_trainer(args, device_id, model, None)
    result = trainer.summary(test_iter, step)
    return result


def _lazy_dataset_loader(pt_file):
    dataset = pt_file
    yield dataset


app = FastAPI()

logging.basicConfig(level=logging.INFO)


class Item(BaseModel):
    data: dict


@app.get("/")
def read_root():
    return {"Hello": "World"}


import json
from kiwipiepy import Kiwi

kiwi = Kiwi(num_workers=6)


@app.post("/")
def highlight(input_list: Item):
    crawled = input_list.data.get("content")
    logger.info(crawled)
    # crawled = json.load(contents)["content"]
    postagged = []
    tokenize_list = list(kiwi.tokenize(crawled))
    for sen in tokenize_list:
        sen_pos = []
        for char in sen:
            token = char.form + "/" + char.tag
            sen_pos.append(token)
        postagged.append(sen_pos)
    news = format_to_dict(postagged, crawled)
    summary_result = summary(args, news, 0, "", None)[0]

    logger.info(summary_result)
    new_list = summary_result.split("<q>")

    return {"content": new_list}
