import time
import transformers
import torch
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig


# Using Llama in place of PaLM
def request_llama(messages):
    try: 
        model = "meta-llama/Meta-Llama-3.1-70B"
        
        pipeline = transformers.pipeline(
            "text-generation", 
            model=model, 
            model_kwargs={"torch_dtype": torch.bfloat16},  
            device_map="auto"  
        )
        
        response = pipeline(
            messages, 
            max_length=1000,  
            do_sample=True,   
            top_k=50          
        )
        
        print("Response:")
        print(response)
        print("--------------------------------")
        
        if len(response) < 1:
            print("No output generated. Response is empty.")
            return None
        else:
            if 'generated_text' in response[0]:
                ret = response[0]['generated_text']
                print(f"Generated Text: {ret}")  
                return ret
            else:
                print("Key 'generated_text' not found in the response.")
                print(f"Response content: {response[0]}")
                return None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



# Using BioMistral in place of ChatGPT
def request_biomistral(prompt):
    try:
        bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",   
        bnb_4bit_compute_dtype=torch.bfloat16  
        )

        tokenizer = AutoTokenizer.from_pretrained("BioMistral/BioMistral-7B")
        model = AutoModel.from_pretrained("BioMistral/BioMistral-7B")

        pipeline = transformers.pipeline(
            task="text-generation", 
            model=model, 
            tokenizer=tokenizer,
            max_length=200,            
            do_sample=True,            
            top_k=50,                  
            device_map="auto"          
        )
        
        try:
            completion = pipeline(prompt)
            ret = completion[0]['generated_text'].strip()
            return ret
        
        except Exception as E:
            print(E)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

