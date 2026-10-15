# ── NEW CELL 1 :Plausibility function ─────shadow,lightining
import cv2
import numpy as np

def check_plausibility(image_path):
    img  = np.array(Image.open(image_path).convert("RGB").resize((224,224)))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Check 1: Lighting
    left  = np.mean(img[:, :w//2])
    right = np.mean(img[:, w//2:])
    lighting_diff = abs(left - right)

    # Check 2: Noise
    noises = []
    for r in range(3):
        for c in range(3):
            block = gray[r*h//3:(r+1)*h//3, c*w//3:(c+1)*w//3]
            noises.append(np.std(block))
    noise_score = np.std(noises) / (np.mean(noises) + 1e-6)

    # Check 3: Edges
    edges = cv2.Canny(gray, 50, 150)
    eq = [np.sum(edges[r*h//2:(r+1)*h//2, c*w//2:(c+1)*w//2])
          for r in range(2) for c in range(2)]
    edge_score = np.std(eq) / (np.mean(eq) + 1e-6)

    # Check 4: Shadow
    dark  = gray < 80
    s_ratio = np.sum(dark[:, :w//2]) / (np.sum(dark[:, w//2:]) + 1e-6)

    # Count suspicious signals
    suspicion = sum([
        lighting_diff > 25,
        noise_score   > 0.4,
        edge_score    > 0.8,
        s_ratio       > 3.0,
    ])

    return {
        "verdict"     : "FAKE" if suspicion >= 2 else "REAL",
        "suspicion"   : suspicion,
        "lighting"    : round(float(lighting_diff), 2),
        "noise"       : round(float(noise_score), 2),
        "edge"        : round(float(edge_score), 2),
        "shadow"      : round(float(s_ratio), 2),
    }

print("Plausibility function ready ✅")
