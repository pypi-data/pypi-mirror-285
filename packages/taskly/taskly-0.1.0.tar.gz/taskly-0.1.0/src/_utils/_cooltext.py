import pyfiglet

from ._rich import console


def cool_text(msg: str):
    """uses pyfiglet to generate text  art

    Args:
        msg (str): Msg to be displayed
    """

    # text = pyfiglet.figlet_format(msg, font='slant') # banner3-D, letters
    text = pyfiglet.figlet_format(msg, font="banner3-D")
    console.print(f"[green]{text}[/green]", justify="center")
