#!/usr/bin/env python3
"""
Script to run article content through Perplexity misinformation detection
This script processes the FA-KES-Dataset.csv file and analyzes each article using the MisinformationDetector
"""

import os
import sys
import csv
import json
from datetime import datetime
from misinformation_detector import MisinformationDetector
from utils import get_api_key


def analyze_articles(input_file="FA-KES-Dataset.csv", output_file=None, max_articles=None):
    """
    Analyze articles from the CSV dataset using Perplexity AI
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save results (optional)
        max_articles (int): Maximum number of articles to analyze (optional, for testing)
    """
    # Get API key
    api_key = get_api_key()
    
    # Initialize the detector
    print("Initializing Misinformation Detector...")
    detector = MisinformationDetector(api_key)
    
    # Set default output file if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"analyzed_articles_{timestamp}.csv"
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Process the CSV file
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
                'analysis_timestamp'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                processed_count = 0
                failed_count = 0
                
                print(f"\nStarting analysis...")
                print("=" * 60)
                
                for row_num, row in enumerate(reader, 1):
                    # Check if we've reached the maximum number of articles
                    if max_articles and processed_count >= max_articles:
                        print(f"Reached maximum article limit ({max_articles}). Stopping.")
                        break
                    
                    # Get article content - prioritize article_content, fallback to article_title
                    article_content = row.get('article_content', '').strip()
                    article_title = row.get('article_title', '').strip()
                    
                    # Use article content if available, otherwise use title
                    content_to_analyze = article_content if article_content else article_title
                    
                    if not content_to_analyze:
                        print(f"Row {row_num}: No content found, skipping...")
                        failed_count += 1
                        continue
                    
                    print(f"\nRow {row_num}: Analyzing article...")
                    print(f"Title: {article_title[:100]}...")
                    
                    # Analyze the content
                    analysis = detector.analyze_post(content_to_analyze)
                    
                    if analysis:
                        # Add analysis results to the row
                        row['bias_score'] = analysis.bias
                        row['truthfulness_score'] = analysis.truthfulness
                        row['severity_score'] = analysis.severity
                        row['explanation'] = analysis.explanation
                        row['sources'] = '; '.join(analysis.sources) if analysis.sources else ''
                        row['analysis_timestamp'] = datetime.now().isoformat()
                        
                        print(f"✓ Analysis complete - Bias: {analysis.bias}, Truth: {analysis.truthfulness}, Severity: {analysis.severity}")
                        processed_count += 1
                    else:
                        # Mark failed analysis
                        row['bias_score'] = ''
                        row['truthfulness_score'] = ''
                        row['severity_score'] = ''
                        row['explanation'] = 'Analysis failed'
                        row['sources'] = ''
                        row['analysis_timestamp'] = datetime.now().isoformat()
                        
                        print(f"✗ Analysis failed")
                        failed_count += 1
                    
                    # Write the row to output file
                    writer.writerow(row)
                
                print("\n" + "=" * 60)
                print(f"Analysis complete!")
                print(f"Total articles processed: {processed_count}")
                print(f"Failed analyses: {failed_count}")
                print(f"Results saved to: {output_file}")
                
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
    except Exception as e:
        print(f"Error processing file: {e}")


def show_sample_analysis(num_samples=3):
    """
    Show a sample analysis of a few articles for testing
    
    Args:
        num_samples (int): Number of sample articles to analyze
    """
    print(f"Running sample analysis on {num_samples} articles...")
    analyze_articles(max_articles=num_samples)


def main():
    """
    Main function with interactive menu
    """
    print("=" * 60)
    print("Article Content Analysis with Perplexity AI")
    print("=" * 60)
    
    while True:
        print("\nSelect an option:")
        print("1. Analyze sample articles (3 articles)")
        print("2. Analyze all articles in dataset")
        print("3. Analyze specific number of articles")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            show_sample_analysis(3)
            break
        elif choice == '2':
            print("\nWarning: This will analyze all articles in the dataset.")
            print("This may take a long time and consume API credits.")
            confirm = input("Continue? (y/N): ").strip().lower()
            
            if confirm == 'y':
                analyze_articles()
            else:
                print("Operation cancelled.")
            break
        elif choice == '3':
            try:
                num_articles = int(input("Enter number of articles to analyze: ").strip())
                if num_articles > 0:
                    analyze_articles(max_articles=num_articles)
                else:
                    print("Please enter a positive number.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            break
        elif choice == '4':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 