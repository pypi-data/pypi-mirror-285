import os
import pickle
from copy import deepcopy
import time
import random
import pandas as pd
from openai import OpenAI
from anthropic import Anthropic
import time
import signal
import warnings
import argparse
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk
import multiprocessing

from logging_results.logging import log_results, log_answers, log_ret_history_question, log_times, log_calibration, log_everything
from post_processing.process_answer import judge_eq, distill_answer, calibrate
from models.api_based_inference import gpt35_inference, gpt4_inference, claude_inference, gemini_inference
from models.open_source_model_inference import open_source_model_inference
from models.load_opensource_model import load_opensource_tokenizer
from models.load_model import load_model
from utils.utils import get_embedding, search_history, open_file, name_change, extract_gt_sessions
warnings.filterwarnings('ignore')
from transformers import AutoTokenizer

#random.seed(42)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="GPT-3.5", help="name of the model. Default: 'GPT-3.5'.")
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction, help="if set, use truncated dataset for debugging.")
    parser.add_argument("--debug_n_episodes", type=int, default=5, help="number of episodes to evalutate on debug mode.")
    parser.add_argument("--quantization", type=str, default="no", help="either to quantize the model or not. Default: False")
    parser.add_argument("--script_name", type=str, default='friends', help="name of the script to evaluate. Should be one of ('friends', 'bigbang', 'theoffice'). Default: 'friends'")
    parser.add_argument("--sleep_time", type=float, default=5, help="time limit in seconds for model response. Default: 5")
    parser.add_argument('--history_type', type=str, default='scene-entire', help="How to store conversation history.")
    parser.add_argument('--num_ret_history', type=int, default=10, help="Number of histories we are going to retrieve. Default: 10.")
    parser.add_argument('--ret_method', type=str, default='openai-emb', help=" Default: openai-emb. Should be one of ('openai-emb', 'bm25', 'no_ret')")
    parser.add_argument('--name_shuffle', type=str, default='original', help=" Default: original. Should be one of ('original', 'shuffle', 'new_name')")
    parser.add_argument('--trial_version', type=int, default=0, help= "version number of the experiment.")
    parser.add_argument('--num_cores', type=int, default=10, help='upper bound of number of cpu cores')
    parser.add_argument('--mode', type=str, default='select', help='question mode.')
    return parser.parse_args()

 
def worker_process(simulator_args):
    #print(f"Process ID: {os.getpid()} on CPU: {os.sched_getaffinity(0)}")
    return simulator(**simulator_args)
