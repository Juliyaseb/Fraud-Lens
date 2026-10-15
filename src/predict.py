# ── CELL 10 : Prediction function ────────────────────────────
def fraud_lens_predict(image_path, true_label=None):

    # Signal 1 — ResNet on raw image
    img    = Image.open(image_path).convert("RGB")
    tensor = resnet_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        probs     = torch.softmax(model(tensor), dim=1)[0]
        real_prob = probs[0].item() * 100
        fake_prob = probs[1].item() * 100

    resnet_pred = "FAKE" if fake_prob >= 50 else "REAL"

 
