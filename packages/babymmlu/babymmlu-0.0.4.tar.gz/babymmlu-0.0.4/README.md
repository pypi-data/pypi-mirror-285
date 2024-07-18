# babymmlu

Implementation of utilities to measure babymmlu benchmark (see https://huggingface.co/datasets/ai-forever/baby_mmlu).

## Methods

### eval_parallel

Calculates babymmlu measures.

| Parameter    | Optional | Type                      | Default value        | Description                                 |
|--------------|----------|---------------------------|----------------------|---------------------------------------------|
| model        |    No    | AutoModelForCausalLM      |                      | Model to evaluate.                          |
| tokenizer    |    No    | AutoTokenizer             |                      | Tokenizer used with model.                  |
| dataset      |    Yes   | Dataset (Optional) or str | ai-forever/baby_mmlu | Dataset to evaluate model on.               |
| q_batch_size |    Yes   | int                       | 10                   | Number of questions to process in parallel. |

#### Return value
The function returns a tuple with 3 elements: babymmlu measured be crossentropy-per-char, crossentropy-per-token and crossentropy-total.

### load_model_and_tokenizer

Loads model and tokenizer from the same location.

| Parameter    | Optional | Type  | Description                                 |
|--------------|----------|-------|---------------------------------------------|
| path         |    No    | str   | Path to load model and tokenizer from.      |
| use_cuda     |   Yes    | bool  | Whether to load model to cuda or to cpu.    |


#### Return value
The function returns a tuple with 2 elements: 
* model
* tokenizer


### load_model

Loads model from the specified location.

| Parameter    | Optional | Type  | Description                                 |
|--------------|----------|-------|---------------------------------------------|
| model_path   |    No    | str   | Path to load model from.                    |
| use_cuda     |   Yes    | bool  | Whether to load model to cuda or to cpu.    |

#### Return value
The function returns loaded model.

### load_tokenizer

Loads tokenizer from the specified location.

| Parameter      | Optional | Type  | Description                                 |
|----------------|----------|-------|---------------------------------------------|
| tokenizer_path |    No    | str   | Path to load tokenizer from.                |

#### Return value
The function returns loaded tokenizer.


## Example
```
import babymmlu
model, tokenizer = babymmlu.load_model_and_tokenizer('ai-forever/rugpt3small_based_on_gpt2')
result = babymmlu.eval_parallel(model, tokenizer)
print('babymmlu crossentropy-per-char, crossentropy-per-token and crossentropy-total', result)
```
