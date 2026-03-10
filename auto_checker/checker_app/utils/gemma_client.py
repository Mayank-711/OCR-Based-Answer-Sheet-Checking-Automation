import google.generativeai as genai
from django.conf import settings


class GemmaClient:
    """Wrapper around Google Generative AI SDK for Gemma / Gemini models."""

    def __init__(self, model_name: str = "gemma-3-27b-it"):
        api_key = settings.GEMMA_API_KEY
        if not api_key:
            raise ValueError(
                "GEMMA_API_KEY is not set. Add it to your .env file."
            )
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        """Send a text prompt and return the generated text."""
        response = self._model.generate_content(prompt)
        return response.text

    def generate_with_image(self, prompt: str, image_path: str) -> str:
        """Send a prompt with an image for vision/OCR tasks."""
        import PIL.Image
        img = PIL.Image.open(image_path)
        response = self._model.generate_content([prompt, img])
        return response.text

    def generate_with_pdf_text(self, prompt: str, pdf_text: str) -> str:
        """Send a prompt with extracted PDF text."""
        full_prompt = f"{prompt}\n\n--- Document Text ---\n{pdf_text}"
        return self.generate(full_prompt)
