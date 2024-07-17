# untis-dif-file-writer

A simple Python package to write dif-files from Untis.

See https://platform.untis.at/HTML/WebHelp/de/untis/index.html -> search for "export dif" -> Export/Import DIF-Dateien.

## Installation

```pip install untis-dif-file-writer``` or ```poetry add untis-dif-file-writer```

## Usage

```
from untis_dif_file_writer.writers import write_dif_file, write_xml_file, write_all_dif_files, UntisFileNumber

# Write the students dif-file:
write_dif_file(UntisFileNumber.STUDENTEN, 
               "path/to/Untis.exe",
               "path/to/Untis-file",
               path_output_folder="path/to/output/folder"),
               output_file_name="students.TXT")

# Write the xml-file:
write_xml_file("path/to/Untis.exe", "path/to/Untis-file")
               
# Write all dif-files:
write_all_dif_files("path/to/Untis.exe", "path/to/Untis-file")
```

Index of columns in dif-files:

```
from untis_dif_file_writer.dif_files_columns import UntisFileKlassen

print(UntisFileKlassen.MIN_STUNDEN_PRO_TAG.value) 
```