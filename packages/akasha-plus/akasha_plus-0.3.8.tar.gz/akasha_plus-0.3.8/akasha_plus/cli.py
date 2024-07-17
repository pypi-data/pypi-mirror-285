import click
import os
import subprocess
import sys
import platform
from pathlib import Path
from .gptq import quantize

VALID_QUANTIZATION_METHODS = ['q2_k', 'q3_k_l', 'q3_k_m', 'q3_k_s', 'q4_0', 'q4_1',
                              'q4_k_m', 'q4_k_s', 'q5_0', 'q5_1', 'q5_k_m', 'q5_k_s', 
                              'q6_k', 'q8_0']
VALID_OUTTYPE = ["f32", "f16"]
def verbose_print(*objects, sep=' ', end='\n', file=None, flush=False, verbose=False):
    if verbose:
        print(*objects, sep=sep, end=end, file=file, flush=flush)
        
def run_command(command:str, capture_output:bool=False) -> subprocess.CompletedProcess: 
    """Execute the command and return the result.

    Parameters
    ----------
    command : str
        The command to be executed.

    Returns
    -------
    subprocess.CompletedProcess
        The object (subprocess.CompletedProcess) after execution.
    """
    result = subprocess.run(command,
                            shell=True,
                            capture_output=capture_output,
                            text=True)
    
    return result

@click.group()
def main():
    """ 
    a python sdk to achieve large language model quatization and deployment
    """
    pass

#%% gguf
@main.command(help='transfer large language model into gguf format.')
@click.option('--model', 'target_model', type=str, required=True, help='target model')
@click.option('--outtype', 'outtype', type=str, required=True, default='f16', help='floating point precision for model weights')
@click.option('--pad-vocab', '-p', 'pad_vocab', is_flag=True, help='add pad tokens when model vocab expects more than tokenizer metadata provides')
@click.option('--verbose', '-v', 'verbose', is_flag=True, help='verbose mode')
def to_gguf(target_model, outtype, pad_vocab, verbose):
    
    if outtype not in VALID_OUTTYPE:
        raise ValueError("Please provide a valid outtype, valid choices are: {VALID_OUTTYPE}")
    model_folder = Path(target_model)
    # check if model_folder is a directory
    if model_folder.is_dir():
        outfile = f'{model_folder}.gguf'
    else:
        outfile = f'{model_folder.stem}.gguf'
    submodule_path = os.path.join(os.path.dirname(__file__), 'gguf-py')
    
    sys.path.append(submodule_path)
    convert_py_path = os.path.join(os.path.dirname(__file__), 'convert.py')
    
    pad_vacab_cmd = ' --pad-vocab' if pad_vocab else ''
    # transfer model to gguf format
    cmd = f'python {convert_py_path} {model_folder} --outfile {outfile} --outtype {outtype}{pad_vacab_cmd}'
    run_command(cmd, capture_output=not verbose)
    
    
@main.command(help='quantize large language model(in gguf type) with different method.')
@click.option('--model', 'target_gguf_model', type=str, required=True, help='target model in gguf type')
@click.option('--method', 'quantization_method', type=str, required=True, default='q4_k_m', help='quantization method')
@click.option('--verbose', '-v', 'verbose', is_flag=True, help='verbose mode')
def quantize_gguf(target_gguf_model, quantization_method, verbose):
    
    # check if gguf_model is .gguf file
    model_path = Path(target_gguf_model)
    if not model_path.suffix == '.gguf':
        raise ValueError("Please provide a valid gguf model file")
    # check if quantization method is valid
    if quantization_method.lower() not in VALID_QUANTIZATION_METHODS:
        raise ValueError("Please provide a valid quantization method, valid choices are: {VALID_QUANTIZATION_METHODS}")
    
    # decide which quantization exectuble to use by checking the operating system
    system_platform = platform.system()
    
    if system_platform == "Linux":
        verbose_print("Running on Linux", verbose=verbose)
        quantize_exec = 'quantize_linux'
    elif system_platform == "Windows":
        verbose_print("Running on Windows", verbose=verbose)
        quantize_exec = 'quantize_win.exe'
    elif system_platform == "Darwin":
        verbose_print("Running on macOS", verbose=verbose)
        quantize_exec = 'quantize_mac'
    else:
        raise ValueError("Unknown operating system")
    # find executable file path inside package
    exec_path = os.path.join(os.path.dirname(__file__), quantize_exec)
    # run the quantization executable command
    quantized_model = f'{model_path.stem}_{quantization_method}.gguf'
    cmd = f'{exec_path} {target_gguf_model} {quantized_model} {quantization_method}'
    run_command(cmd, capture_output=not verbose)
    
#%% gptq    
@main.command(help='quantize large language model with gptq.')
@click.option('--model', 'target_model', type=str, required=True, help='target model path to be quantized')
@click.option('--bits', 'quantizated_bits', type=int, required=True, default=4, help='the number of bits to quantize to')
@click.option('--group-size', 'group_size', type=int, default=128, help='the group size to use for quantization. uses per-column quantization with value=-1.')
@click.option('--damp-percent', 'damp_percentage', type=float, default=0.01, help='percent of the average Hessian diagonal to use for dampening')
@click.option('--sample-path', 'sample_path', type=str, help='path of text file which contains sample texts to use for quantization.')
@click.option('--save-dir', 'save_directory', type=str, help='directory to save quantized model')
def quantize_gptq(target_model, quantizated_bits, group_size, damp_percentage, sample_path, save_directory):
    
    # check if model is a valid directory
    model_path = Path(target_model)
    if not model_path.is_dir():
        raise ValueError("Please provide a valid model directory")
    # set save directory by provided value
    if save_directory:
        save_dir = Path(save_directory)
    else:
        save_dir = None
    # sample texts to use for quantization
    if sample_path:
        sample_path = Path(sample_path)
        if not sample_path.is_file():
            raise ValueError("Please provide a valid sample texts file path.")
        with open(sample_path, 'r') as f:
            examples = f.readlines()
    else:
        examples = []
    # quantize model with gptq
    quantize(model_name_or_path=target_model, 
             bits=quantizated_bits,
             group_size=group_size,
             damp_percent=damp_percentage,
             examples=examples, 
             saved_dir=save_dir)