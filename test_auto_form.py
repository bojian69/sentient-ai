from unittest import IsolatedAsyncioTestCase
import os, asyncio
from together import AsyncTogether
from sentient import sentient
from dotenv import load_dotenv
import re
import datetime

load_dotenv()


class TesAutoForm(IsolatedAsyncioTestCase):
    async_client = None
    web_url = 'https://enpc1.uhomes.com/hackson'

    async def asyncSetUp(self):
        print("setUp: start")
        print('TOGETHER_API_KEY:', os.environ.get("TOGETHER_API_KEY"))
        self.async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
        print("setUp: end")

    # 提取会话文案-预检模版缺失项
    async def test_check_fill_data(self):
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
            await self.result_to_file(response, 'test_check_fill_data_response')

            # Step 3: Extract the form data from the response‘
            form_data = response.choices[0].message.content
            await self.result_to_file(form_data, 'test_check_fill_data')

        except Exception as e:
            print(e)

    # 提供URL地址和goal内容提取表单字段
    async def test_auto_form_field(self):
        try:
            message = (f'open the {self.web_url}, retrieve the fields name for this page form, screenshot this '
                       f'page image base64 format.')

            response = await sentient.invoke(
                goal=message,
                provider="together",
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")

            await self.result_to_file(response, 'test_auto_form_field_response')

        except Exception as e:
            print(e)

    # 提供URL地址和goal自动填充表单字段
    async def test_auto_fill_form_field(self):
        try:
            message = (f'open the {self.web_url}, retrieve the fields name for this page form, screenshot this '
                       f'page image base64 format.')

            response = await sentient.invoke(
                goal=message,
                provider="together",
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")

            await self.result_to_file(response, 'test_auto_fill_form_field_response')

        except Exception as e:
            print(e)

    # 测试执行结果填入执行文件
    async def test_result_to_file(self):
        try:
            result = 'Hello, world!'
            await self.result_to_file(result, 'test')
        except Exception as e:
            print(e)

    # 将结果生成文件
    async def result_to_file(self, result, file_name='test'):
        try:
            current_time = datetime.datetime.now()
            time_str = current_time.strftime("%Y%m%d%H%M%S")[2:]
            directory = 'result_file'
            path = f'{directory}/{file_name}_{time_str}.log'
            # Create the directory if it does not exist
            os.makedirs(directory, exist_ok=True)
            # Convert result to string if it is not already
            result_str = str(result)
            with open(path, 'w') as f:
                f.write(result_str)

        except Exception as e:
            print(e)

    async def asyncTearDown(self):
        # Clean up resources if needed
        print("tearDown: end")

    # To run the test, you would typically use a test runner like this:
    # if __name__ == "__main__":
    #     import unittest
    #     unittest.main()
