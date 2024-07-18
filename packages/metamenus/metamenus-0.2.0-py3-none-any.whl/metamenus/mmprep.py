
from sys import path as sysPath

from click import command
from click import option
from click import version_option

from metamenus import __version__
from metamenus.metamenus import _mmPrep

__author__  = "E. A. Tacao <mailto |at| tacao.com.br>"
__date__    = "15 Sep 2020, 19:27 GMT-03:00"

sysPath.append(".")


@command()
@option('-m', '--menu-module', required=True, help='The python module containing the menu "trees"')
@option('-o', '--output-file', required=True, help='The output file generated that can be parsed by the gettext utilities.')
@version_option(version=f'{__version__}', message='%(version)s')
def commandHandler(menu_module: str, output_file: str):
    from sys import path

    path.append('..')

    _mmPrep(filename=menu_module, output_file=output_file)

    #     print("""
    # ---------------------------------------------------------------------------
    # metamenus %s
    #
    # %s
    # %s
    # Distributed under the GNU AFFERO GENERAL PUBLIC LICENSE.
    # ---------------------------------------------------------------------------
    #
    # Usage:
    # ------
    #
    # metamenus.py menu_file output_file
    #
    # - 'menu_file' is the python file containing the menu 'trees';
    # - 'output_file' is the output file generated that can be parsed by the
    #   gettext utilities.
    #
    # Please see metamenus.__doc__ (under the 'More about i18n' section) and
    # metamenus._mmprep.__doc__ for more details.
    # ---------------------------------------------------------------------------
    # """ % (__version__, __author__, __date__))
    #


if __name__ == "__main__":
    commandHandler()
