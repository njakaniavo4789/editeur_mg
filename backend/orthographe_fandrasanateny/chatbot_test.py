from google import genai
from google.genai import types
import sys

def hanomboka_chat():
    print("--- TOROMARIKA ---")
    print("1. Mandehana ao amin'ny: https://aistudio.google.com/")
    print("2. Fafao ny API Key taloha, mamoròna vaovao (Create API key).")
    print("3. Rehefa manao 'Paste' (Ctrl+V) ianao, tandremo sao misy 'espace' eo aloha na aoriana.\n")

    # Ampiasaina ny input tsotra izao mba ho hitanao izay vao 'Paste'-nao
    api_key = input("Ampidiro ny API Key vaovao (Ctrl+V): ").strip()

    if not api_key:
        print("Error: Tsy nampiditra API Key ianao.")
        return

    try:
        # Fampiasana ny SDK vaovao (google-genai)
        client = genai.Client(api_key=api_key)
        
        sys_instruct = "Tsy maintsy mamaly amin'ny teny malagasy foana ianao. Manampy amin'ny fitadiavana teny mitovy hevitra sy conjugaison ianao."

        # Mampiasa Gemini 2.0 Flash izay stable amin'izao
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=sys_instruct)
        )

        print("\n--- Chatbot Malagasy VONONA ---")
        print("(Soraty 'exit' raha hijanona)")
        
        while True:
            user_input = input("\nIanao: ")
            if user_input.lower() in ['exit', 'hijanona', 'veloma']:
                break
            
            response = chat.send_message(user_input)
            print(f"Gemini: {response.text}")

    except Exception as e:
        print(f"\n[ERROR] Nisy olana teo amin'ny Google API: {e}")
        print("Soso-kevitra: Hamarino raha mbola manan-kery (active) ny API Key-nao ao amin'ny AI Studio.")

if __name__ == "__main__":
    hanomboka_chat()