from transformers import AutoModel, AutoTokenizer

# Specify the model name
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Specify the local directory to save the model
local_directory = "./model"

# Download and save the model and tokenizer
def download_model():
    # Download the model
    model = AutoModel.from_pretrained(model_name)
    # Save the model locally
    model.save_pretrained(local_directory)

    # Download the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # Save the tokenizer locally
    tokenizer.save_pretrained(local_directory)

    print(f"Model and tokenizer have been saved to {local_directory}")

# Run the function
download_model()
