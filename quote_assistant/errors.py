"""Exceptions shared by the model adapters.

Each adapter (model.py, langchain_model.py) catches its own library's error and
re-raises one of these, so callers never depend on which library made the call.
"""


class ExtractionError(Exception):
    """The model's reply could not be turned into valid quotes.

    The original library error (e.g. pydantic.ValidationError or LangChain's
    OutputParserException) is kept as ``__cause__`` via ``raise ... from err``.
    """
