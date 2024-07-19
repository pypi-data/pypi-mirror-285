"""
@author: jldupont
"""
import base64


class Codec:
    """
    Utility class for encoding / decoding strings
    with base64 algorithm and custom alphabet
    compatible with Google GCP labeling capability
    """

    ALTCHARS = b"-_"

    @staticmethod
    def encode(input: str) -> str:
        assert isinstance(input, str)
        result = base64.b64encode(input.encode("utf-8"),
                                  altchars=Codec.ALTCHARS).decode()
        return result.replace("=", "")

    @staticmethod
    def decode(input: str) -> str:
        assert isinstance(input, str)

        # pad input with "=" as base64 decode expects
        # i.e. adjustment based of the encode operation
        pad_count = len(input) % 4
        padded_input = input + "=" * pad_count

        try:
            b64decoded = base64.b64decode(padded_input,
                                          altchars=Codec.ALTCHARS)
            bindecoded = b64decoded.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Error decoding. "
                             "What is encoded using the right encoder?")

        return bindecoded