def simulator(
        script_name,
        sleep_time=0.000001, 
        hard_ratio=0.7, 
        mode='select', 
        num_ret_history = 5, 
        model_name:str="GPT-3.5", 
        debug:bool=False, 
        debug_n_episodes:int=5,
        quantization:str="no",
        history_type:str="utts",
        ret_method:str='openai-emb',
        name_shuffle:str='original',
        num_cores:int=10,
        trial_version:int=0
        ):
    """
    script_name: script name ('friends', 'bigbang', 'theoffice')
    sleep_time: time for one utterance in the simulator. we do not use this parameter in unlimited simulator. (e.g. 3)
    hard_ratio: the ratio of KG based question among the whole question set (0.0-1.0)
    mode: question type ('select' or 'free text')
    num_ret_history: the number of the retrieved utterances
    ret_method: retrieval method. openai embedding based: 'openai-emb', BM25 based: 'bm25', Naive LLM inference: 'no_ret'.
    """
    #model, tokenizer, config = load_model(model_name, quantization)

    simulator_start_time = time.time()
    if ret_method in ['no_ret', 'oracle']:
        history_type = 'scene-entire'
    
    total_turns = 0
    total_sessions = 0
    total_tokens = 0
    total_speakers = 0

    possible_sessions = 0
    total_ans_q_possible = 0
    total_unans_q_possible = 0
    total_fan_possible = 0
    total_kg_onehop_possible = 0
    total_kg_twohop_possible = 0

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-70B-Instruct", cache_dir='/nfs_data_storage/huggingface', token='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')
    
    ####For hyperparameter 
    if history_type == "utts":
        num_ret_history = 20
    elif history_type == "scene-entire":
        if 'llama' in model_name.lower():
            num_ret_history = 3
            if ret_method == 'bm25':
                num_ret_history = 1
        elif 'tulu' in model_name.lower() or 'gemma' in model_name.lower():
            if ret_method == 'bm25':
                num_ret_history = 2
            else:
                num_ret_history = 5
        else:
            num_ret_history = 10
    elif history_type == "scene-summary":
        if 'llama' in model_name.lower():
            num_ret_history = 8
        else:
            num_ret_history = 15
    elif history_type == "openie":
        num_ret_history = 20

    llama_tokenizer = load_opensource_tokenizer("llama2-7b-chat")

    max_token_len = 0
    if model_name == "GPT-3.5":
        max_token_len = 16000
    elif model_name == "GPT-4":
        max_token_len = 128000
    elif model_name == "claude-3" or model_name == "claude-2.1":
        max_token_len = 200000
    elif model_name == "gemini":
        max_token_len = 32000
    else:
        try:
            pass
            #max_token_len = config.max_position_embeddings
        except:
            max_token_len = 4000
    
    openai_client = OpenAI(api_key="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") # Woosog's API key. Pls change it to your own.
    anthropic_client = None
    if "claude" in model_name: # Woosog's API key. Pls change it to your own.
        anthropic_client = Anthropic(api_key="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")

    with open(f'/nfs_edlab/jhkim/samantha_data_final/{script_name}_samantha_total_fine.pickle', 'rb') as f:
        data = pickle.load(f)
    with open(f'/nfs_edlab/jhkim/samantha_data_final/{script_name}_oracle_hard.pickle', 'rb') as f_h:
        oracle_hard = pickle.load(f_h)
    with open(f'/nfs_edlab/jhkim/samantha_data_final/{script_name}_oracle_easy.pickle', 'rb') as f_e:
        oracle_easy = pickle.load(f_e)
    #with open(f'./data/{script_name}_samantha_total_fine.pickle', 'rb') as f:
    #    data = pickle.load(f)
    if script_name == 'friends':
        chatbot = 'Ross'
    elif script_name == 'bigbang':
        chatbot = 'Sheldon'
    elif script_name == 'theoffice':
        chatbot = 'Michael'
    else:
        assert 0
    
    data_dict = {
        'ada_embedding': [], ### openai-emb -> embedding vector, no_ret -> token length
        'history': []
    }

    episodes = list(data)
    if debug:
        episodes = episodes[:debug_n_episodes]
    before_date = ''
    cur_conv_num = 1

    result_list = []
    result_time_list = []
    ambiguous_idx_list = [] # list of indices of the data (episode, scene, question_prompt) where the model's output is ambiguous. 
    ambiguous_answer_list = [] # list of answers(model output) that are ambiguous.
    ambiguous_gold_answer_list = [] # list of ground truth answers for the ambiguous answers.
    answer_list = [] # list of answers generated by the models. TODO: implement logging answers too.
    gold_answer_list = [] # list of ground truth (gold) answers
    ret_histories_question_answer_list = [] # list of (ret_histories, question)
    save_time_list = [] # list of saving time
    retrieve_search_time_list = [] # list of time spent in `search_history`
    ans_time_list = [] # list of time spent in answering
    calibrated_result_list = [] # list of calibrated answers
    calibrated_distilled_answer_list = [] # list of calibrated distilled answers
    epi_scene_date_to_sessions = {}
    date_to_sessions = {}

    for epi in episodes:
        epi_data = data[epi]
        scene_nums = list(epi_data)
        epi_scene_date_to_sessions[epi] = {}
        
        for sc_num in scene_nums:
            total_sessions += 1
            fan_q_possible = 0
            kg_onehop_possible = 0
            kg_twohop_possible = 0
            ansq_possible = 0
            unansq_possible = 0

            script = epi_data[sc_num]['script']
            date = epi_data[sc_num]['date']
            date_splitted = date.replace(',', '').split()
            cannot_hard = 0
            cannot_easy = 0
            
            epi_scene_date_to_sessions[epi][sc_num] = {date: script}
            try:		
                date_to_sessions[date].append(script)
            except:
                date_to_sessions[date] = [script]

            try:
                question_dict = epi_data[sc_num]['hard_q']
                final_hard_list = []
                hard_list = list(question_dict)
                for hard in hard_list:
                    if len(question_dict[hard]) > 0:
                        final_hard_list.append(hard)
                hard_target_type = random.choice(final_hard_list)

                hard_q_list = question_dict[hard_target_type]
                target_question = random.choice(hard_q_list)
            except:
                cannot_hard=1
                pass

            try:
                question_dict = epi_data[sc_num]['easy_q']
                final_easy_list = []
                easy_list = list(question_dict)
                for easy in easy_list:
                    if len(list(question_dict[easy])) > 0:
                        final_easy_list.append(easy)
                easy_target_type = random.choice(final_easy_list)

                easy_q_list = list(question_dict[easy_target_type])
                easy_q_target_num = random.choice(easy_q_list)
                target_question = question_dict[easy_target_type][easy_q_target_num]
            except:
                cannot_easy = 1
                pass

            current_type = ''
            target1_dates = []
            target2_dates = []
            gt_sessions = ""

            #### Question Selection (Hard or Easy)
            rand_val = random.random()
            if cannot_easy == 1 and cannot_hard == 1:
                target_question = 'cannot ask'
                target_question_2 = 'cannot ask'
            elif (cannot_easy == 1 and cannot_hard == 0) or rand_val < hard_ratio:
                question_dict = epi_data[sc_num]['hard_q']
                final_hard_list = []
                hard_list = list(question_dict)
                for hard in hard_list:
                    if len(question_dict[hard]) > 0:
                        if '_' in hard:
                            kg_twohop_possible += len(question_dict[hard])
                        else:
                            kg_onehop_possible += len(question_dict[hard])
                        if 'fu' in hard:
                            unansq_possible += len(question_dict[hard])
                        else:
                            ansq_possible += len(question_dict[hard])
                        final_hard_list.append(hard)
                        if 'fu' not in hard:
                            final_hard_list.append(hard)
                hard_target_type = random.choice(final_hard_list)

                hard_q_list = question_dict[hard_target_type]
                for _ in range(5):
                    target_question = random.choice(hard_q_list)
                    ran_q = target_question['questions'][list(target_question['questions'])[0]]
                    if 'n '+ date_splitted[2] in ran_q or date_splitted[0] + ' ' + date_splitted[2] in ran_q:
                        continue
                
                for _ in range(5):
                    target_question_2 = random.choice(hard_q_list)
                    ran_q = target_question_2['questions'][list(target_question_2['questions'])[0]]
                    if 'n '+ date_splitted[2] in ran_q or date_splitted[0] + ' ' + date_splitted[2] in ran_q:
                        continue

                current_type = hard_target_type
                try:
                    target1_dates = oracle_hard[epi][sc_num][current_type][hard_q_list.index(target_question)]
                    target2_dates = oracle_hard[epi][sc_num][current_type][hard_q_list.index(target_question_2)]
                except:
                    target1_dates = oracle_hard[epi][sc_num][current_type][target_question['questions'][list(target_question['questions'])[0]]]
                    target2_dates = oracle_hard[epi][sc_num][current_type][target_question_2['questions'][list(target_question_2['questions'])[0]]]

            elif (cannot_easy == 0 and cannot_hard == 1) or rand_val >= hard_ratio:
                question_dict = epi_data[sc_num]['easy_q']
                final_easy_list = []
                easy_list = list(question_dict)
                for easy in easy_list:
                    if len(list(question_dict[easy])) > 0:
                        final_easy_list.append(easy)
                        if 'unans' in hard:
                            unansq_possible += len(question_dict[easy])
                        else:
                            ansq_possible += len(question_dict[easy])
                        fan_q_possible += len(question_dict[easy])
                        if 'unans' not in easy:
                            final_easy_list.append(easy)
                            final_easy_list.append(easy)
                            final_easy_list.append(easy)
                easy_target_type = random.choice(final_easy_list)

                easy_q_list = list(question_dict[easy_target_type])
                easy_q_target_num = random.choice(easy_q_list)
                target_question = question_dict[easy_target_type][easy_q_target_num]
                easy_q_target_num_2 = random.choice(easy_q_list)
                target_question_2 = question_dict[easy_target_type][easy_q_target_num_2]

                current_type = easy_target_type
                if current_type in ['ans_w_time', 'dont_know_unans_time']:
                    target1_dates = oracle_easy[epi][sc_num][current_type][easy_q_target_num]
                    target2_dates = oracle_easy[epi][sc_num][current_type][easy_q_target_num_2]


            if before_date != date:
                cur_conv_num = 1
                before_date = date            
            
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
                if chatbot+':' in utter:
                    chatbot_utters.append(utter)
                if ':' in utter:
                    post_utterances.append(utter.strip())
                    temp_utter = deepcopy(utter.strip())
                else:
                    post_utterances.pop()
                    temp_utter += '\n'+utter.strip()
                    post_utterances.append(temp_utter)
            
            if sc_num != scene_nums[0]:
                print()

            print('###########################################')
            print(f'Date: {date}, Conversation #{cur_conv_num}')
            print('###########################################\n')

            try:
                chatbot_utters = chatbot_utters[1:]
                random_chatbot_utter = random.choice(chatbot_utters)
                indexes = [i for i, s in enumerate(post_utterances) if random_chatbot_utter in s]
                for idx in indexes:
                    range_indexes = [i for i in range(max(0, idx-2), min(len(characters), idx+3))]
                close_chars = []
                for idx in range_indexes:
                    close_chars.append(characters[idx])
                characters = list(set(close_chars))
                close_chars = list(set(close_chars))
                for char_ in close_chars:
                    if chatbot.lower() in char_.lower() or 'all' == char_.lower():
                        try:
                            characters.remove(char_)
                        except:
                            pass
                characters.remove(chatbot)
            except:
                pass
            total_speakers = total_speakers + len(characters) + 1

            if len(characters) > 0:
                char_ask = random.choice(characters)
                if not (target_question == 'cannot ask' and target_question_2 == 'cannot ask'):
                    possible_sessions += 1 
                    total_fan_possible += fan_q_possible
                    total_kg_onehop_possible += kg_onehop_possible
                    total_kg_twohop_possible += kg_twohop_possible
                    total_ans_q_possible += ansq_possible
                    total_unans_q_possible += unansq_possible
                

            history_num = 0
            script_history = ""
            #total_sessions += 1
            for un, utter_post in enumerate(post_utterances):
                total_turns += 1
                total_tokens += len(tokenizer(utter_post).input_ids)
                #print(name_change(script_name, utter_post, name_shuffle))
                history = ""
                if history_type == "utts":
                    history = name_change(script_name, utter_post, name_shuffle)
                elif history_type == "scene-entire":
                    if not utter_post.endswith("\n"):
                        utter_post += "\n"
                    script_history += name_change(script_name, utter_post, name_shuffle)
                    history = script_history
                elif history_type == "scene-summary":
                    if not utter_post.endswith("\n"):
                        utter_post += "\n"
                    script_history += name_change(script_name, utter_post, name_shuffle)
                    history = script_history
                elif history_type == "openie":
                    prev_cnt = min(un, 3)
                    prev_utts = post_utterances[un-prev_cnt : un]
                    history_before = '\n'.join(prev_utts)
                    history = name_change(script_name, history_before, name_shuffle)
                else:
                    return AssertionError("Incorrect `history_type`.")

                embedding_vec = None
                
                save_timeout_flag = False
                search_timeout_flag = False
                ans_timeout_flag = False
                save_start_time = None
                save_end_time = None
                save_time = None
                
                # below are what we are actually going to log
                time_in_saving = None 
                time_in_retrieval_searching = None
                time_in_answering = None
                result_time = None
                ans_time = None
                answer = None
                
                already_pop = False
                    
                save_start_time = time.time()
                
                if history_type == "utts":
                    processed_history = f"[Date: {date}, Session #{cur_conv_num}, Utterance #{history_num+1}] {history}"
                    history_num += 1
                elif history_type == "scene-entire":
                    processed_history = f"[Date: {date}, Session #{cur_conv_num}]\n{history}"
                elif history_type == "scene-summary":
                    if len(post_utterances) % 2 != un % 2:
                        sum_prompt = open_file('./prompt/chatgpt_summarize_prompt.txt').replace('<<<DIALOG>>>', history)
                        history_sum = gpt35_inference(sum_prompt, openai_client)
                        processed_history = f"[Date: {date}, Session #{cur_conv_num}]\n{history_sum}\n"
                    elif un == 0 or un == 1:
                        processed_history = f"[Date: {date}, Session #{cur_conv_num}]\n{post_utterances[0]}\n"
                elif history_type == "openie":
                    openie_prompt = open_file('./prompt/openie_utt_prompt.txt').replace('<<<PREV_UTTS>>>', history).replace('<<<LAST_UTT>>>', utter_post)
                    cur_triples = gpt35_inference(openie_prompt, openai_client).replace(";","")
                    processed_history = f"[Date: {date}, Session #{cur_conv_num}, History #{history_num+1}]\n{cur_triples}"

                # save dialogue real time
                
                """
                If history_type is "scene-entire", we temporally save the history up to the last utterance of the chatbot.
                If the question is not asked at the chatbot's utterance, we remove the history saved upto the utterance.
                This is akin to letting a model to have a memory span of the scene.

                When history_type is "utts", we save each utterance as the history.
                Hence, the difference between "utts" and "scene-entire" is the memory burden.
                In otherwords, "scene-entire" has more burden in remembering context.
                """
            
                #save_to_data_dict_signal_handler = signal_handler
                if history_type == "openie" and (cur_triples.lower() == 'nan' or "i'm sorry" in cur_triples.lower()):
                    pass
                else:
                    data_dict['history'].append(processed_history)
                    if history_type == "openie":
                        history_num += 1

                    if ret_method == 'openai-emb':
                        embedding_vec = get_embedding(processed_history, client=openai_client, model="text-embedding-3-small")
                        data_dict['ada_embedding'].append(embedding_vec)
                        data_df = pd.DataFrame(data_dict)
                        
                    elif ret_method == 'bm25':
                        tokenized_docs = [word_tokenize(doc.lower()) for doc in data_dict['history']]
                        bm25 = BM25Okapi(tokenized_docs)
                    elif ret_method == 'no_ret':
                        token_len = llama_tokenizer(processed_history, return_tensors="pt", truncation=True).input_ids.shape[1]
                        data_dict['ada_embedding'].append(token_len)
                    elif ret_method == 'oracle':
                        pass
                    else:
                        return AssertionError("Incorrect `ret_method`.")

                # We use `data_dict` to temporally store (history, embedding_vec) that will be transformed to pandas dataframe.
                # We temporally store information when a question is not asked at the utterance at the moment.
                # This marginally reduces time complexity when saving histories that are not included in the questions.
                
                save_end_time = time.time()
                save_time = save_end_time - save_start_time  
                
                if save_time >= sleep_time:
                    save_timeout_flag = True
                    print("\nTimeout (saving history)!!!\n")
                    print("Corresponding history couldn't be saved.\n")
                    # remove appeneded `data_dict`
                    if len(data_dict['history']) > 0:
                        data_dict['history'].pop()
                    if ret_method in ["openai-emb", "no_ret"]:
                        if len(data_dict['ada_embedding']) > 0:
                            data_dict['ada_embedding'].pop()
                        if ret_method == "openai-emb":
                            data_df = pd.DataFrame(data_dict)
                    #for bm25, `bm25` should be re-calcuated using the popped `data_dict`
                    if ret_method == "bm25":
                        if len(data_dict['history']) > 0:
                            tokenized_docs = [word_tokenize(doc.lower()) for doc in data_dict['history']]
                            bm25 = BM25Okapi(tokenized_docs)
                    already_pop = True

                #### Question
                if random_chatbot_utter.lower() in utter_post.lower() and len(characters) > 0 and target_question != 'cannot ask':
                    #total_sessions += 1
                    real_question = ''
                    try:
                        real_question = target_question['questions'][char_ask]
                        true_answer = target_question['answer']
                        gt_sessions = extract_gt_sessions(date_to_sessions, epi_scene_date_to_sessions, current_type, target1_dates, epi, sc_num, num_ret_history)
                        print("target dates are ", target1_dates)
                    except:
                        try:
                            real_question = target_question['questions']['default']
                            true_answer = target_question['answer']
                            gt_sessions = extract_gt_sessions(date_to_sessions, epi_scene_date_to_sessions, current_type, target1_dates, epi, sc_num, num_ret_history)
                            print("target dates are ", target1_dates)
                        except:
                            try:
                                real_question = target_question_2['questions'][char_ask]
                                true_answer = target_question_2['answer']
                                gt_sessions = extract_gt_sessions(date_to_sessions, epi_scene_date_to_sessions, current_type, target2_dates, epi, sc_num, num_ret_history)
                                print("target dates are ", target2_dates)
                            except:
                                try:
                                    real_question = target_question_2['questions']['default']
                                    true_answer = target_question_2['answer']
                                    gt_sessions = extract_gt_sessions(date_to_sessions, epi_scene_date_to_sessions, current_type, target2_dates, epi, sc_num, num_ret_history)
                                    print("target dates are ", target2_dates)
                                except:
                                    continue
                    
                    true_answer_op = ''
                    for oi, op in enumerate(['(A)', '(B)', '(C)', '(D)', '(E)']):
                        if true_answer.lower() == target_question['options'][oi].lower():
                            true_answer_op = op
                            break
                    if true_answer_op == '':
                        for oi, op in enumerate(['(A)', '(B)', '(C)', '(D)', '(E)']):
                            if true_answer.lower() == target_question_2['options'][oi].lower():
                                true_answer_op = op
                                break
                    if true_answer_op == '':
                        # handling misaligned data
                        continue
                    
                    question_part_prompt = ''

                    if mode == 'select':
                        question_part_prompt += f'{char_ask}: {real_question}\n'
                        options = target_question['options']
                        question_part_prompt += f'\t(A) {options[0]}\n'
                        question_part_prompt += f'\t(B) {options[1]}\n'
                        question_part_prompt += f'\t(C) {options[2]}\n'
                        question_part_prompt += f'\t(D) {options[3]}\n'
                        question_part_prompt += f'\t(E) {options[4]}'

                    elif mode == 'free text':
                        options = target_question['options']
                        question_part_prompt = f"{char_ask}: {real_question} {options[0]}? {options[1]}? {options[2]}? {options[3]}? Or, you cannot answer?"
                    
                              
                    """Start of Answering. Time measure starts HERE"""
                    # time measure START
                    ans_timeout_flag = False
                    retrieve_save_start_time = None
                    ans_start_time = None
                    ret_histories = ''

                    char_ask_sh = name_change(script_name, char_ask, name_shuffle)
                    real_question_sh = name_change(script_name, real_question, name_shuffle)
                    ret_search_start_time = time.time()
                    if ret_method == 'openai-emb': 
                        res = search_history(data_df, f'{char_ask_sh}: {real_question_sh}', client=openai_client, n=num_ret_history)     
                        for ret_history in list(res['history']):
                            ret_histories = ret_histories + ret_history + '\n'
                    elif ret_method == 'bm25':
                        if len(data_dict['history']) == 0:
                            ret_histories = "No history.\n"
                        else:
                            tokenized_query = word_tokenize(f'{char_ask_sh}: {real_question_sh}'.lower())
                            doc_scores = bm25.get_scores(tokenized_query)
                            top_doc_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:num_ret_history]
                            top_docs = [data_dict['history'][i] for i in top_doc_indices]
                            for ret_history in top_docs:
                                ret_histories = ret_histories + ret_history + '\n'
                    elif ret_method == 'no_ret':
                        total_token_len = 0
                        ret_his_inds = []
                        for h_ind in range(len(data_dict['ada_embedding'])):
                            total_token_len += data_dict['ada_embedding'][-1-h_ind]
                            if total_token_len > max_token_len - 500:
                                break
                            ret_his_inds.append(-1-h_ind)
                            ret_histories =  data_dict['history'][-1-h_ind] + '\n' + ret_histories     
                    elif ret_method == 'oracle':
                        ret_histories = gt_sessions                       
                        
                    retrieve_search_time = (time.time()-ret_search_start_time)

                    # Model inference
                    question_part_prompt_sh = name_change(script_name, question_part_prompt, name_shuffle)
                    chatbot_sh = name_change(script_name, chatbot, name_shuffle)
                    ans_start_time = time.time()
                    if ret_method == 'no_ret':
                        prompt = open_file('./prompt/naive_llm_inference.txt').replace('<<<Date>>>', date).replace('<<<Dialog_History>>>', ret_histories).replace('<<<Question>>>', question_part_prompt_sh).replace('<<<Chatbot>>>', chatbot_sh)
                    else:
                        prompt = open_file('./prompt/RAG_qa_prompt.txt').replace('<<<Date>>>', date).replace('<<<Dialog_History>>>', ret_histories).replace('<<<Question>>>', question_part_prompt_sh).replace('<<<Chatbot>>>', chatbot_sh)
                    
                    # if model_name in ["GPT-3.5", "GPT-4"]:
                    #     if model_name == "GPT-3.5":
                    #         answer = gpt35_inference(prompt, openai_client)
                    #     else:
                    #         answer = gpt4_inference(prompt, openai_client)
                    # elif model_name == "claude-3" or model_name == "claude-2.1":
                    #     answer = claude_inference(prompt, model_name, anthropic_client)
                    # elif model_name == "gemini":
                    #     answer = gemini_inference(prompt, model)
                    # else:
                    #     answer = open_source_model_inference(prompt, model, tokenizer, config)
                    print('prompt is ')
                    print(prompt)
                    answer = "(A)"
                    ans_time = time.time() - ans_start_time
                    time_in_saving = save_time       
                    time_in_retrieval_searching = retrieve_search_time
                    time_in_answering = ans_time
                    result_time = save_time + retrieve_search_time + ans_time
                    """Measuring time for timeout stops HERE"""
                    
                    is_ambiguous = False
                    #if not ans_timeout_flag and not save_timeout_flag and not search_timeout_flag:
                    result, is_ambiguous = judge_eq(true_answer_op, answer)
                    
                    # log results
                    answer_list.append(answer)
                    gold_answer_list.append(true_answer_op)
                    result_list.append(result)
                    result_time_list.append(result_time)
                    save_time_list.append(time_in_saving)
                    retrieve_search_time_list.append(time_in_retrieval_searching)
                    ans_time_list.append(time_in_answering)
                    print(question_part_prompt_sh)
                    print(f'------------------------------- Q&A result -------------------------------')
                    print(f'result: {result}, ambiguous answer: {is_ambiguous}')
                    print(f'true answer: {true_answer_op}\t model answer: {answer}')
                    print(f'time spent in saving: {time_in_saving}')
                    print(f'time spent in searching history: {time_in_retrieval_searching}')
                    print(f'time spent in answering: {time_in_answering}')
                    print(f'time spent overall: {result_time}')
                    print(f'time limit: {sleep_time}')
                    print(f'model name: {model_name}')
                    print(f'--------------------------------------------------------------------------')
                    if is_ambiguous:
                        ambiguous_idx_list.append((epi, sc_num, question_part_prompt))
                        ambiguous_answer_list.append(answer)
                        ambiguous_gold_answer_list.append(true_answer_op)

                    distilled_answer = distill_answer(answer)
                    ret_histories_question_answer_list.append((ret_histories, question_part_prompt, true_answer_op, distilled_answer))
                    calibration = calibrate(true_answer_op, answer, question_part_prompt, distilled_answer, lenient=True) # (result, is_ambiguous, calibrated_distilled_answer)
                    calibrated_result_list.append(calibration[0])
                    calibrated_distilled_answer_list.append(calibration[2])
                    # delete unfinished scene
                    # will save the entire scene at the last utterance of each scene
                    
                else: # when question is not asked
                    # if it is the last utterance and a question wasn't asked, save the entire scene. i.e., don't remove the scene
                    # if it was the last utterance and a question was asked, it is going to be saved.
                    #if history_type == "scene-entire" and un == len(post_utterances) - 1:
                    #    data_df = pd.DataFrame(data_dict)
                    pass
                
                if not already_pop and "scene" in history_type and un < len(post_utterances) - 1:
                    if ret_method == 'openai-emb' or ret_method == 'no_ret':
                        try:
                            data_dict["history"].pop()
                            data_dict["ada_embedding"].pop()
                        except:
                            AssertionError("Unexpected error(probable cause: couldn't save even one embedding using openai-emb in time). Please run the program again.")
                    else:
                        try:
                            data_dict["history"].pop()
                        except:
                            pass
            cur_conv_num += 1
    simulator_running_time = time.time() - simulator_start_time
    log_info = {
        "simulator_running_time" : simulator_running_time,
        "result_list" : result_list,
        "result_time_list" : result_time_list,
        "ambiguous_idx_list" : ambiguous_idx_list,
        "ambiguous_answer_list" : ambiguous_answer_list,
        "ambiguous_gold_answer_list" : ambiguous_gold_answer_list,
        "answer_list" : answer_list,
        "gold_answer_list" : gold_answer_list,
        "ret_histories_question_answer_list" : ret_histories_question_answer_list,
        "save_time_list" : save_time_list,
        "retrieve_search_time_list": retrieve_search_time_list, 
        "ans_time_list" : ans_time_list,
        "calibrated_result_list" : calibrated_result_list,
        "calibrated_distilled_answer_list" : calibrated_distilled_answer_list
    }
        #if debug:
        #    data_df.to_csv(f'output/real-time-debug-{script_name}_embedded_scenes_small.csv', index=False)
    print("here!!!", possible_sessions, total_fan_possible, total_kg_onehop_possible, total_kg_twohop_possible, total_ans_q_possible, total_unans_q_possible)

    return log_info



