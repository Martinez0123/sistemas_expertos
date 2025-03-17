import json
import os

def cargar_conocimiento():
    if os.path.exists("conocimiento.json"):
        with open("conocimiento.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return {"Hola": "¿Cómo estás?", "¿Cómo estás?": "¿De qué te gustaría hablar?"}

def guardar_conocimiento(conocimiento):
    with open("conocimiento.json", "w", encoding="utf-8") as file:
        json.dump(conocimiento, file, indent=4, ensure_ascii=False)

def obtener_respuesta(mensaje, conocimiento):
    return conocimiento.get(mensaje, None)

def chatbot():
    conocimiento = cargar_conocimiento()
    print("Chatbot: ¡Hola! Escribe 'salir' para terminar la conversación.")
    
    while True:
        usuario = input("Tú: ")
        if usuario.lower() == "salir":
            print("Chatbot: ¡Hasta luego!")
            break
        
        respuesta = obtener_respuesta(usuario, conocimiento)
        
        if respuesta:
            print(f"Chatbot: {respuesta}")
        else:
            print("Chatbot: No sé la respuesta. ¿Cómo debería responder?")
            nueva_respuesta = input("Nueva respuesta: ")
            conocimiento[usuario] = nueva_respuesta
            guardar_conocimiento(conocimiento)
            print("Chatbot: ¡Gracias! Ahora lo recordaré.")

if __name__ == "__main__":
    chatbot()
