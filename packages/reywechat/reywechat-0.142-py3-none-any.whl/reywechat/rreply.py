# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-10 16:24:10
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Reply methods.
"""


from typing import Any, List, Dict, Literal, Callable

from .rreceive import RMessage
from .rsend import SendParam
from .rwechat import RWeChat


__all__ = (
    "RReplyStop",
    "RReply"
)


class RReplyStop(AssertionError):
    """
    Rey's `reply stop` type.
    """


class RReply(object):
    """
    Rey's `reply` type.
    """


    def __init__(
        self,
        rwechat: RWeChat
    ) -> None:
        """
        Build `reply` instance.

        Parameters
        ----------
        rwechat : `RWeChat` instance.
        """

        # Set attribute.
        self.rwechat = rwechat
        self.rules: List[Dict[Literal["judge", "level"], Any]] = []

        # Add handler.
        self._reply_by_rule()


    def _reply_by_rule(self) -> None:
        """
        Add handler, reply message by rules.
        """


        # Define.
        def handler_reply_by_rule(message: RMessage) -> None:
            """
            Reply message by rules.

            Parameters
            ----------
            message : `RMessage` instance.
            """

            # Loop.
            for rule in self.rules:
                judge: Callable[[RMessage], SendParam] = rule["judge"]

                # Judge.
                try:
                    result = judge(message)

                # Stop.
                except RReplyStop:
                    break

                # Fail.
                if result is None:
                    continue

                # Send.
                if result.__class__ == dict:
                    result = [result]
                for params in result:
                    self.rwechat.rsend.send(**params)

                break


        # Add handler.
        self.rwechat.rreceive.add_handler(handler_reply_by_rule)


    def add_rule(
        self,
        judge: Callable[[RMessage], SendParam],
        level: float = 0
    ) -> None:
        """
        Add reply rule.

        Parameters
        ----------
        judge : Function of judgment and generate send message parameters. The parameter is the `RMessage` instance.
        When throw `RReplyStop` type exception, then stop executes.
            - `Return None` : Judgment failed, continue next rule.
            - `Return Dict` : Send a message and breaking judgment.
            - `Return List[Dict]` : Send multiple messages and breaking judgment.

        level : Priority level, sort from large to small.
        """

        # Get parameter.
        rule = {
            "judge": judge,
            "level": level
        }

        # Add.
        self.rules.append(rule)

        # Sort.
        fund_sort = lambda rule: rule["level"]
        self.rules.sort(
            key=fund_sort,
            reverse=True
        )