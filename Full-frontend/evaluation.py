from sklearn.metrics import precision_score, recall_score, f1_score

def evaluate_extraction(true_labels, predicted_labels):
    """
    Calculates precision, recall, and F1-score for the extraction.
    
    Args:
        true_labels (list): A list of true labels (e.g., extracted material names).
        predicted_labels (list): A list of predicted labels from the model.
        
    Returns:
        dict: A dictionary containing precision, recall, and F1-score.
    """
    # This is a placeholder function. To use it, you would need to:
    # 1. Create a labeled test set with ground truth extractions.
    # 2. Convert the model's output and the ground truth to a comparable format
    #    (e.g., lists of strings or tuples).
    # 3. Handle cases where the lengths of true_labels and predicted_labels might differ.
    
    # For now, this is a simplified example assuming a one-to-one mapping.
    # A real implementation would require more complex logic for entity matching.
    
    # Ensure labels are in a consistent format for comparison
    true_set = set(true_labels)
    pred_set = set(predicted_labels)
    
    # Calculate true positives, false positives, and false negatives
    tp = len(true_set.intersection(pred_set))
    fp = len(pred_set.difference(true_set))
    fn = len(true_set.difference(pred_set))
    
    # Calculate precision, recall, and F1-score
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

if __name__ == '__main__':
    # Example usage:
    # This would be used with a manually labeled dataset for evaluation.
    
    # Example ground truth data
    true_materials = ["Cement", "Fine Aggregate", "Steel", "Water"]
    
    # Example model predictions
    predicted_materials = ["Cement", "Aggregate", "Steel", "Admixtures"]
    
    # evaluation_results = evaluate_extraction(true_materials, predicted_materials)
    # print("Evaluation Results:")
    # print(f"Precision: {evaluation_results['precision']:.2f}")
    # print(f"Recall: {evaluation_results['recall']:.2f}")
    # print(f"F1-Score: {evaluation_results['f1_score']:.2f}")
    pass
