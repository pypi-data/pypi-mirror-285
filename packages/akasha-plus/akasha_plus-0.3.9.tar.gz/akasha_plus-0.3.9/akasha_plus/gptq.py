from transformers import AutoTokenizer, AutoModelForCausalLM
from auto_gptq import BaseQuantizeConfig, AutoGPTQForCausalLM
from typing import List
import os

VALID_BITS = [2, 3, 4, 8]
DEFAULT_EXAMPLES = ["auto-gptq is an easy-to-use model quantization library with user-friendly apis, based on GPTQ algorithm."]

def quantize(model_name_or_path:str="facebook/opt-125m", 
             bits:int=4, damp_percent:float=0.01, group_size:int=128,
             examples:List[str] = None,
             saved_dir:str=None):
    if not examples:
        examples = DEFAULT_EXAMPLES
    if bits not in VALID_BITS:
        raise ValueError(f"Please provide a valid quantization bits, valid choices are: {VALID_BITS}")
    # Quantize config
    quantize_config = BaseQuantizeConfig(
        bits=bits,
        group_size=group_size,
        damp_percent=damp_percent,
        desc_act=False,
    )
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoGPTQForCausalLM.from_pretrained(model_name_or_path, quantize_config)

    # Quantize model by GPTQ
    quantize_examples = [tokenizer(ex) for ex in examples]
    model.quantize(
        quantize_examples,
        batch_size=1,
        use_triton=True,
    )

    # Save model and tokenizer
    if saved_dir is None:
        saved_dir = model_name_or_path + '_quantized'
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)
    model.save_quantized(saved_dir, use_safetensors=True)
    tokenizer.save_pretrained(saved_dir)