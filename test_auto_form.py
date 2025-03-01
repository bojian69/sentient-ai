from unittest import IsolatedAsyncioTestCase
import os, asyncio
from dotenv import load_dotenv
from together import AsyncTogether
import re

load_dotenv()


class TesAutoForm(IsolatedAsyncioTestCase):
    async_client = None

    async def asyncSetUp(self):
        print("setUp: start")
        print('TOGETHER_API_KEY:', os.environ.get("TOGETHER_API_KEY"))
        self.async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
        print("setUp: end")

    async def test_auto_fill_form_data(self):
        try:
            # Step 1: Define the message to send to the AI model
            message = ("I am Liu Ting, my phone number is+61 401 234 567, and my email address is "
                       "liuting@domain.com The form items require last name, first name, email, and "
                       "phone number to extract the required content from the form")

            # Step 2: Send the message to the AI model and get the response
            response = await self.async_client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[{"role": "user", "content": message}],
            )

            # Step 3: Extract the form data from the response‘
            form_data = response.choices[0].message.content
            print("Form Data:", form_data)

        except Exception as e:
            print(e)

    async def asyncTearDown(self):
        # Clean up resources if needed
        print("tearDown: end")

    # To run the test, you would typically use a test runner like this:
    # if __name__ == "__main__":
    #     import unittest
    #     unittest.main()
