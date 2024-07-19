
import os
from openai import OpenAI
from anthropic import Anthropic
from models.load_model import load_model
from agent import DialSim
from agent import Agent
from agent import load_data

# load data
script_name = "friends"
data, oracle_tkg, oracle_fan = load_data(script_name)

# load LLM for agent
#model_name = "gemma-2b-it"
#model_name = "google/gemma-2b-it"
model_name = "GPT-3.5"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# load_model 다른 허깅페이스 모델과 호환되도록 수정 e.g., codellama2
model, tokenizer, config = load_model(model_name, "4bit")

# custom agent는 일단(오늘내일까지)은 보류
# create agent

agent = Agent(
    history_type="session-entire",
    ret_method="bm25",
    num_ret_history=20,
    model_name=model_name, 
    model=model,
    tokenizer=tokenizer,
    config=config,
    client=client,
    openai_client=client
)
"""
from models.api_based_inference import gpt35_inference
import pandas as pd
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from utils.utils import get_embedding, search_history, open_file, name_change
class CustomAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def save_history(self, generator_instance) -> tuple:
        #return super().save_history(history, date, cur_conv_num, un, post_utterances)
        un = generator_instance["un"]
        post_utterances = generator_instance["post_utterances"]
        prev_cnt = min(un, 3)
        prev_utts = post_utterances[un-prev_cnt : un]
        history = '\n'.join(prev_utts)
        generator_instance["history"] = history
        openie_prompt = open_file('./prompt/openie_utt_prompt.txt').replace('<<<PREV_UTTS>>>', generator_instance["history"]).replace('<<<LAST_UTT>>>', generator_instance["utter_post_sh"])
        cur_triples = gpt35_inference(openie_prompt, self.openai_client).replace(";","")
        processed_history = f'[Date: {generator_instance["date"]}, Session #{generator_instance["cur_conv_num"]}, History #{generator_instance["history_num"]+1}]\n{cur_triples}'
        generator_instance["history"] = processed_history
        
        self.data_dict['history'].append(processed_history)
        self.is_data_dict_history_updated = True
        if self.ret_method == 'openai-emb':
            embedding_vec = get_embedding(processed_history, client=self.client, model="text-embedding-3-small")
            self.data_dict['ada_embedding'].append(embedding_vec)
            self.is_data_dict_embedding_updated = True
            data_df = pd.DataFrame(self.data_dict)
            return data_df
        elif self.ret_method == 'bm25':
            tokenized_docs = [word_tokenize(doc.lower()) for doc in self.data_dict['history']]
            bm25 = BM25Okapi(tokenized_docs)
            return bm25
        elif self.ret_method == 'no_ret':
            token_len = self.llama_tokenizer(processed_history, return_tensors="pt", truncation=True).input_ids.shape[1]
            self.data_dict['ada_embedding'].append(token_len)
            self.is_data_dict_embedding_updated = True
            return None
        elif self.ret_method == "oracle":
            return None
        else:
            raise ValueError("Incorrect `ret_method`.")

custom_agent = CustomAgent(
    history_type="openie",
    ret_method="openai-emb",
    num_ret_history=20,
    model_name=model_name, 
    model=model,
    tokenizer=tokenizer,
    config=config,
    client=client,
    openai_client=client,
    adjust_num_ret_history_=False
)
"""
"""
class CustomSimulator(DialSim):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def process_walk(self):
        un = self.generator_instance["un"]
        post_utterances = self.generator_instance["post_utterances"]
        prev_cnt = min(un, 3)
        prev_utts = post_utterances[un-prev_cnt : un]
        history_before = '\n'.join(prev_utts)
        history = name_change(self.script_name, history_before, self.name_shuffle)
        self.generator_instance["history"] = history
        return self.generator_instance
    
"""
#create simulator
# simulator에 Ross

simulator = DialSim(
    sleep_time=5,
    data=data,
    oracle_tkg=oracle_tkg,
    oracle_fan=oracle_fan,
    script_name=script_name,
    agent=agent,
    name_shuffle="original",
    tkg_ratio=0.7,
    debug=True,
    debug_n_episodes=2,
    fast_eval=False
)
"""
custom_simulator = CustomSimulator(
    sleep_time=5,
    data=data,
    oracle_tkg=oracle_tkg,
    oracle_fan=oracle_fan,
    script_name=script_name,
    agent=custom_agent,
    name_shuffle="original",
    tkg_ratio=0.7,
    debug=True,
    debug_n_episodes=2,
    fast_eval=True
)
"""
# run simulation
simulator.simulate()
#custom_simulator.simulate()
# get log
log_info = simulator.log_results()
#log_info = custom_simulator.log_results()
# save log. Default path is "./results/log.json"
simulator.save_log(log_info)
#custom_simulator.save_log(log_info)
# save 도중에 timeout 됐을 때만 popping하도록 수정


"""
1. 기존 디버깅 check
2. save 도중 timeout 수정 check
3. agent_name DialSim으로 옮기기 check
4. load_model 호환성 check
"""