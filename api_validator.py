"""
API Connectivity Validator
Validates that API keys are working correctly
"""
import asyncio
import aiohttp
from typing import Dict, Tuple

class APIValidator:
    """Validates API connectivity and credentials"""

    @staticmethod
    async def validate_suno_api(api_key: str, base_url: str = "https://api.sunoapi.org") -> Tuple[bool, str]:
        """
        Validate Suno API connectivity
        Returns: (is_valid, message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Use the same headers as the actual client
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # Try a simple test request - we'll use the record-info endpoint with a dummy ID
                # This will fail gracefully but confirm API key is valid
                async with session.get(
                    f"{base_url}/api/v1/generate/record-info",
                    params={"taskId": "test"},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    # If we get 200, the API key is valid (even if task doesn't exist)
                    # If we get 400/404, the API key is still valid (just bad task ID)
                    # If we get 401/403, the API key is invalid
                    if response.status in [200, 400, 404]:
                        data = await response.json()
                        # Check if response has expected structure
                        if data and "code" in data:
                            return True, "✅ Suno API conectada correctamente"
                        else:
                            return True, "✅ Suno API conectada (respuesta atípica)"
                    elif response.status == 401:
                        return False, "❌ API Key de Suno inválida"
                    elif response.status == 403:
                        return False, "❌ Acceso denegado - Verifica tu API Key"
                    else:
                        return False, f"❌ Error {response.status} al conectar con Suno"

        except asyncio.TimeoutError:
            return False, "⏱️ Timeout al conectar con Suno API"
        except aiohttp.ClientError as e:
            return False, f"❌ Error de conexión con Suno: {str(e)}"
        except Exception as e:
            return False, f"❌ Error validando Suno API: {str(e)}"

    @staticmethod
    async def validate_replicate_api(api_token: str) -> Tuple[bool, str]:
        """
        Validate Replicate API connectivity
        Returns: (is_valid, message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Token {api_token}",
                    "Content-Type": "application/json"
                }

                # Try to get account info
                async with session.get(
                    "https://api.replicate.com/v1/account",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        username = data.get("username", "Unknown")
                        return True, f"✅ Replicate API conectada (Usuario: {username})"
                    elif response.status == 401:
                        return False, "❌ Token de Replicate inválido"
                    elif response.status == 403:
                        return False, "❌ Acceso denegado - Verifica tu token"
                    else:
                        return False, f"❌ Error {response.status} al conectar con Replicate"

        except asyncio.TimeoutError:
            return False, "⏱️ Timeout al conectar con Replicate API"
        except aiohttp.ClientError as e:
            return False, f"❌ Error de conexión con Replicate: {str(e)}"
        except Exception as e:
            return False, f"❌ Error validando Replicate API: {str(e)}"

    @staticmethod
    async def validate_openai_api(api_key: str, assistant_id: str = None) -> Tuple[bool, str]:
        """
        Validate OpenAI API connectivity
        Returns: (is_valid, message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # Try to list models
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        # If assistant_id provided, validate it
                        if assistant_id:
                            return await APIValidator._validate_openai_assistant(
                                session, headers, assistant_id
                            )
                        return True, "✅ OpenAI API conectada correctamente"
                    elif response.status == 401:
                        return False, "❌ API Key de OpenAI inválida"
                    elif response.status == 403:
                        return False, "❌ Acceso denegado - Verifica tu API Key"
                    else:
                        return False, f"❌ Error {response.status} al conectar con OpenAI"

        except asyncio.TimeoutError:
            return False, "⏱️ Timeout al conectar con OpenAI API"
        except aiohttp.ClientError as e:
            return False, f"❌ Error de conexión con OpenAI: {str(e)}"
        except Exception as e:
            return False, f"❌ Error validando OpenAI API: {str(e)}"

    @staticmethod
    async def _validate_openai_assistant(session, headers, assistant_id: str) -> Tuple[bool, str]:
        """Validate OpenAI Assistant exists using the SDK"""
        try:
            # Import OpenAI client here
            import asyncio
            from openai import OpenAI

            # Get API key from headers
            auth_header = headers.get("Authorization", "")
            api_key = auth_header.replace("Bearer ", "")

            # Create OpenAI client
            client = OpenAI(api_key=api_key)

            # Retrieve assistant using SDK (same method as working diagnostic script)
            assistant = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.beta.assistants.retrieve(assistant_id)
            )

            if assistant:
                return True, f"✅ OpenAI API conectada (Assistant: {assistant.name})"
            else:
                return True, "✅ OpenAI API conectada (Assistant no validado)"

        except Exception as e:
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
                # Assistant not found, but API key is valid
                return True, f"✅ OpenAI API conectada (Assistant ID: {assistant_id[:20]}... - no encontrado)"
            elif "401" in error_str or "unauthorized" in error_str:
                return False, "❌ API Key sin permisos para Assistants"
            else:
                # API key is valid, just couldn't validate assistant
                return True, f"✅ OpenAI API conectada (Assistant no validado - {str(e)[:50]})"

    @staticmethod
    async def validate_all_apis(
        suno_key: str = None,
        suno_url: str = "https://api.sunoapi.org",
        replicate_token: str = None,
        openai_key: str = None,
        openai_assistant: str = None
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Validate all APIs at once
        Returns dict with results for each API
        """
        results = {}

        tasks = []
        if suno_key:
            tasks.append(("suno", APIValidator.validate_suno_api(suno_key, suno_url)))
        if replicate_token:
            tasks.append(("replicate", APIValidator.validate_replicate_api(replicate_token)))
        if openai_key:
            tasks.append(("openai", APIValidator.validate_openai_api(openai_key, openai_assistant)))

        if not tasks:
            return results

        # Run all validations concurrently
        for api_name, task in tasks:
            try:
                is_valid, message = await task
                results[api_name] = (is_valid, message)
            except Exception as e:
                results[api_name] = (False, f"❌ Error: {str(e)}")

        return results

    @staticmethod
    async def quick_validate(api_name: str, **kwargs) -> Tuple[bool, str]:
        """
        Quick validation for a single API

        Args:
            api_name: 'suno', 'replicate', or 'openai'
            **kwargs: API-specific parameters
        """
        if api_name == "suno":
            return await APIValidator.validate_suno_api(
                kwargs.get('api_key'),
                kwargs.get('base_url', 'https://api.sunoapi.org')
            )
        elif api_name == "replicate":
            return await APIValidator.validate_replicate_api(kwargs.get('api_token'))
        elif api_name == "openai":
            return await APIValidator.validate_openai_api(
                kwargs.get('api_key'),
                kwargs.get('assistant_id')
            )
        else:
            return False, f"❌ API desconocida: {api_name}"
