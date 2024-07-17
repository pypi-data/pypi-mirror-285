import logging
import os
import subprocess
from enum import Enum
from typing import Union

from start_end_logging.start_end_logging import log_start, log_end

log = logging.getLogger(__name__)


class UntisFileNumber(Enum):
    """
    Enum for Untis file numbers.
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    """
    STUNDENPLAN = 1
    UNTERRICHT = 2
    KLASSEN = 3
    LEHRER = 4
    RAEUME = 5
    FAECHER = 6
    ABTEILUNGEN = 7
    LEHRBEFAEHIGUNG = 8
    PAUSENAUFSICHT = 9
    STUDENTEN = 10
    STUNDENTAFEL = 11
    ABSENZGRUENDE = 12
    ABSENZEN = 13
    VERTRETUNGEN = 14
    KURSWAHL = 15
    ZEITWUENSCHE = 16
    KLAUSUREN = 17
    FERIEN = 18
    UNTERRICHTSFOLGE = 19
    ANRECHNUNGEN = 20
    ANRECHNUNGSGRUENDE = 21


def write_dif_file(file_number: Union[UntisFileNumber, int, str], path_untis_exe: str, path_untis_file: str,
                   path_output_folder: str = "", output_file_name: str = None) -> None:
    """
    Writes a dif-file from Untis.

    Args:
        file_number (UntisFileNumber | int): Number of dif-file to write.
        path_untis_exe (str): Path to untis.exe.
        path_untis_file (str): Path to untis-file.
        path_output_folder (str): Path to output folder. Defaults to "".
        output_file_name (str): Name of output file. If not specified the Untis default GPUXXX.TXT is used.
    """
    log_start('writing dif file {}'.format(file_number), log)
    if path_untis_exe is None or path_untis_exe == '':
        raise ValueError('Untis.exe not specified.')
    if path_untis_file is None or path_untis_file == '':
        raise ValueError('Untis file not specified.')
    if isinstance(file_number, int):
        if file_number < 1 or file_number > 21:
            raise ValueError('Invalid file number.')
        value = file_number
    elif isinstance(file_number, UntisFileNumber):
        value = file_number.value
    else:
        raise ValueError('Invalid file number.')

    file_name = "GPU{}.TXT".format(str(value).zfill(3)) if output_file_name is None else output_file_name
    path_output_file = os.path.join(path_output_folder, file_name)

    cmd_str = r'"{}" "{}" /{}="{}"'.format(path_untis_exe,
                                           path_untis_file,
                                           "exp{}".format(value),
                                           path_output_file)
    log.info(cmd_str)
    subprocess.call(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    log_end()


def write_xml_file(path_untis_exe: str, path_untis_file: str, path_output_folder: str = "",
                   output_file_name: str = "xml_export.xml") -> None:
    """
    Writes the xml-file from Untis.

    Args:
        path_untis_exe (str): Path to untis.exe.
        path_untis_file (str): Path to untis-file.
        path_output_folder (str): Path to output folder. Defaults to "".
        output_file_name (str): Name of output file. Defaults to xml_export.xml.
    """
    log_start('writing xml file', log)
    if path_untis_exe is None or path_untis_exe == '':
        raise ValueError('Untis.exe not specified.')
    if path_untis_file is None or path_untis_file == '':
        raise ValueError('Untis file not specified.')

    path_output_file = os.path.join(path_output_folder, output_file_name)

    cmd_str = r'"{}" "{}" /{}="{}"'.format(path_untis_exe,
                                           path_untis_file,
                                           "xml",
                                           path_output_file)
    log.info(cmd_str)
    subprocess.call(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    log_end()


def write_all_dif_files(path_untis_exe: str, path_untis_file: str, path_output_folder: str = ""):
    """
    Writes a dif-file from Untis

    Args:
        path_untis_exe (str): Path to untis.exe.
        path_untis_file (str): Path to untis-file.
        path_output_folder (str): Path to output folder. Defaults to "".
    """
    log_start('writing all dif files', log)
    cmd_str = r'"{}" "{}" /exp*="{}"'.format(path_untis_exe, path_untis_file, path_output_folder)
    log.info(cmd_str)
    subprocess.call(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    log_end()
