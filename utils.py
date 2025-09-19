from shortzy import Shortzy
from info import SHORTLINK_URL, SHORTLINK_API

class temp:
    """
    Temporary storage for bot names and user info.
    """
    ME = None       # Your bot's username
    BOT = None      # Bot display name
    U_NAME = None   # Admin/owner name
    B_NAME = None   # Brand name / bot name

async def get_shortlink(link: str) -> str:
    """
    Convert a long URL to a short URL using Shortzy API.
    
    Args:
        link (str): Original long URL

    Returns:
        str: Shortened URL
    """
    try:
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        short_link = await shortzy.convert(link)
        return short_link
    except Exception as e:
        # If shortlink fails, return original URL
        print(f"[Shortlink Error] {e}")
        return link