def worker_process(keyword_arguments):
    #keyword_arguments = dict(keyword_arguments)
    
    
    cpu_count = os.sched_getaffinity(os.getpid())
    # Print the number of CPUs
    print(f"Number of available CPUs: {cpu_count}")
    #print(f"Process ID: {os.getpid()} on CPU: {os.sched_getaffinity(0)}")
    return simulator(**keyword_arguments)

def main(simulator_args):
    """simulator_args = {
        "script_name" : script_name,
        "sleep_time" : sleep_time, 
        "hard_ratio" : hard_ratio, 
        "mode" : mode, 
        "num_ret_history" : num_ret_history, 
        "model_name": model_name, 
        "debug" : debug, 
        "debug_n_episodes" : debug_n_episodes,
        "quantization" : quantization,
        "history_type" : history_type,
        "ret_method" : ret_method,
        "name_shuffle": name_shuffle,
        "num_cores" : num_cores,
        "trial_version" : trial_version
    }
    """
    
    with multiprocessing.Pool(processes=num_cores) as pool:
        #print(f"Process ID: {os.getpid()} on CPU: {os.sched_getaffinity(0)}")
        
        # 각 프로세스가 수행할 worker_process 함수를 4번 실행하도록 지시
        return dict(pool.map(worker_process, [simulator_args.__dict__]))

