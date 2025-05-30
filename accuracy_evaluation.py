#!/usr/bin/env python3
"""
Accuracy Evaluation Script
Compares Perplexity AI analysis results with original dataset labels and calculates accuracy metrics
"""

import os
import sys
import csv
import json
from datetime import datetime
from misinformation_detector import MisinformationDetector


def analyze_and_compare(input_file="FA-KES-Dataset.csv", num_articles=50, output_file=None):
    """
    Analyze articles with Perplexity and compare with original labels
    
    Args:
        input_file (str): Path to the input CSV file
        num_articles (int): Number of articles to analyze
        output_file (str): Path to save detailed results (optional)
    """
    # Get API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("Perplexity API key not found in environment variables.")
        print("Please enter your Perplexity API key:")
        api_key = input().strip()
        
        if not api_key:
            print("Error: API key is required to proceed.")
            sys.exit(1)
    
    # Initialize the detector
    print("Initializing Misinformation Detector...")
    detector = MisinformationDetector(api_key)
    
    # Set default output file if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"accuracy_evaluation_{timestamp}.csv"
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Analyzing {num_articles} articles...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Results tracking
    results = []
    correct_predictions = 0
    total_predictions = 0
    truthfulness_scores = []
    original_labels = []
    
    # Accuracy by threshold
    thresholds = [4, 5, 6]  # Different truthfulness thresholds to test
    threshold_results = {t: {'correct': 0, 'total': 0} for t in thresholds}
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Prepare output file with new columns
            fieldnames = reader.fieldnames + [
                'bias_score', 
                'truthfulness_score', 
                'severity_score', 
                'explanation', 
                'sources',
                'perplexity_prediction',
                'original_label_text',
                'correct_prediction',
                'analysis_timestamp'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                print(f"\nStarting analysis...")
                print("=" * 80)
                
                for row_num, row in enumerate(reader, 1):
                    if row_num > num_articles:
                        break
                    
                    # Get article content and original label
                    article_content = row.get('article_content', '').strip()
                    article_title = row.get('article_title', '').strip()
                    original_label = row.get('labels', '').strip()
                    
                    # Use article content if available, otherwise use title
                    content_to_analyze = article_content if article_content else article_title
                    
                    if not content_to_analyze or not original_label:
                        print(f"Row {row_num}: Missing content or label, skipping...")
                        continue
                    
                    # Convert label to boolean (0 = Real, 1 = Fake)
                    is_fake_original = original_label == '1'
                    
                    print(f"\nRow {row_num}: Analyzing article...")
                    print(f"Title: {article_title[:100]}...")
                    print(f"Original Label: {'Fake' if is_fake_original else 'Real'}")
                    
                    # Analyze the content
                    analysis = detector.analyze_post(content_to_analyze)
                    
                    if analysis:
                        # Determine Perplexity prediction based on truthfulness score
                        # Lower truthfulness = more likely to be fake
                        truthfulness = analysis.truthfulness
                        
                        # Test different thresholds
                        for threshold in thresholds:
                            is_fake_perplexity = truthfulness <= threshold
                            is_correct = is_fake_original == is_fake_perplexity
                            threshold_results[threshold]['total'] += 1
                            if is_correct:
                                threshold_results[threshold]['correct'] += 1
                        
                        # Use threshold of 5 as default for main accuracy calculation
                        is_fake_perplexity = truthfulness <= 5
                        is_correct = is_fake_original == is_fake_perplexity
                        
                        # Update results
                        total_predictions += 1
                        if is_correct:
                            correct_predictions += 1
                        
                        # Store data for detailed analysis
                        truthfulness_scores.append(truthfulness)
                        original_labels.append(1 if is_fake_original else 0)
                        
                        # Add analysis results to the row
                        row['bias_score'] = analysis.bias
                        row['truthfulness_score'] = analysis.truthfulness
                        row['severity_score'] = analysis.severity
                        row['explanation'] = analysis.explanation
                        row['sources'] = '; '.join(analysis.sources) if analysis.sources else ''
                        row['perplexity_prediction'] = 'Fake' if is_fake_perplexity else 'Real'
                        row['original_label_text'] = 'Fake' if is_fake_original else 'Real'
                        row['correct_prediction'] = 'Yes' if is_correct else 'No'
                        row['analysis_timestamp'] = datetime.now().isoformat()
                        
                        print(f"✓ Analysis complete - Truth: {analysis.truthfulness}, "
                              f"Prediction: {'Fake' if is_fake_perplexity else 'Real'}, "
                              f"Correct: {'Yes' if is_correct else 'No'}")
                        
                        results.append(row)
                    else:
                        print(f"✗ Analysis failed")
                        continue
                    
                    # Write the row to output file
                    writer.writerow(row)
                
                print("\n" + "=" * 80)
                print("ACCURACY EVALUATION RESULTS")
                print("=" * 80)
                
                if total_predictions > 0:
                    main_accuracy = (correct_predictions / total_predictions) * 100
                    print(f"Total articles analyzed: {total_predictions}")
                    print(f"Correct predictions: {correct_predictions}")
                    print(f"Main accuracy (threshold ≤5): {main_accuracy:.2f}%")
                    
                    print(f"\nAccuracy by different truthfulness thresholds:")
                    for threshold in thresholds:
                        thresh_data = threshold_results[threshold]
                        if thresh_data['total'] > 0:
                            thresh_accuracy = (thresh_data['correct'] / thresh_data['total']) * 100
                            print(f"  Threshold ≤{threshold}: {thresh_accuracy:.2f}% "
                                  f"({thresh_data['correct']}/{thresh_data['total']})")
                    
                    # Calculate additional metrics
                    print(f"\nDetailed Analysis:")
                    
                    # True/False positives and negatives
                    tp = fp = tn = fn = 0
                    for i, row in enumerate(results):
                        original_fake = row['original_label_text'] == 'Fake'
                        predicted_fake = row['perplexity_prediction'] == 'Fake'
                        
                        if original_fake and predicted_fake:
                            tp += 1
                        elif not original_fake and predicted_fake:
                            fp += 1
                        elif not original_fake and not predicted_fake:
                            tn += 1
                        elif original_fake and not predicted_fake:
                            fn += 1
                    
                    print(f"True Positives (Fake→Fake): {tp}")
                    print(f"False Positives (Real→Fake): {fp}")
                    print(f"True Negatives (Real→Real): {tn}")
                    print(f"False Negatives (Fake→Real): {fn}")
                    
                    # Calculate precision, recall, F1-score
                    if tp + fp > 0:
                        precision = tp / (tp + fp)
                        print(f"Precision: {precision:.3f}")
                    else:
                        precision = 0
                        print("Precision: N/A (no positive predictions)")
                    
                    if tp + fn > 0:
                        recall = tp / (tp + fn)
                        print(f"Recall: {recall:.3f}")
                    else:
                        recall = 0
                        print("Recall: N/A (no positive labels)")
                    
                    if tp + fp > 0 and tp + fn > 0 and (precision + recall) > 0:
                        f1_score = 2 * (precision * recall) / (precision + recall)
                        print(f"F1-Score: {f1_score:.3f}")
                    else:
                        print("F1-Score: N/A (insufficient data for calculation)")
                    
                    # Average truthfulness scores by label
                    fake_scores = [truthfulness_scores[i] for i, label in enumerate(original_labels) if label == 1]
                    real_scores = [truthfulness_scores[i] for i, label in enumerate(original_labels) if label == 0]
                    
                    if fake_scores:
                        avg_fake_truthfulness = sum(fake_scores) / len(fake_scores)
                        print(f"Average truthfulness for FAKE articles: {avg_fake_truthfulness:.2f}")
                    
                    if real_scores:
                        avg_real_truthfulness = sum(real_scores) / len(real_scores)
                        print(f"Average truthfulness for REAL articles: {avg_real_truthfulness:.2f}")
                    
                else:
                    print("No successful predictions to evaluate.")
                
                print(f"\nDetailed results saved to: {output_file}")
                
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
    except Exception as e:
        print(f"Error processing file: {e}")


def main():
    """
    Main function with options for accuracy evaluation
    """
    print("=" * 80)
    print("Perplexity AI Accuracy Evaluation")
    print("=" * 80)
    
    print("\nThis script will analyze articles and compare Perplexity predictions")
    print("with the original dataset labels to calculate accuracy metrics.")
    
    while True:
        print("\nSelect number of articles to analyze:")
        print("1. Quick test (10 articles)")
        print("2. Medium test (50 articles)")
        print("3. Large test (100 articles)")
        print("4. Custom number")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            analyze_and_compare(num_articles=10)
            break
        elif choice == '2':
            analyze_and_compare(num_articles=50)
            break
        elif choice == '3':
            analyze_and_compare(num_articles=100)
            break
        elif choice == '4':
            try:
                num_articles = int(input("Enter number of articles to analyze: ").strip())
                if num_articles > 0:
                    analyze_and_compare(num_articles=num_articles)
                else:
                    print("Please enter a positive number.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            break
        elif choice == '5':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 