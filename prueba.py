import time
from llama_cpp import Llama

# Configuración del modelo con ajustes
llm = Llama(
    model_path="mistral-7b-instruct.Q4_K_M.gguf",
    n_ctx=512,  # Ajusta según la longitud de tu texto
    n_threads=4,  # Ajusta según tu CPU
    n_batch=8,   # Puedes probar con diferentes valores
    use_mlock=True  # Esto puede estabilizar el rendimiento en algunos sistemas
)

# Realizar un warm-up
llm("Un prompt corto para calentar el modelo", max_tokens=10)

start_time = time.time()

# Prompt de texto, definir 50 tokens como máximo
response = llm("Hazme un resumen de la pelicula transformers 1 porfavor", max_tokens=100)

end_time = time.time()
elapsed_time = end_time - start_time

respuesta_final = response["choices"][0]["text"].strip()
print("La respuesta final es: " + respuesta_final)
print(f"Tiempo de respuesta: {elapsed_time:.2f} segundos")