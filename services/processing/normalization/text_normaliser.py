import re
import os


class TextNormalizer:
    def __init__(self, remove_latex: bool = False):
        self.remove_latex = remove_latex

    def clean(self, text: str) -> str:
        # Encode and decode to normalize any weird characters
        text = text.encode("utf-8", "ignore").decode("utf-8")

        # Remove page headers/footers like "Page X of Y"
        text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

        # Remove arXiv ID mentions
        text = re.sub(r"arXiv:\d+\.\d+", "", text)

        # Fix hyphenation across line breaks (e.g., "computa-\ntional" -> "computational")
        text = re.sub(r"-\s*\n\s*", "", text)

        # Collapse all newline characters into spaces
        text = text.replace("\n", " ")

        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text)

        # Optional: Remove LaTeX math expressions
        if self.remove_latex:
            text = re.sub(r"\$.*?\$", "", text)  # remove inline math $...$

        return text.strip()


# # Example usage:
# if __name__ == "__main__":
#     file_path = "/Users/smarthbakshi/Downloads/out.txt"  # Corrected path too

#     with open(file_path, "r", encoding="utf-8") as f:
#         raw_text = f.read()

#     normalizer = TextNormalizer(remove_latex=True)
#     cleaned_text = normalizer.clean(raw_text)
#     print(cleaned_text)