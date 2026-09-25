from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Réponds simplement : connexion Gemini réussie."
)

print(interaction.output_text)