if __name__ == "__main__":
    num_cores = 10
    # Pool 객체 생성, 프로세스 수는 사용할 코어 수와 동일하게 설정
    def set_affinity():
        os.sched_setaffinity(os.getpid(), {0,1,2,3,4,5,6,7,8,9})
        
    set_affinity()
    cpu_count = os.sched_getaffinity(os.getpid())
    # Print the number of CPUs
    print(f"Number of available CPUs: {cpu_count}")
    args = parse_args()
    print(args)
    
    
    
    result_time_mean = 0
    
    log_info = simulator(script_name=args.script_name, history_type=args.history_type, sleep_time=args.sleep_time, num_ret_history=args.num_ret_history, model_name=args.model_name, \
                        debug=args.debug, debug_n_episodes=args.debug_n_episodes, quantization=args.quantization, ret_method=args.ret_method, name_shuffle=args.name_shuffle)

    if "Correct" in log_info["result_list"]:
        score_total = log_info["result_list"].count('Correct') / len(log_info["result_list"])
    else:
        score_total = 0
    valid_result_time_list = []
    for result_time in log_info["result_time_list"]:
        if isinstance(result_time, float):
            valid_result_time_list.append(result_time)
    if len(valid_result_time_list) == 0:
        result_time_mean = 0
    result_time_mean = sum(valid_result_time_list) / len(valid_result_time_list)
    
    if "Correct" in log_info["calibrated_result_list"]:
        calibrated_score = log_info["calibrated_result_list"].count('Correct') / len(log_info["calibrated_result_list"])
    else:
        calibrated_score = 0

    
    
    print()
    print('SCORE: ', score_total)
    print(f'SCORE(calibrated): {calibrated_score}')
    print('Answer Time Mean: ', result_time_mean)
    
    log_results_path = \
        f"./results/results-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"
    log_answers_path = \
        f"./results/answers-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"
    log_ret_histories_question_path = \
        f"./results/retrieval_results-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"
    log_times_path = \
        f"./results/times-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"
    log_calibration_path = \
        f"./results/calibration_results-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"

    log_total_path = \
        f"./results/entire_log-{args.script_name}-model_{args.model_name}-debug_{args.debug}-quantization_{args.quantization}-time_limit_{args.sleep_time}-history_type_{args.history_type}-{args.ret_method}_{args.name_shuffle}-version_{args.trial_version}.json"
    
    
    log_results(score_total, calibrated_score, result_time_mean, log_info["result_list"], log_info["result_time_list"], 
                log_info["ambiguous_idx_list"], log_info["ambiguous_answer_list"], log_info["ambiguous_gold_answer_list"], 
                log_file_path=log_results_path)
    
    log_answers(log_info["answer_list"], log_info["gold_answer_list"], log_file_path=log_answers_path)
    
    log_ret_history_question(log_info["ret_histories_question_answer_list"], log_file_path=log_ret_histories_question_path)
    
    log_times(log_info["save_time_list"], log_info["retrieve_search_time_list"], log_info["ans_time_list"], log_file_path=log_times_path)

    log_calibration(log_info, log_file_path=log_calibration_path)
    log_everything(log_info, log_file_path=log_total_path)