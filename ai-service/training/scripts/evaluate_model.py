import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_model(model_path: str):
    """Load trained model"""
    # TODO: Implement model loading
    return None

def load_test_data(data_path: str):
    """Load test dataset"""
    df = pd.read_csv(data_path)
    X_test = df['text'].values
    y_test = df['emotion'].values
    return X_test, y_test

def evaluate(model, X_test, y_test):
    """Evaluate model performance"""
    # TODO: Implement actual evaluation
    # Placeholder
    y_pred = y_test  # Replace with actual predictions
    
    # Classification report
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    return cm

def plot_confusion_matrix(cm, labels, output_path: str):
    """Plot confusion matrix"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(output_path)
    print(f"Confusion matrix saved to {output_path}")

if __name__ == "__main__":
    model = load_model("models/fine_tuned/emotion_model.pkl")
    X_test, y_test = load_test_data("training/datasets/processed/test.csv")
    
    cm = evaluate(model, X_test, y_test)
    
    labels = ["Hạnh phúc", "Yêu thương", "Quan tâm", "Buồn", "Lo lắng", "Giận dữ"]
    plot_confusion_matrix(cm, labels, "training/results/confusion_matrix.png")
