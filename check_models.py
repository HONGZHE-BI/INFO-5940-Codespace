import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url="https://api.ai.it.cornell.edu",
)

def get_available_models():
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        return available_models
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Checking available models from Cornell API...")
    available_models = get_available_models()
    
    if available_models:
        print(f"Found {len(available_models)} available models:")
        for i, model in enumerate(available_models, 1):
            print(f"{i:2d}. {model}")
            
        print("\n Embedding models found:")
        embedding_models = [m for m in available_models if 'embedding' in m.lower()]
        for model in embedding_models:
            print(f"   • {model}")
    else:
        print("No models found or error occurred")