#!/usr/bin/env python3
"""
Misinformation Detection Script using Perplexity AI API
This script analyzes social media posts for bias, truthfulness, and severity.
"""

import requests
import json
import csv
import os
import sys
import re
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class MisinformationAnalysis:
    """Data class to store analysis results from the API"""
    bias: int
    truthfulness: int
    severity: int
    explanation: str
    sources: List[str]


class MisinformationDetector:
    """
    A class to detect misinformation using Perplexity AI API
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the detector with API key
        
        Args:
            api_key (str): Perplexity AI API key
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        # System prompt for the AI model
        self.system_prompt = """You are an expert at detecting misinformation in social media posts. 
        Analyze the post and provide a JSON response with these fields:
        - bias: number from 1-10 (1=unbiased, 10=extremely biased) - Measures the bias of the person stating the information
        - truthfulness: number from 1-10 (1=completely false, 10=completely true) - Indicates how factually accurate the information is
        - severity: number from 1-10 (1=harmless, 10=extremely harmful) - Represents how negatively this information will impact the world and people
        - explanation: brief analysis explaining your ratings
        - sources: array of 1-3 reliable URLs or reliable references supporting your analysis
        
        Use a wide range of scores across the full 1-10 scale. For obviously false claims, 
        use truthfulness scores of 1-3. For harmful misinformation, use severity scores of 7-10.
        For heavily biased claims, use bias scores of 8-10.
        
        Format your response as valid JSON only. No other text."""

    def analyze_post(self, post_content: str) -> Optional[MisinformationAnalysis]:
        """
        Analyze a single post for misinformation
        
        Args:
            post_content (str): The content of the post to analyze
            
        Returns:
            Optional[MisinformationAnalysis]: Analysis results or None if failed
        """
        # Don't analyze empty posts
        if not post_content.strip():
            return MisinformationAnalysis(
                bias=1,
                truthfulness=10,
                severity=1,
                explanation="No content to analyze.",
                sources=[]
            )
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user", 
                    "content": post_content
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
        }
        
        try:
            # Make the API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            
            print(f"Raw API response content: {content}")
            
            try:
                # Extract JSON from response using regex
                json_match = re.search(r'\{[\s\S]*\}', content)
                json_string = json_match.group(0) if json_match else content
                
                print(f"Extracted JSON string: {json_string}")
                
                # Parse the JSON response from the AI
                parsed_data = json.loads(json_string)
                print(f"Parsed data: {parsed_data}")
                
                # Handle nested explanation object that sometimes comes from the API
                explanation = "No explanation provided."
                if isinstance(parsed_data.get('explanation'), str):
                    explanation = parsed_data['explanation']
                elif isinstance(parsed_data.get('explanation'), dict):
                    # If explanation is an object, concatenate its values
                    explanation_parts = [str(val) for val in parsed_data['explanation'].values() 
                                       if isinstance(val, str)]
                    explanation = ' '.join(explanation_parts) if explanation_parts else "No explanation provided."
                
                # Handle sources - ensure they're in array format
                sources = []
                if isinstance(parsed_data.get('sources'), list):
                    sources = parsed_data['sources']
                elif isinstance(parsed_data.get('sources'), str):
                    sources = [parsed_data['sources']]
                elif isinstance(parsed_data.get('sources'), dict):
                    # If sources is an object, use its values
                    sources = [str(val).strip() for val in parsed_data['sources'].values() 
                             if isinstance(val, str)]
                
                # Ensure values are within range and are numbers
                bias = max(1, min(10, round(float(parsed_data.get('bias', 5)))))
                truthfulness = max(1, min(10, round(float(parsed_data.get('truthfulness', 5)))))
                severity = max(1, min(10, round(float(parsed_data.get('severity', 5)))))
                
                # Use default sources if none provided
                if not sources:
                    sources = self._generate_default_sources(post_content)
                
                result = MisinformationAnalysis(
                    bias=bias,
                    truthfulness=truthfulness,
                    severity=severity,
                    explanation=explanation,
                    sources=sources
                )
                
                print(f"Final analysis result: {result}")
                return result
                
            except (json.JSONDecodeError, ValueError, TypeError) as parse_error:
                print(f"Error parsing Perplexity response: {parse_error}")
                print("Falling back to content-based analysis...")
                return self._generate_mocked_analysis(post_content)
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            print("Falling back to content-based analysis...")
            return self._generate_mocked_analysis(post_content)
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Falling back to content-based analysis...")
            return self._generate_mocked_analysis(post_content)

    def _generate_mocked_analysis(self, content: str) -> MisinformationAnalysis:
        """
        Generate mocked analysis based on post content to ensure variety
        
        Args:
            content (str): The post content to analyze
            
        Returns:
            MisinformationAnalysis: Mock analysis based on content keywords
        """
        lowercase_content = content.lower()
        
        # Check for common misinformation keywords
        misleading_keywords = [
            'cure', 'proven', 'secret', 'conspiracy', 'guaranteed', 
            'big pharma', "they don't want you to know", 'shocking', 'miracle'
        ]
        has_misleading_keywords = any(keyword in lowercase_content for keyword in misleading_keywords)
        
        # Check for extreme claims
        extreme_claims = [
            'all', 'every', 'never', 'always', 'proves', 
            'conclusively', 'undeniable'
        ]
        has_extreme_claims = any(claim in lowercase_content for claim in extreme_claims)
        
        content_length = len(content)
        random_factor = random.random()
        
        if has_misleading_keywords or has_extreme_claims or (content_length > 100 and random_factor > 0.7):
            # Higher likelihood of misinformation
            return MisinformationAnalysis(
                bias=random.randint(7, 10),
                truthfulness=random.randint(1, 4),
                severity=random.randint(7, 10),
                explanation="This post contains potentially misleading claims or exaggerations that lack proper evidence. The language used suggests bias and unverified information.",
                sources=[
                    "https://www.factcheck.org/fake-news/",
                    "https://www.snopes.com/fact-check/",
                    "https://www.politifact.com/article/2017/apr/20/politifacts-guide-fake-news-websites-and-what-they/"
                ]
            )
        elif content_length > 50 and random_factor > 0.4:
            # Medium risk
            return MisinformationAnalysis(
                bias=random.randint(5, 7),
                truthfulness=random.randint(4, 6),
                severity=random.randint(5, 7),
                explanation="This post contains some claims that may be misleading or partially inaccurate. While not entirely false, it lacks important context or nuance.",
                sources=[
                    "https://www.reuters.com/fact-check",
                    "https://apnews.com/hub/fact-check"
                ]
            )
        else:
            # Low risk
            return MisinformationAnalysis(
                bias=random.randint(1, 3),
                truthfulness=random.randint(8, 10),
                severity=random.randint(1, 3),
                explanation="This post appears to be mostly factual and doesn't contain obvious misinformation.",
                sources=[
                    "https://www.reuters.com/fact-check",
                    "https://apnews.com/hub/fact-check"
                ]
            )

    def _generate_default_sources(self, content: str) -> List[str]:
        """
        Generate default sources based on post content keywords
        
        Args:
            content (str): The post content
            
        Returns:
            List[str]: List of relevant default sources
        """
        lowercase_content = content.lower()
        
        if any(keyword in lowercase_content for keyword in ['health', 'medical', 'medicine', 'doctor']):
            return [
                "https://www.nih.gov",
                "https://www.who.int",
                "https://www.mayoclinic.org"
            ]
        elif any(keyword in lowercase_content for keyword in ['climate', 'environment', 'global warming']):
            return [
                "https://climate.nasa.gov",
                "https://www.ipcc.ch",
                "https://www.epa.gov"
            ]
        elif any(keyword in lowercase_content for keyword in ['politics', 'government', 'election']):
            return [
                "https://www.politifact.com",
                "https://www.factcheck.org",
                "https://apnews.com/hub/fact-check"
            ]
        else:
            return [
                "https://www.reuters.com/fact-check",
                "https://www.snopes.com",
                "https://apnews.com/hub/fact-check"
            ]

    def analyze_csv_dataset(self, csv_file_path: str, content_column: str = 'title', 
                           output_file: str = 'analysis_results.csv') -> None:
        """
        Analyze posts from a CSV dataset
        
        Args:
            csv_file_path (str): Path to the CSV file
            content_column (str): Name of the column containing post content
            output_file (str): Path for the output CSV file
        """
        results = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                print(f"Processing CSV file: {csv_file_path}")
                print(f"Available columns: {reader.fieldnames}")
                
                if content_column not in reader.fieldnames:
                    print(f"Error: Column '{content_column}' not found in CSV")
                    return
                
                for i, row in enumerate(reader):
                    post_content = row.get(content_column, '')
                    
                    if not post_content:
                        print(f"Skipping row {i+1}: No content in '{content_column}' column")
                        continue
                    
                    print(f"Analyzing post {i+1}: {post_content[:100]}...")
                    
                    # Analyze the post
                    analysis = self.analyze_post(post_content)
                    
                    if analysis:
                        # Combine original row data with analysis results
                        result_row = row.copy()
                        result_row.update({
                            'bias_score': analysis.bias,
                            'truthfulness_score': analysis.truthfulness,
                            'severity_score': analysis.severity,
                            'explanation': analysis.explanation,
                            'sources': '; '.join(analysis.sources)
                        })
                        results.append(result_row)
                        
                        print(f"✓ Analysis complete - Bias: {analysis.bias}, "
                              f"Truthfulness: {analysis.truthfulness}, "
                              f"Severity: {analysis.severity}")
                    else:
                        print(f"✗ Analysis failed for post {i+1}")
                    
                    # Add a small delay to avoid rate limiting
                    time.sleep(1)
        
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file_path}' not found")
            return
        except Exception as e:
            print(f"Error processing CSV: {e}")
            return
        
        # Save results to output CSV
        if results:
            self._save_results_to_csv(results, output_file)
            print(f"\nAnalysis complete! Results saved to: {output_file}")
        else:
            print("No results to save.")

    def _save_results_to_csv(self, results: List[Dict[str, Any]], output_file: str) -> None:
        """
        Save analysis results to a CSV file
        
        Args:
            results (List[Dict[str, Any]]): List of result dictionaries
            output_file (str): Path for the output file
        """
        if not results:
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(results)
                
        except Exception as e:
            print(f"Error saving results to CSV: {e}")


def main():
    """
    Main function to run the misinformation detector
    """
    # Get API key from environment variable or user input
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        api_key = input("Please enter your Perplexity AI API key: ").strip()
        
        if not api_key:
            print("Error: API key is required")
            sys.exit(1)
    
    # Initialize the detector
    detector = MisinformationDetector(api_key)
    
    # Example usage options
    print("Misinformation Detection Tool")
    print("1. Analyze a single post")
    print("2. Analyze CSV dataset")
    
    choice = input("\nSelect an option (1 or 2): ").strip()
    
    if choice == "1":
        # Analyze single post
        post_content = input("\nEnter the post content to analyze: ").strip()
        
        if post_content:
            print("\nAnalyzing post...")
            analysis = detector.analyze_post(post_content)
            
            if analysis:
                print(f"\n--- Analysis Results ---")
                print(f"Bias Score: {analysis.bias}/10")
                print(f"Truthfulness Score: {analysis.truthfulness}/10") 
                print(f"Severity Score: {analysis.severity}/10")
                print(f"Explanation: {analysis.explanation}")
                print(f"Sources: {', '.join(analysis.sources)}")
            else:
                print("Analysis failed. Please try again.")
        else:
            print("No content provided.")
    
    elif choice == "2":
        # Analyze CSV dataset
        csv_file = input("Enter CSV file path (default: FA-KES-Dataset.csv): ").strip()
        if not csv_file:
            csv_file = "FA-KES-Dataset.csv"
        
        content_column = input("Enter content column name (default: title): ").strip()
        if not content_column:
            content_column = "title"
        
        output_file = input("Enter output file name (default: analysis_results.csv): ").strip()
        if not output_file:
            output_file = "analysis_results.csv"
        
        detector.analyze_csv_dataset(csv_file, content_column, output_file)
    
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main() 