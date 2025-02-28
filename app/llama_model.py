import time
from llama_cpp import Llama

# Configuración del modelo con ajustes
llm = Llama(
    model_path="mistral-7b-instruct.Q4_K_M.gguf",  # Asegúrate de que el archivo exista en la ruta configurada
    n_ctx=2024,      # Context window de 512 tokens
    n_threads=4,    # Ajusta según tu CPU
    n_batch=8,      # Puedes probar con diferentes valores
    use_mlock=True  # Esto puede estabilizar el rendimiento en algunos sistemas
)

# Realizar un warm-up
llm("Calienta el modelo", max_tokens=10)

def truncate_text(text: str, max_chars: int = 2000) -> str:
    """
    Trunca el texto a un máximo de caracteres para evitar exceder el contexto.
    """
    if len(text) > max_chars:
        return text[:max_chars]
    return text

def generate_summary(text: str, max_tokens: int = 150) -> str:
    """
    Genera un resumen del texto dado utilizando el modelo Llama.
    Si el texto es muy extenso, se trunca para evitar exceder el context window.
    """
    truncated_text = truncate_text(text, max_chars=2000)
    prompt = f"Resume el siguiente texto de forma clara y concisa:\n\n{truncated_text}\n\nResumen:"
    start_time = time.time()
    response = llm(prompt, max_tokens=max_tokens)
    elapsed_time = time.time() - start_time
    print(f"Tiempo de respuesta del resumen: {elapsed_time:.2f} segundos")
    summary = response["choices"][0]["text"].strip()
    return summary

def answer_question(question: str, context: str, max_tokens: int = 100) -> str:
    """
    Responde una pregunta basada en el contexto dado utilizando el modelo Llama.
    Se trunca el contexto si es demasiado extenso.
    """
    truncated_context = truncate_text(context, max_chars=2000)
    prompt = f"Contexto:\n{truncated_context}\n\nPregunta: {question}\n\nRespuesta:"
    start_time = time.time()
    response = llm(prompt, max_tokens=max_tokens)
    elapsed_time = time.time() - start_time
    print(f"Tiempo de respuesta para la pregunta: {elapsed_time:.2f} segundos")
    answer = response["choices"][0]["text"].strip()
    return answer
