# ── CELL 6 : Load ResNet50 ────────────────────────────────────
model = models.resnet50(pretrained=True)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace final layer with dropout
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(num_features, 2)
)
model = model.to(device)
print("ResNet50 loaded ✅")
print("Final layer replaced ✅")
