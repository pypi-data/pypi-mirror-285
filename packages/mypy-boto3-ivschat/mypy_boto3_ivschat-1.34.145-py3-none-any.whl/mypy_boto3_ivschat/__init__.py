"""
Main interface for ivschat service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_ivschat import (
        Client,
        IvschatClient,
    )

    session = Session()
    client: IvschatClient = session.client("ivschat")
    ```
"""

from .client import IvschatClient

Client = IvschatClient

__all__ = ("Client", "IvschatClient")
