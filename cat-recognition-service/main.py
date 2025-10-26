import sys
import io
import base64
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
model = AutoModelForImageClassification.from_pretrained("akahana/vit-base-cats-vs-dogs").to(device)
model.eval()

def is_cat_image(image_bytes: bytes) -> bool:
    print(torch.__version__)
    print(torch.version.cuda)       # Shows the CUDA version PyTorch was built for
    print(torch.cuda.is_available())  # True if GPU is detected
    
    print("Using device:", device)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU name:", torch.cuda.get_device_name(0))
        print("Memory allocated (MB):", torch.cuda.memory_allocated(0) / 1024**2)
        print("Memory reserved (MB):", torch.cuda.memory_reserved(0) / 1024**2)


    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = logits.softmax(-1)[0]

    label = model.config.id2label[probs.argmax().item()]
    print(f"Predicted label: {label} ({probs.max().item():.2f})")

    # Match any label containing "cat" OR known feline-related labels
    cat_keywords = ["cat", "lynx", "tiger cat", "Egyptian cat", "Siamese cat", "Persian cat"]
    return any(keyword.lower() in label.lower() for keyword in cat_keywords)


if __name__ == "__main__":
    # Read base64 data from STDIN
    b64_string = sys.stdin.read().strip()
    if not b64_string:
        print("Usage: powershell: ... | python cat_check.py")
        sys.exit(1)

    try:
        image_bytes = base64.b64decode(b64_string)
    except Exception as e:
        print("❌ Invalid base64 input:", e)
        sys.exit(1)

    print("🐱 This is a cat!" if is_cat_image(image_bytes) else "🚫 Not a cat.")
