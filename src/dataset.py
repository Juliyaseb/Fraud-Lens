# ── CELL 3 : ResNet transforms ───────────────────────────────

# ResNet50 expects ImageNet normalization
resnet_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225]
    )
])
print("Transforms ready ✅")

# ── CELL 4 : Dataset class ────────────────────────────────────
class CarDataset(Dataset):
    def __init__(self, image_paths, labels, transform):
        self.image_paths = image_paths
        self.labels      = labels
        self.transform   = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert("RGB")
        return self.transform(img), self.labels[idx]

print("Dataset class ready ✅")

# ── CELL 5 : Split + DataLoaders ─────────────────────────────
X_temp, X_test, y_temp, y_test = train_test_split(
    all_paths, all_labels,
    test_size=0.15, random_state=42, stratify=all_labels
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp,
    test_size=0.176, random_state=42, stratify=y_temp
)

train_loader = DataLoader(
    CarDataset(X_train, y_train, resnet_transform),
    batch_size=16, shuffle=True
)
val_loader = DataLoader(
    CarDataset(X_val, y_val, resnet_transform),
    batch_size=16, shuffle=False
)
test_loader = DataLoader(
    CarDataset(X_test, y_test, resnet_transform),
    batch_size=16, shuffle=False
)

print(f"Train : {len(X_train)}")
print(f"Val   : {len(X_val)}")
print(f"Test  : {len(X_test)}")
print("DataLoaders ready ✅")
