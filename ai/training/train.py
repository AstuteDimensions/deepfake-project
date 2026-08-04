import os
import torch
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm

from ai.datasets.dataset import load_datasets
from ai.models.model import get_model


torch.set_num_threads(8)


def train_epoch(model, dataloader, criterion, optimizer, device):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training", leave=False)

    for images, labels in pbar:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item() * images.size(0)

        _, preds = outputs.max(1)

        total += labels.size(0)
        correct += preds.eq(labels).sum().item()

        pbar.set_postfix(loss=f"{loss.item():.4f}")

    return running_loss / total, 100 * correct / total



def validate_epoch(model, dataloader, criterion, device):

    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        pbar = tqdm(dataloader, desc="Validation", leave=False)

        for images, labels in pbar:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            _, preds = outputs.max(1)

            total += labels.size(0)
            correct += preds.eq(labels).sum().item()

    return running_loss / total, 100 * correct / total



def run_training(dataset_path,
                 epochs=15,
                 batch_size=64,
                 lr=1e-4,
                 checkpoint_dir="ai/checkpoints"):


    # GPU support
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Training on {device}")

    if device.type == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))


    train_loader, val_loader, _, classes = load_datasets(
        dataset_path,
        batch_size=batch_size
    )


    print("Classes:", classes)


    model = get_model(device=device)


    criterion = nn.CrossEntropyLoss()


    optimizer = optim.Adam(
        model.parameters(),
        lr=lr,
        weight_decay=1e-4
    )


    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.5,
        patience=2
    )


    os.makedirs(checkpoint_dir, exist_ok=True)


    checkpoint_path = os.path.join(
        checkpoint_dir,
        "best_model.pth"
    )


    best_val_acc = 0.0


    if os.path.exists(checkpoint_path):

        checkpoint = torch.load(
            checkpoint_path,
            map_location=device
        )


        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:

            model.load_state_dict(
                checkpoint["model_state_dict"]
            )

            best_val_acc = checkpoint.get(
                "val_acc",
                0.0
            )

            print(
                f"Resumed training (Best Accuracy: {best_val_acc:.2f}%)"
            )


        else:

            print("Old checkpoint detected.")

            model.load_state_dict(checkpoint)


    else:

        print("Starting new training.")



    for epoch in range(epochs):

        print(f"\nEpoch {epoch+1}/{epochs}")


        train_loss, train_acc = train_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device
        )


        val_loss, val_acc = validate_epoch(
            model,
            val_loader,
            criterion,
            device
        )


        scheduler.step(val_acc)


        print(f"Train Loss : {train_loss:.4f}")
        print(f"Train Acc  : {train_acc:.2f}%")

        print(f"Val Loss   : {val_loss:.4f}")
        print(f"Val Acc    : {val_acc:.2f}%")


        current_lr = optimizer.param_groups[0]["lr"]

        print(f"Learning Rate : {current_lr}")


        if val_acc > best_val_acc:

            best_val_acc = val_acc


            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "val_acc": best_val_acc
                },
                checkpoint_path
            )


            print(
                f"⭐ Best Model Saved ({best_val_acc:.2f}%)"
            )


    print("\nTraining Complete!")



if __name__ == "__main__":


    DATASET_PATH = r"C:\Users\Ann\Desktop\Buildathon\Dataset"


    run_training(
        dataset_path=DATASET_PATH,
        epochs=15,
        batch_size=64,
        lr=1e-4
    )