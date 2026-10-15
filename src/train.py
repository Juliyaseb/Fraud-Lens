# ── CELL 7 : Train ───────────────────────────────────────────
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)

EPOCHS   = 10
best_acc = 0
train_losses, val_losses, val_accs = [], [], []

print("Training started...")

for epoch in range(EPOCHS):
    # Training
    model.train()
    running_loss = 0
    for X_batch, y_batch in train_loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        optimizer.zero_grad()
        loss = criterion(model(X_batch), y_batch)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Validation
    model.eval()
    preds, actuals = [], []
    val_loss = 0
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            val_loss += criterion(outputs, y_batch.to(device)).item()
            preds.extend(torch.argmax(outputs, 1).cpu().numpy())
            actuals.extend(y_batch.numpy())

    acc = accuracy_score(actuals, preds)
    train_losses.append(running_loss / len(train_loader))
    val_losses.append(val_loss / len(val_loader))
    val_accs.append(acc)

    if acc > best_acc:
        best_acc = acc
        torch.save(
            model.state_dict(),
            "/content/drive/MyDrive/fraud-lens/model/fraud_lens_raw.pth"
        )
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {train_losses[-1]:.4f} | Val Acc: {acc:.4f} ← BEST ✅")
    else:
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {train_losses[-1]:.4f} | Val Acc: {acc:.4f}")

print(f"\nBest accuracy : {best_acc:.4f}")
print("Training complete ✅")


# ── CELL 8 : Evaluate on test set ────────────────────────────
model.load_state_dict(torch.load(
    "/content/drive/MyDrive/fraud-lens/model/fraud_lens_raw.pth",
    map_location=device
))
model.eval()

preds, actuals = [], []
with torch.no_grad():
    for X_batch, y_batch in test_loader:
        preds.extend(
            torch.argmax(model(X_batch.to(device)), 1).cpu().numpy()
        )
        actuals.extend(y_batch.numpy())

print("="*45)
print("TEST RESULTS")
print("="*45)
print(classification_report(actuals, preds, target_names=["Real","Fake"]))

cm = confusion_matrix(actuals, preds)
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].imshow(cm, cmap="Blues")
axes[0].set_title("Confusion Matrix")
axes[0].set_xlabel("Predicted")
axes[0].set_ylabel("Actual")
axes[0].set_xticks([0,1]); axes[0].set_xticklabels(["Real","Fake"])
axes[0].set_yticks([0,1]); axes[0].set_yticklabels(["Real","Fake"])
for i in range(2):
    for j in range(2):
        axes[0].text(j, i, cm[i,j], ha="center", va="center",
                     color="white" if cm[i,j] > cm.max()/2 else "black",
                     fontsize=14)
axes[1].plot(train_losses, label="Train Loss")
axes[1].plot(val_losses,   label="Val Loss")
axes[1].plot(val_accs,     label="Val Accuracy")
axes[1].set_title("Training Curves")
axes[1].set_xlabel("Epoch")
axes[1].legend()
plt.tight_layout()
plt.savefig("/content/drive/MyDrive/fraud-lens/model/training_results_raw.png", dpi=120)
plt.show()
print("Results saved ✅")
