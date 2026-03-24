import google.generativeai as genai
import os

# 1. Fakana ny API Key amin'ny fomba tsotra (input)
print("--- FANOMPOHANA ---")
api_key_input = input("Ampidiro ny API Key-nao (Ctrl+V): ").strip()

if not api_key_input:
    print("Error: Tsy maintsy mampiditra API Key ianao vao mandeha ny programa.")
    exit()

# Fanamboarana ny API
genai.configure(api_key=api_key_input)

# 2. Toromarika ho an'ny rafitra (System Instruction)
instruction = (
    "Tsy maintsy mamaly amin'ny teny malagasy foana ianao, na inona na inona fiteny ampiasain'ny olona. "
    "Manampy amin'ny fitadiavana teny mitovy hevitra (synonymes) sy conjugaison ianao. "
    "Raha misy teny teknika dia hazavaina amin'ny teny malagasy tsotra."
)

# Ampiasaina ny Gemini 1.5 Flash (manana Quota malalaka kokoa amin'ny Free Tier)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=instruction
)

# 3. Manomboka ny resaka
chat = model.start_chat(history=[])

print("\n--- Gemini Malagasy VONONA (Soraty 'exit' raha hijanona) ---")

while True:
    try:
        user_input = input("\nIanao: ")
        
        if user_input.lower() in ['exit', 'hijanona', 'veloma']:
            print("Gemini: Veloma finaritra!")
            break
            
        if not user_input.strip():
            continue

        response = chat.send_message(user_input)
        print(f"Gemini: {response.text}")

    except Exception as e:
        print(f"\n[ERROR] Nisy olana: {e}")
        print("Soso-kevitra: Miandrasa 30 segondra vao manontany indray raha lany ny quota.")