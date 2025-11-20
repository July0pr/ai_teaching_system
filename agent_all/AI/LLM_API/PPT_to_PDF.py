import os
import glob
from win32com.client import gencache
import pythoncom


def pptToPDF(filename, new_directory):
    pdfName = os.path.basename(filename).split('.ppt')[0] + '.pdf'
    savePathFile = os.path.join(new_directory, pdfName)
    if os.path.isfile(savePathFile):  # 判断目标PDF文件是否已经存在
        print(pdfName, "已转换")
        return savePathFile  # 返回已存在的PDF文件路径
    try:
        p = gencache.EnsureDispatch("PowerPoint.Application")  # 初始化PowerPoint应用程序实例
        ppt = p.Presentations.Open(filename, WithWindow=False)  # 打开PPT/PPTX文件
        ppt.ExportAsFixedFormat(savePathFile, 2, PrintRange=None)  # 导出为PDF
        print("已转换并保存:", savePathFile)
    except Exception as e:
        print(os.path.basename(filename), "文件格式转换失败，因为 %s" % e)
        return None  # 如果转换失败，则返回None
    finally:
        ppt.Close()  # 关闭PPT/PPTX文件
        p.Quit()  # 关闭PowerPoint应用程序
    return savePathFile  # 成功转换后返回新的PDF文件路径


def trans(ppt_file_paths):
    NewDirectory = r"D:\项目与竞赛\深度学习与人工智能\agent_all\data\PPT_to_PDF"
    # 生成PDF文件的存储路径
    if not os.path.exists(NewDirectory):
        os.makedirs(NewDirectory)  # 创建目录如果它不存在

    pdf_file_paths = []  # 存储转换后的PDF文件路径列表
    path_mapping = {}  # 维护原始PPT和转换后PDF文件路径的映射

    for each in ppt_file_paths:
        pdf_path = pptToPDF(each, NewDirectory)
        if pdf_path:  # 只有当pdf_path不是None时才添加到列表中
            pdf_file_paths.append(pdf_path)
            path_mapping[pdf_path] = each  # 记录转换后PDF文件路径到原始PPT文件路径的映射

    return pdf_file_paths, path_mapping
