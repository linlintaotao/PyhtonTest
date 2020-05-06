import os
import zipfile


# 压缩zip
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(os.path.join(source_dir, output_filename), 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfinder = os.path.join(parent, filename)
            arcname = pathfinder[pre_len:].strip(os.path.sep)
            zipf.write(pathfinder, arcname)
    zipf.close()


if __name__ == '__main__':
    # 获取路径
    report_dir = os.path.abspath('..') + "/data/"
    # 调用打包方法
    make_zip(report_dir, os.path.join(os.path.abspath('..'), "dailyReport.zip"))
