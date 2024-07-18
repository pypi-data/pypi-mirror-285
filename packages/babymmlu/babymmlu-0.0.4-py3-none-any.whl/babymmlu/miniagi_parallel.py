import datasets
import numpy as np
import torch
from torch.nn import CrossEntropyLoss

def eval_parallel(model, tokenizer, dataset=None, q_batch_size=10):
    if dataset is None:
        dataset = load_dataset('ai-forever/baby_mmlu')
    elif isinstance(dataset, str):
        dataset = load_dataset(dataset) 
    
    result = calculate_parallel(model, tokenizer, dataset, q_batch_size)
    return calc_metric(result, 'crossentropy_per_char_answer'),  \
           calc_metric(result, 'crossentropy_per_token_answer'), \
           calc_metric(result, 'crossentropy_total_answer')


# Функция возвращает result - список словарей, где каждый словарь соответствует одному вопросу с ответом
# Здесь q_batch_size - кол-во вопросов, обрабатываемых за один батч
def calculate_parallel(model, tokenizer, dataset, q_batch_size):
 
    # Кол-во батчей
    batch_count = (len(dataset) + q_batch_size - 1)  // q_batch_size

    res = []
    for batch_num in range(batch_count):
        dataset_batch = dataset.select(range(batch_num*q_batch_size, min((batch_num+1)*q_batch_size, len(dataset))))
       
        crossentropy_per_char, crossentropy_per_token, crossentropy_total = get_crossentropy(model, tokenizer, dataset_batch)

        assert len(crossentropy_per_char) == len(crossentropy_per_token) ==  len(crossentropy_total)
    
        for i in range(len(crossentropy_per_char)):
            d = dataset_batch[i]
            
            cur_crossentropy_per_char = crossentropy_per_char[i]
            cur_crossentropy_per_token = crossentropy_per_token[i]
            cur_crossentropy_total = crossentropy_total[i]

            assert  len(d['choices']) == len(cur_crossentropy_per_char) == len(cur_crossentropy_per_token) == len(cur_crossentropy_total)
            
            processed = {
                'question': d['question'],
                'choices':d['choices'],
                'answer_text':d['choices'][d['answer']],
                'answer': d['answer'],
                
                'crossentropy_per_char_answer' : int(np.argmin(cur_crossentropy_per_char)),
                'crossentropy_per_char_answer_text' : d['choices'][int(np.argmin(cur_crossentropy_per_char))],

                'crossentropy_per_token_answer' : int(np.argmin(cur_crossentropy_per_token)),
                'crossentropy_per_token_answer_text' : d['choices'][int(np.argmin(cur_crossentropy_per_token))],
   
                'crossentropy_total_answer' : int(np.argmin(cur_crossentropy_total)),
                'crossentropy_total_answer_text' : d['choices'][int(np.argmin(cur_crossentropy_total))]
            }        
            res.append(processed)    
        
    return res

def load_dataset(dataset_path, split='test'):
    return datasets.load_dataset(dataset_path, split=split)

def calc_metric(result, metric_key):
    right, err = 0,0
    wrong_answers = []    
    for x in result:
        if x[metric_key] != x['answer']:
            err += 1
            wrong_answers.append(x)
        else:
            right += 1

    metric = 1 - err/len(result)
    return metric
 

