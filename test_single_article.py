#!/usr/bin/env python3
"""
Quick test script to analyze a single article from the dataset
"""

import os
import csv
from misinformation_detector import MisinformationDetector


def test_single_article():
    """
    Test the analysis with a single article from the CSV dataset
    """
    # Get API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("Perplexity API key not found in environment variables.")
        print("Please enter your Perplexity API key:")
        api_key = input().strip()
        
        if not api_key:
            print("Error: API key is required to proceed.")
            return
    
    # Initialize detector
    print("Initializing Misinformation Detector...")
    detector = MisinformationDetector(api_key)
    
    # Read the first article from the CSV
    try:
        with open('FA-KES-Dataset.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Get the first article
            first_row = next(reader)
            
            article_title = first_row.get('article_title', '')
            article_content = first_row.get('article_content', '')
            source = first_row.get('source', '')
            date = first_row.get('date', '')
            location = first_row.get('location', '')
            labels = first_row.get('labels', '')
            
            print("\n" + "="*80)
            print("ANALYZING ARTICLE")
            print("="*80)
            print(f"Title: {article_title}")
            print(f"Source: {source}")
            print(f"Date: {date}")
            print(f"Location: {location}")
            print(f"Original Label: {labels}")
            print("\nContent Preview:")
            print(article_content[:300] + "..." if len(article_content) > 300 else article_content)
            
            print("\n" + "-"*80)
            print("RUNNING PERPLEXITY ANALYSIS...")
            print("-"*80)
            
            # Analyze the article content
            content_to_analyze = article_content if article_content else article_title
            analysis = detector.analyze_post(content_to_analyze)
            
            if analysis:
                print("\n" + "="*80)
                print("ANALYSIS RESULTS")
                print("="*80)
                print(f"Bias Score: {analysis.bias}/10")
                print(f"Truthfulness Score: {analysis.truthfulness}/10") 
                print(f"Severity Score: {analysis.severity}/10")
                print(f"\nExplanation:")
                print(analysis.explanation)
                print(f"\nSources:")
                for i, source in enumerate(analysis.sources, 1):
                    print(f"{i}. {source}")
                
                # Compare with original label
                print(f"\n" + "-"*80)
                print("COMPARISON WITH ORIGINAL DATASET")
                print("-"*80)
                print(f"Original Label: {'Fake' if labels == '1' else 'Real'}")
                print(f"Perplexity Truthfulness: {analysis.truthfulness}/10")
                
                if labels == '1':  # Fake news
                    if analysis.truthfulness <= 5:
                        print("✓ Perplexity agrees this is likely false/misleading")
                    else:
                        print("✗ Perplexity disagrees - rates as truthful")
                else:  # Real news
                    if analysis.truthfulness >= 6:
                        print("✓ Perplexity agrees this is likely truthful")
                    else:
                        print("✗ Perplexity disagrees - rates as false/misleading")
                
            else:
                print("❌ Analysis failed!")
                
    except FileNotFoundError:
        print("Error: FA-KES-Dataset.csv not found in current directory")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_single_article() 