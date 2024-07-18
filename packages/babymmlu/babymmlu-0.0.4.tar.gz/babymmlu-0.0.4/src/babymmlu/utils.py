from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_model_and_tokenizer(path, use_cuda=None):
    return load_model(path, use_cuda), load_tokenizer(path)

def load_model(model_path, use_cuda=None):
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
    if use_cuda is None:
        use_cuda = torch.cuda.is_available()
    device = 'cuda' if use_cuda else 'cpu'
    model.to(device)
    model.eval()
    return model

def load_tokenizer(tokenizer_path):
    return AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
