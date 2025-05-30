# Misinformation Detection Tool

A Python script that uses the Perplexity AI API to analyze social media posts for misinformation, bias, and potential harm.

## Features

- **Bias Detection**: Measures the bias level from 1-10 (1=unbiased, 10=extremely biased)
- **Truthfulness Assessment**: Evaluates factual accuracy from 1-10 (1=completely false, 10=completely true)
- **Severity Analysis**: Assesses potential harm from 1-10 (1=harmless, 10=extremely harmful)
- **Source Verification**: Provides reliable sources supporting the analysis
- **Batch Processing**: Can analyze entire CSV datasets
- **Export Results**: Saves analysis results to CSV format

## Requirements

- Python 3.7+
- Perplexity AI API key
- Required Python packages (see requirements.txt)

## Installation

1. **Clone or download the script files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**
   
   Option A - Environment Variable (Recommended):
   ```bash
   export PERPLEXITY_API_KEY="your_api_key_here"
   ```
   
   Option B - Enter when prompted by the script

## Usage

### Method 1: Interactive Mode

Run the main script and follow the prompts:

```bash
python misinformation_detector.py
```

The script will present you with two options:
1. **Analyze a single post** - Enter text manually for immediate analysis
2. **Analyze CSV dataset** - Process an entire CSV file with multiple posts

### Method 2: Programmatic Usage

Use the `MisinformationDetector` class in your own code:

```python
from misinformation_detector import MisinformationDetector

# Initialize with your API key
detector = MisinformationDetector("your_api_key_here")

# Analyze a single post
analysis = detector.analyze_post("Your post content here")

if analysis:
    print(f"Bias: {analysis.bias}/10")
    print(f"Truthfulness: {analysis.truthfulness}/10")
    print(f"Severity: {analysis.severity}/10")
    print(f"Explanation: {analysis.explanation}")
    print(f"Sources: {analysis.sources}")

# Analyze CSV dataset
detector.analyze_csv_dataset("your_dataset.csv", "content_column", "output.csv")
```

### Method 3: Run Example

See the example in action:

```bash
python example_usage.py
```

## CSV Dataset Processing

When processing CSV files, the script:

1. **Reads the CSV file** and identifies available columns
2. **Analyzes each row** using the specified content column
3. **Adds analysis results** as new columns:
   - `bias_score`
   - `truthfulness_score` 
   - `severity_score`
   - `explanation`
   - `sources`
4. **Saves results** to a new CSV file with all original data plus analysis

### CSV Format Expected

Your CSV should have a column containing the text content to analyze. Common column names:
- `title`
- `content` 
- `text`
- `post`
- `message`

Example CSV structure:
```csv
id,title,author,date
1,"Breaking news about...",@user1,2023-01-01
2,"Scientists discover...",@user2,2023-01-02
```

## API Response Format

The script expects the Perplexity AI API to return JSON with these fields:

```json
{
  "bias": 7,
  "truthfulness": 3,
  "severity": 8,
  "explanation": "This post contains misleading information about...",
  "sources": [
    "https://reliable-source1.com/article",
    "https://reliable-source2.com/study"
  ]
}
```

## Error Handling

The script includes comprehensive error handling for:
- **API request failures** (network issues, timeouts)
- **Invalid API responses** (malformed JSON, missing fields)
- **File processing errors** (missing files, encoding issues)
- **Rate limiting** (includes delays between requests)

## Rate Limiting

To avoid hitting API rate limits:
- The script includes a 1-second delay between requests
- For large datasets, consider processing in smaller batches
- Monitor your API usage on the Perplexity AI dashboard

## Configuration

### Model Settings

The script uses these default settings:
- **Model**: `llama-3.1-sonar-small-128k-online`
- **Temperature**: `0.1` (for consistent results)
- **Max Tokens**: `1000`

You can modify these in the `MisinformationDetector` class if needed.

### System Prompt

The AI analysis is guided by a detailed system prompt that instructs it to:
- Use the full 1-10 scale for scoring
- Apply specific criteria for bias, truthfulness, and severity
- Provide reliable sources for verification
- Return responses in valid JSON format

## Example Output

```
=== Analysis Results ===
Bias Score: 8/10
Truthfulness Score: 2/10
Severity Score: 7/10
Explanation: This post contains unsubstantiated medical claims with no scientific backing. The language is highly biased and uses fear tactics typical of health misinformation.
Sources: https://www.who.int/news-room/fact-sheets/detail/cancer, https://www.cancer.org/treatment/treatments-and-side-effects.html
```

## Files Included

- `misinformation_detector.py` - Main script with the MisinformationDetector class
- `example_usage.py` - Example demonstrating programmatic usage
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Troubleshooting

### Common Issues

1. **"API request failed"**
   - Check your API key is correct
   - Verify internet connection
   - Check Perplexity AI service status

2. **"Failed to parse JSON response"**
   - The AI model may have returned non-JSON text
   - Try running the request again
   - Check if the model is available

3. **"Column not found in CSV"**
   - Verify the column name exists in your CSV
   - Check for typos in column name
   - Use the interactive mode to see available columns

4. **Rate limiting errors**
   - Increase the delay between requests
   - Process smaller batches
   - Check your API plan limits

## Security Notes

- **Never commit API keys** to version control
- **Use environment variables** for API keys in production
- **Be mindful of API usage costs** when processing large datasets
- **Validate and sanitize input** when processing untrusted data

## Contributing

Feel free to enhance the script with:
- Additional error handling
- More sophisticated analysis metrics
- Support for other AI models
- Performance optimizations
- Better CSV handling

## License

This script is provided as-is for educational and research purposes. 