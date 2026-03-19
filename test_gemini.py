import google.generativeai as genai

# 🔑 Replace with your API key
genai.configure(api_key="AIzaSyCJ6QAL6QeAKtqMDHDTZcwpwRoziyi9Row")

try:
    # ✅ Use working model from your list
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = "Generate 1 simple quiz question about Python lists with 4 options and answer."

    response = model.generate_content(prompt)

    print("\n✅ API KEY WORKING\n")
    print("Response:\n")
    print(response.text)

except Exception as e:
    print("\n❌ ERROR:\n")
    print(e)