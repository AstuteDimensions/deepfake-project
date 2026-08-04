import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from ai.datasets.dataset import load_datasets
from ai.models.model import get_model

# Force PyTorch to utilize CPU performance cores efficiently
torch.set_num_threads(8)

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    pbar = tqdm(dataloader, desc="  Training", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        total += labels.size(0)
        correct += preds.eq(labels).sum().item()
        pbar.set_postfix({"loss": f"{loss.item():.4f}"})
    return running_loss / total, (correct / total) * 100.0

def validate_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    pbar = tqdm(dataloader, desc="  Validating", leave=False)
    with torch.no_grad():
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            _, preds = outputs.max(1)
            total += labels.size(0)
            correct += preds.eq(labels).sum().item()
    return running_loss / total, (correct / total) * 100.0

def run_training(dataset_path, epochs=10, batch_size=128, lr=0.001, checkpoint_dir="ai/checkpoints"):
    device = torch.device("cpu")
    print(f"🚀 Training using device: {device} (Optimized for Intel Core Ultra 9)")
    
    train_loader, val_loader, _, classes = load_datasets(dataset_path, batch_size=batch_size)
    print(f"Classes found: {classes}")
    
    model = get_model(device=device)
    
    # --- Checkpoint Resuming Logic ---
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, "best_model.pth")
    best_val_acc = 0.0

    if os.path.exists(checkpoint_path):
        print(f"🔄 Found saved checkpoint! Resuming training from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Load model weights (handles both raw state_dict and dict with metadata)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
            best_val_acc = checkpoint.get("val_acc", 0.0)
        else:
            model.load_state_dict(checkpoint)
            
        print(f"✅ Loaded weights successfully (Previous Best Accuracy: {best_val_acc:.2f}%)")
    else:
        print("🆕 No checkpoint found. Starting fresh training from scratch...")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch [{epoch}/{epochs}] ---")
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate_epoch(model, val_loader, criterion, device)
        
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            # Save weights along with best validation accuracy
            save_data = {
                "model_state_dict": model.state_dict(),
                "val_acc": best_val_acc
            }
            torch.save(save_data, checkpoint_path)
            print(f"⭐ Best model updated and saved to {checkpoint_path} ({best_val_acc:.2f}% Acc)")

if __name__ == "__main__":
    DATASET_PATH = r"C:\Users\Ann\Desktop\Buildathon\Dataset"
    run_training(dataset_path=DATASET_PATH, epochs=10, batch_size=128)