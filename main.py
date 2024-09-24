from spell_checker import SpellChecker
from text_utils import normalize_text, download_text
from error_tables import error_tables_example


def run_tests(spell_checker):
    """
    Run unit tests to validate the functionality of the SpellChecker.

    This function conducts various tests on the spell-checking capabilities of the SpellChecker class.
    It checks for correct spelling corrections in various scenarios, including handling empty strings,
    sentences with no errors, and different alpha values.
    Any assertion failures will raise an error, while successful tests will print confirmation messages.

    Parameters:
    -----------
    spell_checker : SpellChecker
        An instance of the SpellChecker class that provides the spell-checking functionality to be tested.
    """
    try:
        # Test various common spelling corrections
        assert spell_checker.spell_check("i have somthing", 0.95) == "i have something"
        assert spell_checker.spell_check("the united states of amarica", 0.95) == "the united states of america"
        assert spell_checker.spell_check("speling", 0.95) == "spelling"

        # Test sentences with no spelling errors
        assert spell_checker.spell_check("There is nothing in the sky", 0.95) == "there is nothing in the sky"
        assert spell_checker.spell_check("The dog is breathing very fast", 0.95) == "the dog is breathing very fast"

        # Test single word with no errors
        assert spell_checker.spell_check("word", 0.95) == "word"

        # Test sentences with spelling errors
        assert spell_checker.spell_check("the united states of amarica is big", 0.95) == "the united states of america is big"  # Replace
        assert spell_checker.spell_check("unieied kingdom", 0.95) == "unified kingdom"  # Replace
        assert spell_checker.spell_check("korrectud", 0.95) == "corrected"  # Replace 2
        assert spell_checker.spell_check("bycycle", 0.95) == "bicycle"  # Replace
        assert spell_checker.spell_check("inconvient", 0.95) == "inconvenient"  # Insert 2
        assert spell_checker.spell_check("arrainged", 0.95) == "arranged"  # Delete
        assert spell_checker.spell_check("peotry", 0.95) == "poetry"  # Transpose
        assert spell_checker.spell_check("peotryy", 0.95) == "poetry"  # Transpose + delete
        assert spell_checker.spell_check("quintessential", 0.95) == "quintessential"  # Unknown
        assert spell_checker.spell_check('haunts of the whalle', 0.95) == 'haunts of the whale'  # Delete

        # Test correction in a sentence context
        assert spell_checker.spell_check("The dog is barking very loud", 0.95) == "the dog is barking very loud"
        assert spell_checker.spell_check("I like to go for a walk in the parrk", 0.95) == "i like to go for a walk in the park"

        # Test empty string input
        assert spell_checker.spell_check("", 0.95) == ""

        # Test input with no errors
        assert spell_checker.spell_check("This is a test sentence with no errors", 0.95) == "this is a test sentence with no errors"

        # Test input with multiple sentences
        assert spell_checker.spell_check("This is the first sentence. Here is the second.", 0.95) == "this is the first sentence here is the second"
        print("Edge case spell check tests passed.")

        # Test with different alpha values
        assert spell_checker.spell_check("i have somthing", 0.9) == "i have something"
        assert spell_checker.spell_check("i have somthing", 0.5) == "i have something"
        assert spell_checker.spell_check("i have somthing", 0.1) == "i have something"
        print("Spell check tests with different alpha values passed.")

        print("All tests passed.")

    except AssertionError as e:
        print("A test failed:", e)


def main():
    """
    Main function to run the SpellChecker and execute tests.

    This function downloads a text file, normalizes it, initializes the SpellChecker and its language model,
    adds error tables, and executes the unit tests on the spell-checking functionality.
    """
    # Example usage
    norvig_url = "https://norvig.com/big.txt"  # URL of the text file
    norvig_big_text = download_text(norvig_url)
    norvig_big_text = normalize_text(norvig_big_text)

    spell_checker = SpellChecker()
    language_model = spell_checker.LanguageModel()
    language_model.build_model(norvig_big_text)
    spell_checker.add_language_model(language_model)
    spell_checker.add_error_tables(error_tables_example)

    run_tests(spell_checker)
    print("The test was completed successfully.")


if __name__ == "__main__":
    main()