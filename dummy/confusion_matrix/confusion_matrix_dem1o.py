from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    accuracy_score, precision_score, recall_score, f1_score, classification_report
)
import matplotlib.pyplot as plt

# --- Ground truth (actual) and predicted results ---
y_true = [
    "detected", "not_detected", "detected", "detected",
    "not_detected", "detected", "not_detected", "not_detected",
    "detected", "not_detected", "detected", "detected", "not_detected"
]

y_pred = [
    "detected", "not_detected", "detected", "detected",
    "detected", "detected", "not_detected", "not_detected",
    "detected", "not_detected", "detected", "detected", "not_detected"
]

# ✅ Define readable display labels
display_labels = ["Microplastic Detected", "Microplastic Not Detected"]

# --- Confusion Matrix ---
cm = confusion_matrix(y_true, y_pred, labels=["detected", "not_detected"])

# --- Metrics ---
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, pos_label="detected")
recall = recall_score(y_true, y_pred, pos_label="detected")
f1 = f1_score(y_true, y_pred, pos_label="detected")

print("\n📊 MODEL PERFORMANCE METRICS")
print("----------------------------------")
print(f"✅ Accuracy  : {accuracy*100:.1f}%")
print(f"🎯 Precision : {precision:.2f}")
print(f"📈 Recall    : {recall:.2f}")
print(f"📊 F1-Score  : {f1:.2f}")

print("\nDetailed Classification Report:\n")
print(classification_report(y_true, y_pred, target_names=display_labels))

# --- Display Confusion Matrix ---
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
disp.plot(cmap="Blues", xticks_rotation=0)
plt.title("Confusion Matrix — Microplastic Detection (13 Test Images)")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

# Add performance text on the plot
textstr = f"Acc: {accuracy*100:.1f}%\nPrec: {precision:.2f}\nRec: {recall:.2f}\nF1: {f1:.2f}"
plt.gcf().text(0.73, 0.18, textstr, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig("confusion_matrix_result.png", dpi=300)
plt.show()

print("\n✅ Confusion Matrix saved as 'confusion_matrix_result.png'")
