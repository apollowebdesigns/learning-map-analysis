

def calculate_metrics(predicted, true):
    """
    Calculate various metrics for evaluating the performance of a model.

    Args:
        predicted (list): Predicted set of elements.
        true (list): True set of elements.

    Returns:
        dict: A dictionary containing the calculated metrics.
    """

    # True Positives (TP): Elements in both predicted and true sets
    tp = len(set(predicted) & set(true))

    # False Positives (FP): Elements in predicted set but not in true set
    len(set(predicted) - set(true))

    # False Negatives (FN): Elements in true set but not in predicted set
    fn = len(set(true) - set(predicted))

    # True Negatives (TN): For this case, we don't have a clear definition of TN
    # So we'll use a modified accuracy calculation

    # Calculate metrics
    precision = tp / len(predicted) if len(predicted) > 0 else 0
    recall = tp / len(true) if len(true) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Accuracy calculation
    accuracy = tp / len(predicted) if len(predicted) > 0 else 0
    
    # percentage_covered = 100 * fn/len(set(true))
    percentage_covered = 100 * len(set(true).intersection(predicted))/len(set(true))
    journey_size = len(set(predicted))
    actual_size = len(set(true))

    # Return a dictionary containing the calculated metrics
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy,
        'percentage_covered': percentage_covered,
        'journey_size': journey_size,
        'actual_size': actual_size,
        'predicted_learning_journey': predicted,
        'actual_learning_journey': true,
    }
