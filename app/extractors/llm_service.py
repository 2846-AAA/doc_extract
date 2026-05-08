import json
from groq import Groq
from loguru import logger
from app.core.config import settings
from app.core.exceptions import LLMError
from app.extractors.templates import DocumentTemplate


class LLMService:

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"

    def extract_fields(self, raw_text: str, template: DocumentTemplate) -> dict:
        fields_list = ", ".join(template.fields)

        system_prompt = (
            "You are a document data extraction assistant. "
            "Extract information from the given document text and return ONLY a valid JSON object. "
            "Do not include any explanation or markdown. "
            "If a field cannot be found, set its value to null. "
            "Keep values exactly as they appear in the document."
        )

        user_prompt = f"""Document type: {template.display_name}
Context: {template.prompt_hint}

Fields to extract: {fields_list}

Document text:
{raw_text}

Return a JSON object with these exact keys: {fields_list}"""

        try:
            logger.debug(f"Calling Groq LLM for {template.doc_type} extraction")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            extracted = json.loads(content)
            logger.info(f"LLM extraction successful, got {len(extracted)} fields")
            return extracted

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            raise LLMError(f"LLM response was not valid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise LLMError(f"Groq API call failed: {str(e)}")