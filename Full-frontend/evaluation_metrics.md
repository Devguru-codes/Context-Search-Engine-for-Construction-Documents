# Proposed Metrics for Model Accuracy Assessment

To holistically evaluate the performance of our information extraction pipeline, we propose a suite of three standard NLP metrics: **Precision, Recall, and F1-Score**. These will be calculated by comparing the model's extracted output against a manually verified "ground truth" dataset.

### 1. Precision: The "How Correct Is It?" Metric

*   **What it measures:** Of all the information our model extracted, what percentage of it was actually correct and relevant?
*   **Why it's important for this project:** High precision is crucial for earning user trust. An engineer needs to be confident that the information presented is not "noise" or irrelevant data. This metric directly measures how free from errors the output is.
*   **Formula:**
    ```
    Precision = (True Positives) / (True Positives + False Positives)
    ```
    *   **True Positive:** A piece of information (e.g., an IS code) that was correctly extracted.
    *   **False Positive:** A piece of information that was incorrectly extracted.

### 2. Recall: The "Did It Find Everything?" Metric

*   **What it measures:** Of all the correct and relevant information that existed in the source document, what percentage did our model successfully find?
*   **Why it's important for this project:** High recall is critical for ensuring compliance and safety. Missing a key material specification (a False Negative) could have serious consequences. This metric measures how comprehensive the model's extraction is.
*   **Formula:**
    ```
    Recall = (True Positives) / (True Positives + False Negatives)
    ```
    *   **False Negative:** A piece of relevant information that the model failed to extract.

### 3. F1-Score: The "Balanced" Metric

*   **What it measures:** The harmonic mean of Precision and Recall. It provides a single score that balances the trade-off between the two.
*   **Why it's the best overall metric:** In a real-world scenario, you need both high precision (no errors) and high recall (no omissions). A model that is perfect at one but terrible at the other is not useful. The F1-Score provides the best single measure of a model's overall effectiveness.
*   **Formula:**
    ```
    F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
    ```

### Summary for Presentation

> "To objectively measure our model's accuracy, we suggest using a framework based on three industry-standard metrics: Precision, Recall, and the F1-Score.
>
> *   **Precision** ensures that what we extract is correct.
> *   **Recall** ensures that we don't miss anything important.
> *   And the **F1-Score** gives us a balanced measure of overall performance.
>
> This approach will allow for a robust and comprehensive assessment of our model's ability to accurately and reliably extract critical information."