# Функция возвращает три списка списков - crossentropy_per_char, crossentropy_per_token и crossentropy_total размерами (len(dataset), len(choices)) каждая
def get_crossentropy(model, tokenizer, dataset):

    qa_separator = ''
    all_questions = []
    all_questions_with_answers = []
    all_questions_with_answers_answer_idx = [] # Индекс вопроса для каждого элемента из all_questions_with_answers
    all_answers_char_lens = [] # Длины ответов в символах
    
    for i, d in enumerate(dataset):
        all_questions.append(d['question'])
        all_questions_with_answers.extend([d['question'] + qa_separator + c for c in d['choices']])
        all_questions_with_answers_answer_idx.extend([i] * len(d['choices']))
        all_answers_char_lens.extend([len(c) for c in d['choices']])

    assert len(all_questions_with_answers) == len(all_questions_with_answers_answer_idx) == len(all_answers_char_lens)

    # Batch tokenization
    all_questions_with_answers_tokens_ids = clear_eos_ensure_bos_batch(tokenizer, tokenizer(all_questions_with_answers).input_ids)

    # Длины вопросов с ответами в токенах
    all_questions_with_answers_tokens_lens = [len(qa) for qa in all_questions_with_answers_tokens_ids]

    # Максимальная длина вопроса и ответа в токенах
    max_questions_with_answers_tokens_lens = max(all_questions_with_answers_tokens_lens)

    # Токен для выравнивания.
    # Значение не влияет на результат и может совпадать с реальными используемыми токенами
    pad_token_id = 0 

    # Устройство
    device = model.device  

    # Тензор вопросов и ответов с заполнением значением pad_token_id нехватающих элементов
    all_questions_with_answers_tensor = torch.tensor([all_questions_with_answers_tokens_ids[i] + [pad_token_id] * (max_questions_with_answers_tokens_lens - all_questions_with_answers_tokens_lens[i]) for i in range(len(all_questions_with_answers_tokens_lens))]).to(device)

    # Длины вопросов в токенах
    all_questions_tokens_lens = [get_question_len(all_questions_with_answers_tensor[[qa_id for qa_id, qa_q_id in enumerate(all_questions_with_answers_answer_idx) if qa_q_id == q_id]]) for q_id in range(len(all_questions))]
       
    # Токен маскирования
    mask_token_id = -100
    
    # Правильные лэйблы с масками
    target_ids = torch.tensor([[mask_token_id] * all_questions_tokens_lens[all_questions_with_answers_answer_idx[i]] + all_questions_with_answers_tokens_ids[i][all_questions_tokens_lens[all_questions_with_answers_answer_idx[i]]:] + [mask_token_id] * (max_questions_with_answers_tokens_lens - all_questions_with_answers_tokens_lens[i]) for i in range(len(all_questions_with_answers_tokens_lens))]).to(device)

    # Маска внимания
    attention_mask = torch.tensor([[1] * all_questions_with_answers_tokens_lens[i] + [0] * (max_questions_with_answers_tokens_lens - all_questions_with_answers_tokens_lens[i]) for i in range(len(all_questions_with_answers_tokens_lens))]).to(device)

    # Длины ответов в токенах
    all_answers_token_lens = [qa_tok_len - all_questions_tokens_lens[all_questions_with_answers_answer_idx[qa_n]] for qa_n, qa_tok_len in enumerate(all_questions_with_answers_tokens_lens)]
 
    # Преобразовываем к тензорам
    all_answers_token_lens = torch.tensor(all_answers_token_lens).to(device)
    all_answers_char_lens =  torch.tensor(all_answers_char_lens).to(device)

    with torch.no_grad():
        outputs = model(input_ids=all_questions_with_answers_tensor, attention_mask=attention_mask)

    shift_logits = outputs.logits[..., :-1, :].contiguous()
    shift_labels = target_ids[..., 1:].contiguous()
    loss_fct = CrossEntropyLoss(reduction='none')

    # Размеры 
    # shift_logits : [len(all_questions_with_answers_tokens_lens), max_questions_with_answers_tokens_lens - 1, embedding_size]
    # shift_labels : [len(all_questions_with_answers_tokens_lens), max_questions_with_answers_tokens_lens - 1]


    # Размеры при расчёте лосса
    # shift_logits : [len(all_questions_with_answers_tokens_lens) * (max_questions_with_answers_tokens_lens - 1), embedding_size]
    # shift_labels : [len(all_questions_with_answers_tokens_lens) * (max_questions_with_answers_tokens_lens - 1)]

    crossentropy_tensor = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1)).view(shift_labels.size())

    # После вызова лосса получаем тензор размера [len(all_questions_with_answers_tokens_lens) * (max_questions_with_answers_tokens_lens - 1)]
    # Ресайзим его к [len(all_questions_with_answers_tokens_lens), (max_questions_with_answers_tokens_lens - 1)]

    # Усредняем neg_log_likelihood построчно. 
    # Внимание: значения в маскированных элементах равно нулю. Тем не менее, эти элементы принимают участие при расчёте среднего.
    crossentropy_total = torch.sum(crossentropy_tensor, axis=-1)

    # Размер neg_log_likelihood : [len(all_questions_with_answers_tokens_lens)]

    # Умножаем на длины ответов в токенах
    #crossentropy_total = neg_log_likelihood * max_questions_with_answers_tokens_lens

    # Делим на длины ответов в символах
    crossentropy_per_char = crossentropy_total / all_answers_char_lens

    # Делим на длины ответов в токенах
    crossentropy_per_token = crossentropy_total / all_answers_token_lens
      
    # Подготавливаем итоговые списки списков
    last_answer_idx = -1
    ret_crossentropy_per_char = []
    ret_crossentropy_per_token = []
    ret_crossentropy_total = []
    for i in range(len(all_questions_with_answers_tokens_lens)):
        cur_answer_idx = all_questions_with_answers_answer_idx[i]
        if last_answer_idx != cur_answer_idx:
            ret_crossentropy_per_char.append([])
            ret_crossentropy_per_token.append([])
            ret_crossentropy_total.append([])
        ret_crossentropy_per_char[-1].append(crossentropy_per_char[i].item())
        ret_crossentropy_per_token[-1].append(crossentropy_per_token[i].item())
        ret_crossentropy_total[-1].append(crossentropy_total[i].item())
        last_answer_idx = cur_answer_idx

    return ret_crossentropy_per_char, ret_crossentropy_per_token, ret_crossentropy_total


def get_question_len(tokens_tensor):
    for i in range(tokens_tensor.shape[-1]):
        different_token_ids_count = len(set(tokens_tensor[:,i].cpu().numpy()))
        if different_token_ids_count > 1:
            return i
    assert False, "Same answers"
       

def clear_eos_ensure_bos_batch(tokenizer, batch):
    return [[tokenizer.bos_token_id] + [t for t in text if t not in [tokenizer.bos_token_id, tokenizer.eos_token_id]] for text in batch]


