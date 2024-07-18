author_info = (
    ("Mehdi Kamani", "mkamani@sheypoor.com"),)

package_info = """
Asyncio compatible wraper around the aio-pika library for consumining messages.
"""
package_license = "MIT License"

team_email = ""

version_info = (0, 0, 1)

__author__ = ", ".join("{} <{}>".format(*info) for info in author_info)
__version__ = ".".join(map(str, version_info))
