'''
This script repackes Android applications from piggybacked_scores_diff.csv list
and generates list with information if applications were repackaged successfully.
'''
import os
import subprocess
import logger
import logging
import csv
import shutil

apktool_path = r'C:\distr\android\apktool\apktool_2.2.3.jar'
jarsigner_path = r'c:\Program Files\Java\jdk1.8.0_111\bin\jarsigner.exe'
zipalign_path = "C:\\users\\aleksandr.pilgun\\appdata\\local\\android\\sdk\\build-tools\\25.0.1\\zipalign.exe"

base_dir = os.path.abspath(os.path.dirname(__file__))
apkrepacker_log_file = os.path.join(base_dir, 'apkrepacker.log')
logging.basicConfig(filename=apkrepacker_log_file, level=logging.DEBUG)
logger.enabled = True

csv_file = "piggybacked_scores_diff.csv"
csv_output_name = "apktool_repackaged.csv"

input_apk_dir = r'E:\apps-serval-piggybacking-2015'
output_apk_dir = r'C:\projects\comma\output'
temp_dir = r'C:\projects\comma\output\temp'

def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()
    return out, err, pipe.returncode

def read_csv(path):
    apks = []
    with open(path, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            apks.append(apk_info(original=row[0], piggy=row[1],
                res_num1=row[2], res_num2=row[3], f_score=row[4], certificates=row[5]))
    return apks

def repackage(output_apk, input_apk, name):
    clean_temp(temp_dir)
    cmd_decode = "java -jar {0} d --force --no-debug-info -o {1} {2}".format(apktool_path, temp_dir, input_apk)
    out_d, err_d, code_d = request_pipe(cmd_decode)
    #logger.log("PATH: {0}BUILD:\nOUT: {1}\nERR: {2}\nCODE: {3}".format(name, out_d, err_d, code_d))
    
    cmd_build = "java -jar {0} b --force-all -o {1} {2}".format(apktool_path, output_apk, temp_dir)
    out_b, err_b, code_b = request_pipe(cmd_build)
    #logger.log("PATH: {0}BUILD:\nOUT: {1}\nERR: {2}\nCODE: {3}".format(name, out_b, err_b, code_b))

    success = str(os.path.exists(output_apk))
    return apktool_rslt(success, out_d, out_b, err_d, err_b, code_d, code_b)

def clean_temp(dir):
    if os.path.exists(dir):
        #Hack for windows. Shutil can't remove files with paths longer 260.
        cmd = "rd {0} /s /q".format(dir)
        request_pipe(cmd)
        #shutil.rmtree(dir)
    os.makedirs(dir)

def save_csv(path, list_of_apks):
    with open(path, 'wb') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(apk_info.get_title())
        for app in list_of_apks:
            writer.writerow(app.get_row())

def main():
    list_of_apks = read_csv(os.path.join(base_dir, csv_file))
    list_of_apks = list_of_apks[1:] #removed title of csv
    apks = len(list_of_apks)
    i = 0
    print("Repackaging of {0} apks.".format(len(list_of_apks)))
    for app in list_of_apks:
        try:
            original_in_apk = os.path.join(input_apk_dir, app.original)
            original_out_apk = os.path.join(output_apk_dir, app.original)
            result = repackage(original_out_apk, original_in_apk, name=app.original)
            app.set_original_apktool_result(result)
            logger.log("-".join(app.get_row()))
            print("{0} - original - {1} - success: {2}".format(i, app.original, app.success1))

        except Exception as e:
            logger.log("FAILED-{0}: {1}".format(app.original, e))
        
        
        # print("{0} - piggy - {1}".format(i, app.piggy))
        # piggy_in_apk = os.path.join(input_apk_dir, app.piggy)
        # piggy_out_apk = os.path.join(output_apk_dir, app.piggy)
        # result = repackage(piggy_out_apk, piggy_in_apk, app.piggy)
        # app.set_piggy_apktool_result(result)
        i += 1
        
    save_csv(os.path.join(base_dir,csv_output_name), list_of_apks)

class apk_info(object):
    def __init__(self, original='', piggy='', res_num1='', res_num2='', 
        f_score='', certificates=''):
        self.original = original
        self.piggy = piggy
        self.res_num1 = res_num1
        self.res_num2 = res_num2
        self.f_score = f_score
        self.certificates = certificates

        self.success1=''
        self.success2=''
        self.out_decode1 = ''
        self.out_decode2 = ''
        self.out_build1 = ''
        self.out_build2 = ''
        self.err_dec1 = ''
        self.err_dec2 = ''
        self.err_build1 = ''
        self.err_build2 = ''
        self.code_dec1 = ''
        self.code_dec2 = ''
        self.code_build1 = ''
        self.code_build2 = ''

    def set_original_apktool_result(self, result):
        self.success1 = result.success
        self.out_decode1 = result.out_decode
        self.out_build1 = result.out_build
        self.err_dec1 = result.err_decode
        self.err_build1 = result.err_build
        self.code_dec1 = result.code_decode
        self.code_build1 = result.code_build

    def set_piggy_apktool_result(self, result):
        self.success2 = result.success
        self.out_decode2 = result.out_decode
        self.out_build2 = result.out_build
        self.err_dec2 = result.err_decode
        self.err_build2 = result.err_build
        self.code_dec2 = result.code_decode
        self.code_build2 = result.code_build

    def get_row(self):
        return [self.original,
                self.piggy,
                self.res_num1,
                self.res_num2,
                self.f_score,
                self.certificates,
                self.success1,
                self.success2,
                self.out_decode1,
                self.out_decode2,
                self.out_build1,
                self.out_build2,
                self.err_dec1,
                self.err_dec2,
                self.err_build1,
                self.err_build2,
                self.code_dec1,
                self.code_dec2,
                self.code_build1,
                self.code_build2]
    @staticmethod
    def get_title():
        return ["original",
                "piggy",
                "res_num1",
                "res_num2",
                "f_score",
                "certificates",
                "success_orig",
                "success_piggy",
                "out_decode1",
                "out_decode2",
                "out_build1",
                "out_build2",
                "err_dec1",
                "err_dec2",
                "err_build1",
                "err_build2",
                "code_dec1",
                "code_dec2",
                "code_build1",
                "code_build2"]

class apktool_rslt(object):
    def __init__(self, success, out_decode, out_build, err_decode, err_build,
        code_decode, code_build):
        self.success = success
        self.out_decode=''#out_decode.replace('\n', ' -> ')
        self.out_build = ''#out_build.replace('\n', ' -> ')
        self.err_decode = err_decode.replace('\r\n', ' -> ').replace('\n',' ')
        self.err_build = err_build.replace('\r\n', ' -> ').replace('\n',' ')
        self.code_decode = str(code_decode)
        self.code_build = str(code_build)

if __name__ == '__main__':
    main()