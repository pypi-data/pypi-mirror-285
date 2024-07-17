from untis_dif_file_writer.writers import UntisFileNumber


def get_GPU_file_name(untis_file_number: UntisFileNumber):
    return "GPU{}.TXT".format(str(untis_file_number).zfill(3))
