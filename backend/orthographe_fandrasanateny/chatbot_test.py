import google.generativeai as genai

# 1. Ampidiro ny API Key-nao
genai.configure(api_key="AIzaSyAWqd4Q_fNJqVgwdDM-ZV8G58TToKtqTP0")

# 2. Amboary ny "System Instruction" mba hiteny malagasy foana izy
instruction = "Tsy maintsy mamaly amin'ny teny malagasy foana ianao, na inona na inona fiteny ampiasain'ny olona miresaka aminao. Raha misy teny teknika dia azonao hazavaina amin'ny teny malagasy tsotra."

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Ity no modely haingana sy maimaim-poana
    system_instruction=instruction
)

# 3. Manomboka ny resaka
chat = model.start_chat(history=[])

print("--- Gemini amin'ny teny malagasy (Soraty 'exit' raha hampiato) ---")

while True:
    user_input = input("Ianao: ")
    if user_input.lower() == 'exit':
        break
        
    response = chat.send_message(user_input)
    print(f"Gemini: {response.text}")