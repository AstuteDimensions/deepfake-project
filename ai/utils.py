import os
import torch
import matplotlib.pyplot as plt

def save_checkpoint(model, optimizer, epoch, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict()
    }
    torch.save(state, path)

def load_checkpoint(model, optimizer, path, device):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No checkpoint found at {path}")
    checkpoint = torch.load(path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])
    if optimizer and "optimizer_state" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state"])
    return checkpoint.get("epoch", 0)

def plot_training_history(train_losses, val_losses, train_accs, val_accs, save_path=None):
    epochs = range(1, len(train_losses) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(epochs, train_losses, label="Train Loss")
    ax1.plot(epochs, val_losses, label="Val Loss")
    ax1.set_title("Loss History")
    ax1.set_xlabel("Epochs")
    ax1.legend()
    
    ax2.plot(epochs, train_accs, label="Train Acc (%)")
    ax2.plot(epochs, val_accs, label="Val Acc (%)")
    ax2.set_title("Accuracy History")
    ax2.set_xlabel("Epochs")
    ax2.legend()
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()