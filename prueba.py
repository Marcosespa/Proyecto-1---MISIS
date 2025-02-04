import time
from llama_cpp import Llama

# MODELO USADO Mistral 7B Q4_K_M (4GB)
llm = Llama(model_path="mistral-7b-instruct.Q4_K_M.gguf")


start_time = time.time()

# Prompt de texto, definir 50 tokens como máximo
response = llm("¿Cuál es la capital de Francia?", max_tokens=50)

end_time = time.time()
elapsed_time = end_time - start_time

respuesta_final = response["choices"][0]["text"].strip()
print("La respues final es:"+respuesta_final)
print(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")
