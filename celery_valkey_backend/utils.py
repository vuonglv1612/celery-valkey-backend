from urllib.parse import urlparse, urlunparse


def mask_url_password(url: str, mask: str = "***") -> str:
    """
    Masks the password in a ValKey URL.

    Args:
        url (str): The ValKey URL (e.g., 'valkey://username:password@localhost:6379/0')
        mask (str): The string to replace the password with (default: '***')

    Returns:
        str: URL with password masked

    Examples:
        >>> mask_url_password('valkey://user:secret123@localhost:6379/0')
        'valkey://user:***@localhost:6379/0'

        >>> mask_url_password('valkey://admin:pass@127.0.0.1:6379/1', 'xxxxx')
        'valkey://admin:xxxxx@127.0.0.1:6379/1'
    """
    if not url:
        return url

    try:
        # Parse the URL
        parsed = urlparse(url)

        # If there's no authentication info, return original URL
        if "@" not in parsed.netloc:
            return url

        # Split the netloc into authentication and host parts
        auth, host = parsed.netloc.split("@", 1)

        # Split authentication into username and password
        if ":" in auth:
            username, _ = auth.split(":", 1)
            # Reconstruct authentication with masked password
            masked_auth = f"{username}:{mask}"
        else:
            # If no password in URL, return original URL
            return url

        # Reconstruct netloc with masked authentication
        masked_netloc = f"{masked_auth}@{host}"

        # Reconstruct URL components
        masked_components = list(parsed)
        masked_components[1] = masked_netloc  # Replace netloc with masked version

        # Return reconstructed URL
        return urlunparse(masked_components)

    except Exception:
        # If any error occurs during parsing, return original URL
        return url
