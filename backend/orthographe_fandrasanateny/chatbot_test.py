from google import genai
from google.genai import types
import getpass # Ity no ampiasaina mba tsy hiseho eo amin'ny écran izay soratanao

def hanomboka_chat():
    print("--- TOROMARIKA MOMBA NY API KEY ---")
    print("1. Mandehana ao amin'ny: https://aistudio.google.com/")
    print("2. Fafao ilay API Key taloha (raha mbola eo).")
    print("3. Tsindrio ny 'Create API key' hahazoana iray vaovao tanteraka.")
    print("----------------------------------\n")

    # Ampiasaina ny getpass mba ho feno kintana (*) ny teny soratanao ho fiarovana
    api_key = getpass.getpass("Ampidiro ny API Key vaovao (tsy hiseho ny soratra): ")

    try:
        client = genai.Client(api_key=api_key)
        
        # Toromarika ho an'ny rafitra
        sys_instruct = "Tsy maintsy mamaly amin'ny teny malagasy foana ianao. Manampy amin'ny fitadiavana teny mitovy hevitra sy conjugaison ianao."

        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=sys_instruct)
        )

        print("\n--- Chatbot Malagasy vonona (Soraty 'exit' raha hampiato) ---")
        
        while True:
            user_input = input("\nIanao: ")
            if user_input.lower() in ['exit', 'hijanona', 'veloma']:
                print("Gemini: Veloma finaritra!")
                break
            
            response = chat.send_message(user_input)
            print(f"Gemini: {response.text}")

    except Exception as e:
        print(f"\n[ERROR] Nisy olana: {e}")
        print("Hamarino tsara ilay API Key vaovao vao noforoninao.")

if __name__ == "__main__":
    hanomboka_chat()