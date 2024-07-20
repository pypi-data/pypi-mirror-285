import re


class TextUtils:
    def __remove_multiple_space(self, text: str) -> str:
        """Removes the multiple space from the text

        Args:
            text (str): Document to remove

        Returns:
            str: Multiple space removed text
        """
        cleaned_text = re.sub(r"\s+", " ", text).strip()
        return cleaned_text

    def __remove_unicode(self, text: str) -> str:
        """Remove the ASCII codes from the text

        Args:
            text (str): Document to remove

        Returns:
            str: ASCII removed text
        """
        return text.encode("ascii", errors="ignore").decode("ascii")

    def text_preprocess(self, text) -> str:
        space_removal = self.__remove_multiple_space(text)
        ascii_removal = self.__remove_unicode(space_removal)
        return ascii_removal
