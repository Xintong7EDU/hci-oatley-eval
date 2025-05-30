#!/usr/bin/env python3
"""
Example usage of the MisinformationDetector class
"""

import os
from misinformation_detector import MisinformationDetector


def main():
    """
    Example demonstrating how to use the MisinformationDetector
    """
    # Get API key from environment variable
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("Please set the PERPLEXITY_API_KEY environment variable")
        print("Example: export PERPLEXITY_API_KEY='your_api_key_here'")
        return
    
    # Initialize the detector
    detector = MisinformationDetector(api_key)
    
    # Example 1: Analyze a single post
    print("=== Example 1: Single Post Analysis ===")
    sample_post = "Breaking: Scientists discover that drinking water can cure cancer! Share this before Big Pharma removes it!"
    
    analysis = detector.analyze_post(sample_post)
    
    if analysis:
        print(f"Post: {sample_post}")
        print(f"Bias Score: {analysis.bias}/10")
        print(f"Truthfulness Score: {analysis.truthfulness}/10")
        print(f"Severity Score: {analysis.severity}/10")
        print(f"Explanation: {analysis.explanation}")
        print(f"Sources: {', '.join(analysis.sources)}")
    else:
        print("Analysis failed")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Analyze CSV dataset (if it exists)
    print("=== Example 2: CSV Dataset Analysis ===")
    csv_file = "FA-KES-Dataset.csv"
    
    if os.path.exists(csv_file):
        print(f"Analyzing first 3 rows of {csv_file}...")
        
        # For demo purposes, let's just analyze a few rows
        import csv
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows_processed = 0
                
                for row in reader:
                    if rows_processed >= 3:  # Limit to 3 rows for demo
                        break
                    
                    # Assuming 'title' column contains the content
                    post_content = row.get('title', '')
                    
                    if post_content:
                        print(f"\nAnalyzing: {post_content[:100]}...")
                        analysis = detector.analyze_post(post_content)
                        
                        if analysis:
                            print(f"Bias: {analysis.bias}, Truthfulness: {analysis.truthfulness}, Severity: {analysis.severity}")
                        else:
                            print("Analysis failed")
                        
                        rows_processed += 1
                        
        except Exception as e:
            print(f"Error processing CSV: {e}")
    else:
        print(f"CSV file '{csv_file}' not found. Skipping CSV analysis.")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main() 