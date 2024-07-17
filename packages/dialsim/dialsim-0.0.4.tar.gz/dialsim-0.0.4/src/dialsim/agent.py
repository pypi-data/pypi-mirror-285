import os, json
import pickle
from copy import deepcopy
import time
import random
import pandas as pd
import time
import warnings
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

from .logging_results.logging import log_results, log_everything
from .post_processing.process_answer import judge_eq, distill_answer, calibrate
from .models.api_based_inference import gpt35_inference, gpt4_inference, claude_inference, gemini_inference
from .models.open_source_model_inference import open_source_model_inference
from .models.load_opensource_model import load_opensource_tokenizer
from .models.load_model import load_model
from .utils.utils import get_embedding, search_history, open_file, name_change, extract_gt_sessions_bm25_date
warnings.filterwarnings('ignore')
from func_timeout import func_set_timeout, FunctionTimedOut, func_timeout

class BaseAgent:
    """Base class for the agents in DialSim.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_max_token_len(model_name:str, config:object=None)->int:
        """Get the context length of the model.
        It supports OpenAI models, Antrhopic models, and huggingface models.

        Args:
            model_name (str) : The name of the model. e.g., "GPT-3.5", "tulu2-7b-dpo"
            config (object) : The config.json file of the huggingface model. Optional if the model is API-based. Default: None
        Returns:
            The context length of the model.

        """
        if model_name == "GPT-3.5":
            max_token_len = 16000
        elif model_name == "GPT-4":
            max_token_len = 128000
        elif model_name == "claude-3" or model_name == "claude-2.1":
            max_token_len = 200000
        elif model_name == "gemini":
            max_token_len = 32000
        elif 'tulu' in model_name:
            max_token_len = 6000
        else:
            try:
                max_token_len = config.max_position_embeddings
            except:
                max_token_len = 4000
        return max_token_len

class Agent(BaseAgent):
    """This is an agent class for the baselines of DialSim.

    Attributes:
        history_type (str): The type of history to be saved. It can be one of "utts", "session-entire", "session-summary"
        ret_method (str): The method of retrieving history. It can be one of "openai-emb", "bm25", "no_ret", "oracle"
        num_ret_history (int): The number of retrieved history to be used in the conversation.
        model_name (str): The name of the LLM to be used for the agent.
        model (object, optional): The LLM model object. Optional if the model is API-based.
        tokenizer (object, optional): The tokenizer object of the LLM model. Optional if the model is API-based. Default: None
        config (object, optional): The configuration object of the LLM model. Optional if the model is API-based. Default: None
        client (object, optional): The client object. Optional if you are not using APIs such as OpenAI or Anthropic. Default: None
        adjust_num_ret_history_ (bool): Whether to adjust the number of retrieved history based on the model name. Default: True
    
    """
    def __init__(
            self, 
            history_type:str, 
            ret_method:str, 
            num_ret_history:int, 
            model_name:str, 
            model:object=None, 
            tokenizer:object=None, 
            config:object=None, 
            client:object=None,
            openai_client:object=None,
            adjust_num_ret_history_:bool=True
    )->None:
        super().__init__()
        
        #if history_type not in ["utts", "session-entire", "session-summary"]:
        #    raise ValueError("`history_type` must be one of 'utts', 'session-entire', 'session-summary'")
        #if ret_method not in ["openai-emb", "bm25", "no_ret", "oracle"]:
        #    raise ValueError("`ret_method` must be one of 'openai-emb', 'bm25', 'no_ret', 'oracle'")
        #if model_name not in ["GPT-3.5", "GPT-4", "GPT-4o", "claude-3", "claude-2.1", "gemini-pro", "gemini-1.5-pro", "llama2-7b-chat", "llama2-70b-chat", "mixtral-it", "mistral-7b-it", "tulu2-7b-dpo", "tulu2-70b-dpo", "gemma-2b-it", "gemma-7b-it"]:
        #    raise ValueError("`model_name` must be one of 'GPT-3.5', 'GPT-4', 'GPT-4o', 'claude-3', 'claude-2.1', 'gemini-pro', 'gemini-1.5-pro', 'llama2-7b-chat', 'llama2-70b-chat', 'mixtral-it', 'mistral-7b-it', 'tulu2-7b-dpo', 'tulu2-70b-dpo', 'gemma-2b-it', 'gemma-7b-it'")

        if ret_method == 'openai-emb':
            if client is None:
                raise ValueError("Client object is required for `openai-emb` retrieval method.")
            if openai_client is None:
                self.openai_client = client
        
        self.openai_client = openai_client

        self.data_dict = {
        'ada_embedding': [], ### openai-emb -> embedding vector, no_ret -> token length
        'history': []
        }
        self.history_type = history_type
        self.ret_method = ret_method
        self.num_ret_history = num_ret_history
        self.max_token_len = self.get_max_token_len(model_name, config)
        
        self.model_name = model_name
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.client = client
        self.adjust_num_ret_history_ = adjust_num_ret_history_
        if self.adjust_num_ret_history_:
            self.adjust_num_ret_history()
        if ret_method == 'no_ret':
            self.llama_tokenizer = load_opensource_tokenizer("llama2-7b-chat")
        else:
            self.llama_tokenizer = ""
        #self.is_saved = False
        self.is_data_dict_embedding_updated = False
        self.is_data_dict_history_updated = False
        
    def adjust_num_ret_history(self)->None:
        """Adjusts `num_ret_history` for different `model_name`, `ret_method`, and `history_type`.
        The adjustments are based on heuristics.

        Returns:
            None

        """
        if self.history_type == "utts":
            self.num_ret_history = 20
        elif self.history_type == "session-entire":
            if 'llama' in self.model_name.lower():
                self.num_ret_history = 3
                if self.ret_method == 'bm25':
                    self.num_ret_history = 1
            elif 'tulu' in self.model_name.lower() or 'gemma' in self.model_name.lower():
                if self.ret_method == 'bm25':
                    self.num_ret_history = 2
                else:
                    self.num_ret_history = 5
            else:
                self.num_ret_history = 10
        elif self.history_type == "session-summary":
            if 'llama' in self.model_name.lower():
                self.num_ret_history = 8
            else:
                self.num_ret_history = 15

    def save_history(self, generator_instance:dict)->tuple:
        """Saves the history of the conversation.

        Args:
            generator_instance (dict): The generator instance, result of the `walk` method.

        Returns:
            tuple: The vectorized memory(if exists) and the current history number.
        
        Raises:
            ValueError: If the `ret_method` is incorrect.

        """
        self.is_data_dict_embedding_updated = False
        self.is_data_dict_history_updated = False
        

        if self.history_type == "utts":
            processed_history = f'[Date: {generator_instance["date"]}, Session #{generator_instance["cur_conv_num"]}, Utterance #{generator_instance["history_num"]+1}] {generator_instance["history"]}'
        elif self.history_type == "session-entire":
            processed_history = f'[Date: {generator_instance["date"]}, Session #{generator_instance["cur_conv_num"]}]\n{generator_instance["history"]}'
        elif self.history_type == "session-summary":
            history_sum = ""
            if generator_instance["un"] == len(generator_instance["post_utterances"])-1:
                sum_prompt = open_file('./prompt/chatgpt_summarize_prompt.txt').replace('<<<DIALOG>>>', generator_instance["history"])
                try:
                    if self.model_name in ["GPT-3.5", "GPT-4"]:
                        if self.model_name == "GPT-3.5":
                            history_sum = gpt35_inference(sum_prompt, self.client)
                        else:
                            history_sum = gpt4_inference(sum_prompt, self.client)
                    elif self.model_name == "claude-3" or self.model_name == "claude-2.1":
                        history_sum = claude_inference(sum_prompt, self.model_name, self.client)
                    elif self.model_name == "gemini":
                        history_sum = gemini_inference(sum_prompt, self.model)
                    else:
                        history_sum = open_source_model_inference(sum_prompt, self.model_name, self.model, self.tokenizer, self.config)
                except:
                    pass
            else:
                history_sum = generator_instance["history"]
            processed_history = f'[Date: {generator_instance["date"]}, Session #{generator_instance["cur_conv_num"]}]\n{history_sum}\n'

        #save_to_data_dict_signal_handler = signal_handler
        self.data_dict['history'].append(processed_history)
        self.is_data_dict_history_updated = True
        if self.ret_method == 'openai-emb':
            embedding_vec = get_embedding(processed_history, client=self.client, model="text-embedding-3-small")
            self.data_dict['ada_embedding'].append(embedding_vec)
            self.is_data_dict_embedding_updated = True
            data_df = pd.DataFrame(self.data_dict)
            #self.is_saved = True
            return data_df
        elif self.ret_method == 'bm25':
            tokenized_docs = [word_tokenize(doc.lower()) for doc in self.data_dict['history']]
            bm25 = BM25Okapi(tokenized_docs)
            #self.is_saved = True
            return bm25
        elif self.ret_method == 'no_ret':
            token_len = self.llama_tokenizer(processed_history, return_tensors="pt", truncation=True).input_ids.shape[1]
            self.data_dict['ada_embedding'].append(token_len)
            self.is_data_dict_embedding_updated = True
            #self.is_saved = True
            return None
        elif self.ret_method == "oracle":
            #self.is_saved = True
            return None
        else:
            raise ValueError("Incorrect `ret_method`.")
        
    def retrieve_history(
            self,
            save_result, 
            char_ask_sh, 
            real_question_sh, 
            gt_sessions,
            openai_client:object=None,
        ):
        """Retrieves the history from the memory.
        It can use one of the following: OpenAI's text-embedding-3-small, BM25, no retrieval, and Oracle.

        Args:
            openai_client (object, optional): The OpenAI client object. It is required if `ret_method` is "openai-emb". Default: None
        """
        
        ret_histories = ''
        if self.ret_method == 'openai-emb': 
            if len(self.data_dict['history']) == 0:
                ret_histories = "No history.\n"
            else:
                res = search_history(df=save_result, product_description=f'{char_ask_sh}: {real_question_sh}', client=openai_client, n=self.num_ret_history)     
                for ret_history in list(res['history']):
                    ret_histories = ret_histories + ret_history + '\n'
        elif self.ret_method == 'bm25':
            if len(self.data_dict['history']) == 0:
                ret_histories = "No history.\n"
            else:
                tokenized_query = word_tokenize(f'{char_ask_sh}: {real_question_sh}'.lower())
                doc_scores = save_result.get_scores(tokenized_query)
                top_doc_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:self.num_ret_history]
                top_docs = [self.data_dict['history'][i] for i in top_doc_indices]
                for ret_history in top_docs:
                    ret_histories = ret_histories + ret_history + '\n'
        elif self.ret_method == 'no_ret':
            total_token_len = 0
            ret_his_inds = []
            if len(self.data_dict['history']) == 0:
                ret_histories = "No history.\n"
            else:
                for h_ind in range(len(self.data_dict['ada_embedding'])):
                    total_token_len += self.data_dict['ada_embedding'][-1-h_ind]
                    if total_token_len > self.max_token_len - 500:
                        break
                    ret_his_inds.append(-1-h_ind)
                    ret_histories =  self.data_dict['history'][-1-h_ind] + '\n' + ret_histories    
        elif self.ret_method == 'oracle':
            ret_histories = gt_sessions                                    
        return ret_histories
    
    def answer_question(self, answer_prompt):
        answer = ""
        try:
            if self.model_name in ["GPT-3.5", "GPT-4"]:
                if self.model_name == "GPT-3.5":
                    answer = gpt35_inference(answer_prompt, self.client)
                else:
                    answer = gpt4_inference(answer_prompt, self.client)
            elif self.model_name == "claude-3" or self.model_name == "claude-2.1":
                answer = claude_inference(answer_prompt, self.model_name, self.client)
            elif self.model_name == "gemini":
                answer = gemini_inference(answer_prompt, self.model)
            else:
                answer = open_source_model_inference(answer_prompt, self.model_name, self.model, self.tokenizer, self.config)
        except:
            pass
        return answer

class DialSim:
    def __init__(
            self, 
            sleep_time:float, 
            data:pd.DataFrame, 
            oracle_tkg:pd.DataFrame, 
            oracle_fan:pd.DataFrame, 
            script_name:str,
            agent:BaseAgent,
            name_shuffle:str="origianl",
            tkg_ratio:float=0.7, 
            fast_eval:bool=True, 
            debug:bool=False, 
            debug_n_episodes:int=10
    )->None:
        self.sleep_time = sleep_time
        self.data = data # pickle data
        self.oracle_tkg = oracle_tkg
        self.oracle_fan = oracle_fan
        self.script_name = script_name
        self.name_shuffle = name_shuffle
        self.tkg_ratio = tkg_ratio
        self.epi_session_date_to_sessions = {} 
        self.date_to_sessions = {}
        self.target_level_list = []
        self.episodes = list(data)
        self.agent = agent
        self.agent_name = ""
        if self.script_name == "friends":
            self.agent_name = "Ross"
        elif self.script_name == "bigbang":
            self.agent_name = "Sheldon"
        elif self.script_name == "theoffice":
            self.agent_name = "Michael"
        else:
            raise ValueError("Incorrect `script_name`. It should be one of 'friends', 'bigbang', 'theoffice'.")
        if debug:
            self.episodes = self.episodes[:debug_n_episodes]
        self.before_date = ''
        self.cur_conv_num = 1
        self.fast_eval = fast_eval
        self.debug = debug

        self.history_num = 0
        self.generator_instance = None
        # where the results are logged
        self.result_list = []
        self.result_time_list = []
        self.ambiguous_idx_list = [] # list of indices of the data (episode, session, question_prompt) where the model's output is ambiguous. 
        self.ambiguous_answer_list = [] # list of answers(model output) that are ambiguous.
        self.ambiguous_gold_answer_list = [] # list of ground truth answers for the ambiguous answers.
        self.answer_list = [] # list of answers generated by the models. TODO: implement logging answers too.
        self.gold_answer_list = [] # list of ground truth (gold) answers
        self.ret_histories_question_answer_list = [] # list of (ret_histories, question)
        self.save_time_list = [] # list of saving time
        self.retrieve_search_time_list = [] # list of time spent in `search_history`
        self.ans_time_list = [] # list of time spent in answering
        self.calibrated_result_list = [] # list of calibrated answers
        self.calibrated_distilled_answer_list = [] # list of calibrated distilled answers
    def process_walk(self):
        return self.generator_instance
    def walk(self):
        """
        Retrieve a question from DialSim data
        """
        for epi in self.episodes:
            self.epi_session_date_to_sessions[epi] = {}
            self.epi_data = self.data[epi]
            session_nums = list(self.epi_data)
            for sc_num in session_nums:
                self.history_num = 0
                already_asked = 0
                script = self.epi_data[sc_num]['script']
                date = self.epi_data[sc_num]['date']
                date_splitted = date.replace(',', '').split()
                cannot_tkg = 0
                cannot_fan = 0
                temp_script = name_change(self.script_name, script, self.name_shuffle)
                self.epi_session_date_to_sessions[epi][sc_num] = {date: temp_script}
                try:
                    self.date_to_sessions[date].append(temp_script)
                except:
                    self.date_to_sessions[date] = [temp_script]
                ###Whether it is possible to ask tkg-based questions 
                try:
                    question_dict = self.epi_data[sc_num]['hard_q']
                    final_tkg_list = []
                    tkg_list = list(question_dict)
                    for tkg in tkg_list:
                        if len(question_dict[tkg]) > 0:
                            final_tkg_list.append(tkg)
                    tkg_target_type = random.choice(final_tkg_list)

                    tkg_q_list = question_dict[tkg_target_type]
                    target_question = random.choice(tkg_q_list)
                except:
                    cannot_tkg=1
                    pass

                 ###Whether it is possible to ask fan quiz-based questions 
                try:
                    question_dict = self.epi_data[sc_num]['easy_q']
                    final_fan_list = []
                    fan_list = list(question_dict)
                    for fan in fan_list:
                        if len(list(question_dict[fan])) > 0:
                            final_fan_list.append(fan)
                    fan_target_type = random.choice(final_fan_list)

                    fan_q_list = list(question_dict[fan_target_type])
                    fan_q_target_num = random.choice(fan_q_list)
                    target_question = question_dict[fan_target_type][fan_q_target_num]
                except:
                    cannot_fan = 1
                    pass

                target_question_list = []
                self.current_type = ''
                gt_sessions = ""
                target_dates_list = []

                #### Question Selection (tkg or fan)
                rand_val = random.random()
                if cannot_fan == 1 and cannot_tkg == 1:
                    target_question_list = ['cannot ask' for _ in range(20)]
                elif (cannot_fan == 1 and cannot_tkg == 0) or rand_val < self.tkg_ratio:
                    question_dict = self.epi_data[sc_num]['hard_q']
                    final_tkg_list = []
                    fu_num = 0
                    not_fu_list = []
                    tkg_list = list(question_dict)
                    for tkg in tkg_list:
                        if len(question_dict[tkg]) > 0:
                            final_tkg_list.append(tkg)
                            if 'fu' in tkg:
                                fu_num += 1
                            else:
                                not_fu_list.append(tkg)
                    if len(not_fu_list) > 0:
                        random.shuffle(not_fu_list)
                        while True:
                            should_stop = 0
                            for not_fu in not_fu_list:
                                if fu_num/len(final_tkg_list) < 0.215:
                                    should_stop = 1
                                    break
                                final_tkg_list.append(not_fu)
                            if should_stop == 1:
                                break
                    tkg_target_type = random.choice(final_tkg_list)
                    tkg_q_list = question_dict[tkg_target_type]

                    self.current_type = tkg_target_type
                    for _ in range(20):
                        target_question = random.choice(tkg_q_list)
                        ran_q = target_question['questions'][list(target_question['questions'])[0]]
                        if 'n '+ date_splitted[2] in ran_q or date_splitted[0] + ' ' + date_splitted[2] in ran_q:
                            continue
                        final_target_question = deepcopy(target_question)
                        target_question_list.append(final_target_question)
                        
                        try:
                            target_dates_list.append(self.oracle_tkg[epi][sc_num][self.current_type][tkg_q_list.index(target_question)])
                        except:
                            try:
                                target_dates_list.append(self.oracle_tkg[epi][sc_num][self.current_type][target_question['questions'][list(target_question['questions'])[0]]])
                            except:
                                target_dates_list.append([])
                elif (cannot_fan == 0 and cannot_tkg == 1) or rand_val >= self.tkg_ratio:
                    question_dict = self.epi_data[sc_num]['easy_q']
                    final_fan_list = []
                    unans_num = 0
                    ans_list = []
                    fan_list = list(question_dict)
                    for fan in fan_list:
                        if len(list(question_dict[fan])) > 0:
                            final_fan_list.append(fan)
                            if 'unans' in fan:
                                unans_num += 1
                            else:
                                ans_list.append(fan)
                    
                    if len(ans_list) > 0:
                        random.shuffle(ans_list)
                        while True:
                            should_stop = 0
                            for ans_ele in ans_list:
                                if unans_num/len(final_fan_list) < 0.27:
                                    should_stop = 1
                                    break
                                final_fan_list.append(ans_ele)
                            if should_stop == 1:
                                break
                    fan_target_type = random.choice(final_fan_list)
                    fan_q_list = list(question_dict[fan_target_type]) 
                    self.current_type = fan_target_type
                
                    for _ in range(20):
                        fan_q_target_num = random.choice(fan_q_list) 
                        target_question = deepcopy(question_dict[fan_target_type][fan_q_target_num])
                        target_question_list.append(target_question)
                        if self.current_type in ['ans_w_time', 'dont_know_unans_time']:
                            try:
                                target_dates_list.append(self.oracle_fan[epi][sc_num][self.current_type][fan_q_target_num])
                            except:
                                target_dates_list.append([])
                        else:
                            target_dates_list.append([])
                if self.before_date != date:
                    self.cur_conv_num = 1
                    self.before_date = date            
                
                utterances = script.split('\n')
                post_utterances = []
                temp_utter = ''    
                chatbot_utters = []
                characters = []
                for utter in utterances:
                    if len(utter.strip()) == 0:
                        continue
                    if 'Teleplay: ' in utter or 'Story: ' in utter:
                        continue
                    if ':' in utter:
                        characters.append(utter.split(':')[0].strip())
                    if self.agent_name+':' in utter:
                        chatbot_utters.append(utter.strip())
                    if ':' in utter:
                        post_utterances.append(utter.strip())
                        temp_utter = deepcopy(utter.strip())
                    else:
                        post_utterances.pop()
                        temp_utter += '\n'+utter.strip()
                        post_utterances.append(temp_utter)
                
                if sc_num != session_nums[0]:
                    print()
                print('###########################################')
                print(f'Date: {date}, Conversation #{self.cur_conv_num}')
                print('###########################################\n')
                try:
                    if len(chatbot_utters) > 1:
                        chatbot_utters = chatbot_utters[1:]
                    random_chatbot_utter = random.choice(chatbot_utters)
                    bot_indices = [i for i, s in enumerate(post_utterances) if random_chatbot_utter in s]
                    range_indices = [i for i in range(max(0, bot_indices[0]-3), min(len(post_utterances), bot_indices[0]+3))]
                    close_chars = []
                    for idx in range_indices:
                        if ':' in post_utterances[idx]:
                            close_chars.append(post_utterances[idx].split(':')[0])
                    characters = list(set(close_chars))
                    close_chars = list(set(close_chars))
                    
                    for char_ in close_chars:
                        if self.agent_name.lower() in char_.lower() or 'all' == char_.lower():
                            try:
                                characters.remove(char_)
                            except:
                                pass 
                except:
                    pass

                if len(characters) > 0:
                    self.char_ask = random.choice(characters)
                else:
                    self.char_ask = ""

                script_history = ""
                for un, utter_post in enumerate(post_utterances):
                    self.history_num += 1
                    self.char_ask_sh = name_change(self.script_name, self.char_ask, self.name_shuffle)
                    history = ""
                    if self.agent.history_type == "utts":
                        history = name_change(self.script_name, utter_post, self.name_shuffle)
                    elif self.agent.history_type == "session-entire":
                        if not utter_post.endswith("\n"):
                            utter_post += "\n"
                        script_history += name_change(self.script_name, utter_post, self.name_shuffle)
                        history = script_history
                    elif self.agent.history_type == "session-summary":
                        if not utter_post.endswith("\n"):
                            utter_post += "\n"
                        script_history += name_change(self.script_name, utter_post, self.name_shuffle)
                        history = script_history
                    #else:
                    #    raise AssertionError("Incorrect `history_type`.")
                    utter_post_sh = name_change(self.script_name, utter_post, self.name_shuffle)
                    
                    #self.cur_conv_num += 1
                    if random_chatbot_utter.lower() in utter_post.lower() and len(characters) > 0 and target_question_list[0] != 'cannot ask':
                        
                        if already_asked == 1:
                            continue
                        real_question = ''
                        real_tar_id = -1
                        for tar_id in range(len(target_question_list)):
                            if self.char_ask in list(target_question_list[tar_id]['questions']):
                                real_question = target_question_list[tar_id]['questions'][self.char_ask]
                            elif 'default' in list(target_question_list[tar_id]['questions']):
                                real_question = target_question_list[tar_id]['questions']['default']
                            else:
                                continue
                            
                            try:
                                true_answer = target_question_list[tar_id]['answer']
                                real_tar_id = tar_id
                                assert(len(target_dates_list)==len(target_question_list))
                                gt_sessions = extract_gt_sessions_bm25_date(self.date_to_sessions, self.epi_session_date_to_sessions, self.current_type, target_dates_list[tar_id], epi, sc_num, self.agent.num_ret_history, real_question)
                                break
                            except:
                                continue
                        if real_question == '' or real_tar_id == -1 or gt_sessions == "":
                            continue
                        
                        self.true_answer_op = ''

                        for oi, op in enumerate(['(A)', '(B)', '(C)', '(D)', '(E)']):
                            if true_answer.lower() == target_question_list[real_tar_id]['options'][oi].lower():
                                self.true_answer_op = op
                                break

                        if self.true_answer_op == '':
                            continue
                        
                        question_part_prompt = ''
                        
                        question_part_prompt += f'{self.char_ask}: {real_question}\n'
                        options = target_question_list[real_tar_id]['options']
                        question_part_prompt += f'\t(A) {options[0]}\n'
                        question_part_prompt += f'\t(B) {options[1]}\n'
                        question_part_prompt += f'\t(C) {options[2]}\n'
                        question_part_prompt += f'\t(D) {options[3]}\n'
                        question_part_prompt += f'\t(E) {options[4]}'
                        self.question_part_prompt_sh = name_change(self.script_name, question_part_prompt, self.name_shuffle)
                        self.agent_name_sh = name_change(self.script_name, self.agent_name, self.name_shuffle)
                        #self.agent_name = self.agent_name_sh
                        self.real_question_sh = name_change(self.script_name, real_question, self.name_shuffle)
                        self.generator_instance = {
                            "epi" : epi,
                            "sc_num" : sc_num,
                            "date" : date,
                            "cur_conv_num" : self.cur_conv_num,
                            "history" : history,
                            "history_num" : self.history_num,
                            "question" : self.question_part_prompt_sh,
                            "gt_sessions" : gt_sessions,
                            "un" : un,
                            "utter_post_sh" : utter_post_sh,
                            "post_utterances" : post_utterances,
                            "true_answer_op" : self.true_answer_op
                        } 
                        yield self.generator_instance
                    else:
                        self.generator_instance = {
                            "epi" : epi,
                            "sc_num" : sc_num,
                            "date" : date,
                            "cur_conv_num" : self.cur_conv_num,
                            "history" : history,
                            "history_num" : self.history_num,
                            "question" : "",
                            "gt_sessions" : gt_sessions,
                            "un" : un,
                            "utter_post_sh" : utter_post_sh,
                            "post_utterances" : post_utterances,
                            "true_answer_op" : ""
                        } 
                        yield self.generator_instance
                self.cur_conv_num += 1   
    def simulate(self):
        """
        dialsim simulator. Does what the original file does.
        """
        self.simulator_start_time = time.time()
        embedding_vec = None
                
        save_timeout_flag = False
        search_timeout_flag = False
        ans_timeout_flag = False
        save_start_time = None
        save_end_time = None
        save_time = None
        is_ambiguous = False
        ret_histories = ''
        # below are what we are actually going to log
        time_in_saving = None 
        time_in_retrieval_searching = None
        time_in_answering = None
        result_time = None
        ans_time = None
        answer = ""
        already_pop = False
        history_before_save_len = None
        embedding_before_save_len = None
        save_result = None
        for idx, inst in enumerate(self.walk()):
            inst = self.process_walk()
                
            if inst["question"]:
                print(inst["question"])

            save_start_time = time.time()
            save_result = None


            try:
                save_result = func_timeout(self.sleep_time, self.agent.save_history, args=(inst,))
                save_end_time = time.time()
                save_time = save_end_time - save_start_time  
            except FunctionTimedOut:
                save_timeout_flag = True
                print("\nTimeout (saving history)!!!\n")
                print("Corresponding history couldn't be saved.\n")
                if self.agent.ret_method == "openai-emb":

                    if self.agent.is_data_dict_embedding_updated:
                        self.agent.data_dict['ada_embedding'].pop()
                    if self.agent.is_data_dict_history_updated:
                        self.agent.data_dict['history'].pop()
                    save_result = pd.DataFrame(self.agent.data_dict)
                    
                elif self.agent.ret_method == "bm25":
                    if self.agent.is_data_dict_history_updated:
                        self.agent.data_dict['history'].pop()
                        tokenized_docs = [word_tokenize(doc.lower()) for doc in self.data_dict['history']]
                        save_result = BM25Okapi(tokenized_docs)
                elif self.agent.ret_method == "no_ret":
                    if self.agent.is_data_dict_embedding_updated:
                        self.agent.data_dict['ada_embedding'].pop()
                    if self.agent.is_data_dict_history_updated:
                        self.agent.data_dict['history'].pop()
                elif self.agent.ret_method == "oracle":
                    pass
                
                already_pop = True
                result = "Wrong (Timeout in saving history)"
                is_ambiguous = False
                answer = "<<<Timeout in saving history>>>"
                time_in_saving = "<<<Timeout in saving history>>>" 
                time_in_retrieval_searching = "<<<Timeout in saving history>>>"
                time_in_ans = "<<<Timeout in saving history>>>"
                result_time = "<<<Timeout in saving history>>>"

            if inst["question"]:
                if not save_timeout_flag:
                    ret_search_start_time = time.time()
                    try:
                        ret_histories = func_timeout(self.sleep_time, self.agent.retrieve_history, args=(save_result, self.char_ask_sh, self.real_question_sh, inst["gt_sessions"], self.agent.openai_client))
                        retrieve_search_time = time.time()-ret_search_start_time
                    except FunctionTimedOut: # timeout during searching history. Note that saving history was done correctly though.
                        print("\nTimeout (searching history)!!!\n")
                        search_timeout_flag = True
                        result = "Wrong (Timeout in searching history)"
                        is_ambiguous = False
                        answer = "<<<Timeout in searching history>>>"
                        time_in_saving = save_time # record actual time taken in saving
                        time_in_retrieval_searching = "<<<Timeout in searching history>>>"
                        time_in_ans = "<<<Timeout in searching history>>>"
                        result_time = "<<<Timeout in searching history>>>"
                    if not search_timeout_flag:
                        if self.agent.ret_method == 'no_ret':
                            answer_prompt = open_file('./prompt/naive_llm_inference.txt').replace('<<<Date>>>', inst["date"]).replace('<<<Dialog_History>>>', ret_histories).replace('<<<Question>>>', self.question_part_prompt_sh).replace('<<<Chatbot>>>', self.agent_name_sh)
                        else:
                            answer_prompt = open_file('./prompt/RAG_qa_prompt.txt').replace('<<<Date>>>', inst["date"]).replace('<<<Dialog_History>>>', ret_histories).replace('<<<Question>>>', self.question_part_prompt_sh).replace('<<<Chatbot>>>', self.agent_name_sh)
                        ans_start_time = time.time()
                        try:
                            answer = func_timeout(self.sleep_time, self.agent.answer_question, args=(answer_prompt,))
                            ans_time = time.time() - ans_start_time
                            time_in_saving = save_time       
                            time_in_retrieval_searching = retrieve_search_time
                            time_in_answering = ans_time
                            result_time = save_time + retrieve_search_time + ans_time
                            print(f"{self.agent_name_sh}: {answer}")
                        except FunctionTimedOut:
                            print("\nTimeout (answering)!!!\n")
                            ans_timeout_flag = True
                            result = "Wrong (Timeout in answering)"
                            is_ambiguous = False
                            answer = "<<<Timeout in answering>>>"
                            time_in_saving = save_time
                            time_in_retrieval_searching = retrieve_search_time
                            time_in_answering = "<<<Timeout in answering>>>"
                            result_time = "<<<Timeout in answering>>>"

                is_ambiguous = False
                if not ans_timeout_flag and not save_timeout_flag and not search_timeout_flag:
                    result, is_ambiguous = judge_eq(self.true_answer_op, answer)
                    if result_time >= self.sleep_time:
                        result = "Wrong (Timeout)"
                    else:
                        if not self.fast_eval:
                            time.sleep(self.sleep_time-result_time)

                already_asked = 1
                # log results
                self.answer_list.append(answer)
                self.gold_answer_list.append(self.true_answer_op)
                self.result_list.append(result)
                self.result_time_list.append(result_time)
                self.save_time_list.append(time_in_saving)
                self.retrieve_search_time_list.append(time_in_retrieval_searching)
                self.ans_time_list.append(time_in_answering)
                self.target_level_list.append({"self.current_type" : self.current_type})
                print(f'------------------------------- Q&A result -------------------------------')
                print(f'result: {result}, ambiguous answer: {is_ambiguous}')
                print(f'true answer: {self.true_answer_op}\t model answer: {answer}')
                print(f'time spent in saving: {time_in_saving}')
                print(f'time spent in searching history: {time_in_retrieval_searching}')
                print(f'time spent in answering: {time_in_answering}')
                print(f'time spent overall: {result_time}')
                print(f'time limit: {self.sleep_time}')
                print(f'model name: {self.agent.model_name}')
                print(f'--------------------------------------------------------------------------')
            
                if is_ambiguous:
                    self.ambiguous_idx_list.append((inst["epi"], inst["sc_num"], inst["question"]))
                    self.ambiguous_answer_list.append(answer)
                    self.ambiguous_gold_answer_list.append(self.true_answer_op)
                distilled_answer = distill_answer(answer)
                self.ret_histories_question_answer_list.append((ret_histories, inst["question"], self.true_answer_op, distilled_answer))
                calibration = calibrate(self.true_answer_op, answer, inst["question"], distilled_answer, lenient=True) # (result, is_ambiguous, calibrated_distilled_answer)
                if isinstance(result_time, float) and result_time >= self.sleep_time:
                    self.calibrated_result_list.append("Wrong (Timeout)")
                    self.calibrated_distilled_answer_list.append("Wrong (Timeout)")
                else:
                    self.calibrated_result_list.append(calibration[0])
                    self.calibrated_distilled_answer_list.append(calibration[2])
            elif not self.fast_eval:
                if save_time is None:
                    pass
                else:
                    time.sleep(self.sleep_time-save_time)
            if not already_pop and "session" in self.agent.history_type and inst["un"] < len(inst["post_utterances"]) - 1:
                if self.agent.ret_method == 'openai-emb' or self.agent.ret_method == 'no_ret':
                    try:
                        self.agent.data_dict["history"].pop()
                        self.agent.data_dict["ada_embedding"].pop()
                    except:
                        AssertionError("Unexpected error(probable cause: couldn't save even one embedding using openai-emb in time). Please run the program again.")
                else:
                    try:
                        self.agent.data_dict["history"].pop()
                    except:
                        pass

            print(inst["utter_post_sh"].strip())
            #if idx ==200:
            #    break
        self.simulator_end_time = time.time()
    def log_results(self):
        simulator_running_time = self.simulator_end_time - self.simulator_start_time
        if "Correct" in self.result_list:
            score_total = self.result_list.count('Correct') / len(self.result_list)
        else:
            score_total = 0
        
        valid_result_time_list = []
        for result_time in self.result_time_list:
            if isinstance(result_time, float):
                valid_result_time_list.append(result_time)
        
        if len(valid_result_time_list) == 0:
            result_time_mean = 0
        else:
            result_time_mean = sum(valid_result_time_list) / len(valid_result_time_list)
        
        if "Correct" in self.calibrated_result_list:
            calibrated_score = self.calibrated_result_list.count('Correct') / len(self.calibrated_result_list)
        else:
            calibrated_score = 0
        
        log_info = {
            "score" : score_total,
            "calibrated_score" : calibrated_score,
            "result_time_mean" : result_time_mean,
            "simulator_running_time" : simulator_running_time,
            "result_list" : self.result_list,
            "result_time_list" : self.result_time_list,
            "ambiguous_idx_list" : self.ambiguous_idx_list,
            "ambiguous_answer_list" : self.ambiguous_answer_list,
            "ambiguous_gold_answer_list" : self.ambiguous_gold_answer_list,
            "answer_list" : self.answer_list,
            "gold_answer_list" : self.gold_answer_list,
            "ret_histories_question_answer_list" : self.ret_histories_question_answer_list,
            "save_time_list" : self.save_time_list,
            "retrieve_search_time_list": self.retrieve_search_time_list, 
            "ans_time_list" : self.ans_time_list,
            "calibrated_result_list" : self.calibrated_result_list,
            "calibrated_distilled_answer_list" : self.calibrated_distilled_answer_list,
            "target_level_list" : self.target_level_list
        }
            
        return log_info

    def save_log(self, log_info:dict, save_path:str="./results/log.json"):
        if not save_path.endswith(".json"):
            raise ValueError("`save_path` must end with '.json'")
        with open(save_path, 'w') as f:
            json.dump(log_info, f, indent=2)

        
    
        