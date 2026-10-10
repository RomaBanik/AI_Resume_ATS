import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# =========================================================
# 1. PASTE YOUR GEMINI API KEY HERE
# =========================================================

 API_KEY = os.getenv("GEMINI_API_KEY")


# =========================================================
# 2. CREATE GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=API_KEY)


# =========================================================
# 3. GET AVAILABLE MODELS
# =========================================================

print("\n" + "=" * 60)
print("       GEMINI MODEL CHECKER")
print("=" * 60)

print("\nChecking your Gemini API key...\n")

try:

    models = list(client.models.list())

except Exception as e:

    print("❌ Could not connect to Gemini API.")
    print("\nError:")
    print(e)
    exit()


print("✅ API key is working.")
print("\nFinding models that support generateContent...\n")


# =========================================================
# 4. FIND MODELS THAT SUPPORT TEXT GENERATION
# =========================================================

working_candidates = []

for model in models:

    model_name = model.name

    supported_actions = getattr(
        model,
        "supported_actions",
        []
    )

    if "generateContent" in supported_actions:

        # Remove "models/" if present
        clean_name = model_name.replace(
            "models/",
            ""
        )

        working_candidates.append(clean_name)


# =========================================================
# 5. DISPLAY MODELS
# =========================================================

if not working_candidates:

    print("❌ No models supporting generateContent were found.")
    exit()


print("Models supporting generateContent:\n")

for model_name in working_candidates:

    print("✔", model_name)


# =========================================================
# 6. PREFERRED MODELS
# =========================================================

# We prefer Flash models for our ATS project because
# our project mainly needs text analysis and generation.

preferred_models = [

    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",

]


# =========================================================
# 7. TEST MODELS
# =========================================================

print("\n" + "=" * 60)
print("Testing models...")
print("=" * 60 + "\n")


tested_models = []


for preferred_model in preferred_models:

    if preferred_model not in working_candidates:

        continue


    print(f"Testing: {preferred_model}")

    try:

        response = client.models.generate_content(

            model=preferred_model,

            contents=(
                "Reply with only the word WORKING."
            )

        )

        if response and response.text:

            print(
                f"✅ {preferred_model} is WORKING!"
            )

            tested_models.append(
                preferred_model
            )

        else:

            print(
                f"⚠️ {preferred_model} returned empty response."
            )


    except Exception as e:

        error_message = str(e)

        print(
            f"❌ {preferred_model} failed."
        )

        print(
            "   Reason:",
            error_message[:250]
        )


# =========================================================
# 8. SELECT BEST WORKING MODEL
# =========================================================

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)


if tested_models:

    best_model = tested_models[0]

    print("\n🎉 GEMINI IS WORKING!")
    print("\nBest model for your ATS project:")

    print(
        f"\n    {best_model}\n"
    )

    print(
        "Use this in your app.py:"
    )

    print(
        f'\n    model="{best_model}"\n'
    )

else:

    print(
        "\n❌ None of the preferred Flash models worked."
    )

    print(
        "\nAvailable generateContent models were:"
    )

    for model_name in working_candidates:

        print(
            "   -",
            model_name
        )


print("\n" + "=" * 60)