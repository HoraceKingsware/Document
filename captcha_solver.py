"""
验证码识别模块
支持使用Claude或OpenAI识别验证码
"""
import base64
import os
from io import BytesIO
from PIL import Image
import anthropic
import openai
from config import Config


class CaptchaSolver:
    """验证码识别器"""

    def __init__(self):
        self.model = Config.AI_MODEL

        if self.model == 'claude':
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        elif self.model == 'openai':
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            raise ValueError(f"不支持的模型: {self.model}")

    def solve_captcha_from_file(self, image_path: str) -> str:
        """
        从文件识别验证码

        Args:
            image_path: 验证码图片路径

        Returns:
            识别出的验证码文本
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()

        return self._solve_captcha(image_data)

    def solve_captcha_from_element(self, screenshot_bytes: bytes) -> str:
        """
        从截图bytes识别验证码

        Args:
            screenshot_bytes: 截图的字节数据

        Returns:
            识别出的验证码文本
        """
        return self._solve_captcha(screenshot_bytes)

    def _solve_captcha(self, image_data: bytes) -> str:
        """
        使用AI模型识别验证码

        Args:
            image_data: 图片的字节数据

        Returns:
            识别出的验证码文本
        """
        # 转换为base64
        base64_image = base64.b64encode(image_data).decode('utf-8')

        if self.model == 'claude':
            return self._solve_with_claude(base64_image)
        elif self.model == 'openai':
            return self._solve_with_openai(base64_image)

    def _solve_with_claude(self, base64_image: str) -> str:
        """使用Claude识别验证码"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": "这是一个验证码图片。请识别图片中的验证码文字或数字，只返回验证码内容，不要有任何其他解释。如果是数字+字母组合，请保持大小写。"
                            }
                        ],
                    }
                ],
            )

            captcha_text = message.content[0].text.strip()
            print(f"Claude识别结果: {captcha_text}")
            return captcha_text

        except Exception as e:
            print(f"Claude识别验证码失败: {str(e)}")
            raise

    def _solve_with_openai(self, base64_image: str) -> str:
        """使用OpenAI识别验证码"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "这是一个验证码图片。请识别图片中的验证码文字或数字，只返回验证码内容，不要有任何其他解释。如果是数字+字母组合，请保持大小写。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=300,
            )

            captcha_text = response.choices[0].message.content.strip()
            print(f"OpenAI识别结果: {captcha_text}")
            return captcha_text

        except Exception as e:
            print(f"OpenAI识别验证码失败: {str(e)}")
            raise


if __name__ == "__main__":
    # 测试代码
    solver = CaptchaSolver()
    # result = solver.solve_captcha_from_file("captcha.png")
    # print(f"识别结果: {result}")
