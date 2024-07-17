"""
This module provides a command line interface for sending SMS messages via SmsAero asynchronously.
"""

import argparse
import asyncio
import pprint
import sys

from smsaero import SmsAero, SmsAeroException


async def main_async() -> None:
    """
    Parses command line arguments and sends an SMS message via SmsAero asynchronously.

    The command line arguments are:
    --email: The email registered with SmsAero.
    --api_key: The API key from SmsAero.
    --phone: The phone number to send the SMS message to.
    --message: The text of the message to be sent.

    If the SMS message is sent successfully, the response data from SmsAero is printed.
    If an error occurs, the error message is printed and the program exits with status code 1.
    """
    parser = argparse.ArgumentParser(description="Send SMS via smsaero.ru gate")
    parser.add_argument("--email", type=str, required=True, help="Your email registered with SmsAero")
    parser.add_argument("--api_key", type=str, required=True, help="Your SmsAero API key")
    parser.add_argument("--phone", type=int, required=True, help="Phone number to send SMS to")
    parser.add_argument("--message", type=str, required=True, help="Message to send")

    args = parser.parse_args()

    api = SmsAero(args.email, args.api_key)
    try:
        result = await api.send_sms(args.phone, args.message)
        pprint.pprint(result)
    except SmsAeroException as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        await api.close_session()


def main() -> None:
    """
    Runs the main function asynchronously.
    """
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
