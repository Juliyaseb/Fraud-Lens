import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# __ CELL 12 : Prediction function ────────────────────────────
def fraud_lens_predict(image_path, true_label=None):
    # 1. ResNet Signal
    img = Image.open(image_path).convert("RGB")
    img_t = val_transform(img).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        output = model(img_t)
        res_prob = torch.softmax(output, dim=1)[0][1].item()

    # 2. Plausibility Signal (Your manual metrics)
    p = check_plausibility(image_path)

    # 3. XGBoost Ensemble Decision
    # Create a small dataframe for the single image
    input_data = pd.DataFrame([
        {
            'resnet_score': res_prob,
            'lighting': p['lighting'],
            'noise': p['noise'],
            'edge': p['edge'],
            'shadow': p['shadow']
        }
    ])

    final_prob = xgb_model.predict_proba(input_data)[0][1] # Prob of FAKE
    final_verdict = "FAKE" if final_prob >= 0.5 else "REAL"

    print("─"*40)
    print(f"  File: {os.path.basename(image_path)}")
    if true_label:
        print(f"  True Label            : {true_label}")
    print(f"  🔍 FRAUD LENS VERDICT : {final_verdict} ({final_prob*100:.1f}% confidence)")
    print("─"*40)
    print(f"  ResNet Probability  : {res_prob*100:.1f}% (of being FAKE)")
    print(f"  Lighting Score      : {p['lighting']}")
    print(f"  Noise Score         : {p['noise']}")
    print(f"  Edge Score          : {p['edge']}")
    print(f"  Shadow Score        : {p['shadow']}")
    print("─"*40)

    # Plotting the image
    plt.figure(figsize=(6, 6))
    plt.imshow(mpimg.imread(image_path))
    plt.title(f"Verdict: {final_verdict} ({final_prob*100:.1f}%) -- True: {true_label or 'N/A'}")
    plt.axis('off')
    plt.show()
