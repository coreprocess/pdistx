import sys


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            # TODO(Nghia Lam): Something wrong with new line characters '\n',
            # it cannot write a new line ...
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)
