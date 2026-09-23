from google import genai

client = genai.Client(
    vertexai=True,
    project="aquashield-bengaluru",
    location="global"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="In one sentence, explain why water conservation matters."
)

print(response.text)