from robotlibcore import keyword


class Text:
    @keyword
    def set_text(self, locator: str, text: str) -> None:
        locator.set_text(text)
