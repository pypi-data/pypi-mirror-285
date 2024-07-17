from os import walk, path


class Searcher():


    def __init__(self, path, keywords):
        self.path = path
        self.keywords = [keywords]
        
        self.extensions = {
            'valid': ['pdf', 'txt', 'csv', 'bat', 'ps1', 'cmd', 'py', 'sh', 'doc', 'xls', 'xlsx', 'zip', 'xml', 'docx', 'doc', 'xls', 'xlsx', 'html', 'json'],
            'bin_files': ['pdf', 'doc', 'docx', 'xls', 'xlsx']
        }
        
        self.valid_files = []
        self.sensitive_files = []

        self.walk_dir(self.path)
        self.read_files()
        self.return_sensitive_files()


    def walk_dir(self, path):
        for root, subdirs, files in walk(path):
            if len(files) > 0:
                for file in files:
                    file_path = root + '/' + file
                    file_ext = file.split('.')[-1]
                    if file_ext in self.extensions["valid"]:
                        if file_ext == 'zip':
                            self.walk_zip(file_path)
                        else:
                            self.valid_files.append((file_path,file_ext))
        
        return self.valid_files


    def read_files(self):
        for file in self.valid_files:
            contador_titulo = 0
            if file[1] not in self.extensions["bin_files"]:
                if file[1] == 'csv':
                    with open(file[0], 'r') as f:
                        text = f.read()
                        if any([k in text.lower() for k in self.keywords]):
                            print('='*50)
                            print(f'[*] {file[0]}')
                            print('='*50)
                            print(text)
                            self.sensitive_files.append(file)
                else:
                    with open(file[0], 'r') as f:
                        n_line = 0
                        for line in f.readlines():
                            n_line += 1
                            if any([k in line.lower() for k in self.keywords]):
                                if contador_titulo == 0:
                                    print('='*50)
                                    print(f'[*] {file[0]}')
                                    print('='*50)
                                    contador_titulo += 1
                                    self.sensitive_files.append(file)
                                print(f'{n_line} {line}')
                        print('')
                        
            elif file[1] == 'pdf':
                self.read_pdf(file)
                
            elif file[1] == 'docx' or file[1] == 'doc' or file[1] == 'xls' or file[1] == 'xlsx':
                self.read_ms_file(file)


    def read_pdf(self, file):
        from PyPDF2 import PdfReader
        pdf = PdfReader(file[0])
        contador_titulo = 0
        for page in range(len(pdf.pages)):
            page = pdf.pages[page].extract_text()
            for text in page.split('\n'):
                if any([k in text.lower() for k in self.keywords]):

                    if contador_titulo == 0:
                        print('='*50)
                        print(f'[*] {file[0]}')
                        print('='*50)
                        contador_titulo += 1
                        self.sensitive_files.append(file)

                    print(f'{text}\n')


    def read_ms_file(self, file):
        import textract
        
        text = textract.process(file[0]).decode()
        contador_titulo = 0
        for line in text.split('\n'):
            if any([k in line.lower() for k in self.keywords]):

                if contador_titulo == 0:
                    print('='*50)
                    print(f'[*] {file[0]}')
                    print('='*50)
                    contador_titulo += 1
                    self.sensitive_files.append(file)
                    if file[1] == 'xls' or file[1] == 'xlsx':
                        if path.getsize(file[0]) < 10000:
                            print(f'{text}')
                        else:
                            print('File too big, but conatins keywords. Check manually\n')
                        break

                print(f'{line}\n')    
    

    def walk_zip(self, zip_path):
        from zipfile import ZipFile
        with ZipFile(zip_path, 'r') as z:
            zip_folder = zip_path.replace('.zip','')
            if not path.isdir(zip_folder):
                z.extractall(path=zip_folder)
                self.walk_dir(zip_folder)
        
        
    def return_sensitive_files(self):
        print('='*50)
        print('[*] Sensitive Files:')
        print('='*50)
        for file in self.sensitive_files:
            print(file[0])



def main():
    import argparse

    parser = argparse.ArgumentParser(usage='python searcher.py -p $PATH [-k keyword1,keyword2,...]', description='Herramienta para extraer informacion de documentos localizados en un directorio en base a keywords. Util para auditorias en las que encontramos un share que nos decargamos mediante netexec o smbclient, y queremos procesar toda la info lo mas rapido posible')
    
    parser.add_argument('-p', '--path', dest='path', help='Ruta a analizar ',required=True)
    parser.add_argument('-k', '--keywords', dest='keywords', default='passw', help="Listado de keywords a buscar separadas por comas. Ex: -k contraseña,admin,passwd")

    args = parser.parse_args()
    
    Searcher(args.path, args.keywords)
    

if __name__ == '__main__':
    main()