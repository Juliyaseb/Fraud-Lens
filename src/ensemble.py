 # Combined decision
    if resnet_pred == "FAKE" or plaus["verdict"] == "FAKE":
        final = "FAKE"
        conf  = fake_prob
    else:
        final = "REAL"
        conf  = real_prob

    # Generate reasons
    reasons = []
    if resnet_pred == "FAKE":
        reasons.append(
            f"ResNet50 detected manipulation patterns "
            f"in image texture and boundaries "
            f"(confidence: {fake_prob:.1f}%)"
        )
    if plaus["lighting"] > 25:
        reasons.append(
            f"Lighting inconsistency detected "
            f"(diff: {plaus['lighting']}) — "
            f"brightness mismatch between image regions"
        )
    if plaus["noise"] > 0.4:
        reasons.append(
            f"Noise pattern mismatch "
            f"(score: {plaus['noise']:.2f}) — "
            f"inconsistent camera noise across regions"
        )
    if plaus["edge"] > 0.8:
        reasons.append(
            f"Unnatural edge patterns "
            f"(score: {plaus['edge']:.2f}) — "
            f"artificial boundaries detected"
        )
    if not reasons and final == "REAL":
        reasons.append(
            "No manipulation signatures detected. "
            "Image textures and physical properties "
            "are consistent with authentic photograph."
        )

    # Show result
    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    ax.imshow(img.resize((224, 224)))
    color = "red" if final == "FAKE" else "green"
    ax.set_title(
        f"🔍 FRAUD LENS — {final} ({conf:.1f}%)",
        fontsize=12, color=color
    )
    ax.axis("off")
    plt.tight_layout()
    plt.show()

    # Print verdict
    print("\n" + "="*55)
    print(f"  🔍 FRAUD LENS VERDICT  : {final}")
    print(f"  ResNet Signal          : {resnet_pred} ({fake_prob:.1f}%)")
    print(f"  Plausibility Signal    : {plaus['verdict']} ({plaus['suspicion']}/4 flags)")
    if true_label:
        ok = "✅ CORRECT" if final == true_label else "❌ WRONG"
        print(f"  True Label             : {true_label}")
        print(f"  Result                 : {ok}")
    print(f"\n  REASONS:")
    for i, r in enumerate(reasons, 1):
        print(f"  {i}. {r}")
    print(f"\n  Physical Analysis:")
    print(f"  → Lighting diff        : {plaus['lighting']}")
    print(f"  → Noise score          : {plaus['noise']}")
    print(f"  → Edge score           : {plaus['edge']}")
    print(f"  → Shadow ratio         : {plaus['shadow']}")
    print("="*55)

    return final, conf
