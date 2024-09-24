import re
import requests


def normalize_text(text):
    """
    Return a normalized version of the specified string.
    This function cleans and normalizes the input text by removing punctuation, special characters, and converting it to lowercase.
    The normalization process ensures that the text consists only of letters, numbers and spaces.

    Parameters:
    -----------
    text : str
        The text to normalize.

    Returns:
    --------
    str
        The normalized text.
    """
    # Create a translation table to replace chars and apply it to the text
    translation_table = {'â\x80\x9c': '"', 'â\x80\x9d': '"', 'â\x80\x99': "'", '“': '"', '”': '"', '‘': "'", '’': "'"}
    for original_char, fixed_char in translation_table.items():
        text = text.replace(original_char, fixed_char)

    text = text.lower()  # Convert to lowercase
    text = text.replace('-', ' ')  # Convert hyphens to spaces
    text = text.replace('—', ' ')  # Convert em dashes to spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove all non-word characters except underscores
    text = text.replace('_', '')  # Remove underscores
    punctuation = re.compile(r"([!?.,;`'’\"“—\-+@|<>^~*#=$•™éâêàœ])")  # Define a regex pattern to match specific punctuation
    text = punctuation.sub('', text)  # Remove the punctuation
    bad_word = '\ufeff'
    text = re.sub(bad_word, '', text)
    text = re.sub(r'\s+', ' ', text)  # Replace sequences of whitespace characters with a single space
    return text


def download_text(url):
    """
    Download the text from a specified URL.

    Parameters:
    -----------
    url : str
        The URL from which to download the text.

    Returns:
    --------
    str or None
        The text content downloaded from the URL, or None if an error occurred during the download process.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None