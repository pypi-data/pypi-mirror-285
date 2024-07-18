import zipfile
import chardet
import os
import shutil
import socket
import xml.etree.ElementTree as ET


def is_port_open(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # 设置超时时间
    try:
        sock.connect((ip, int(port)))
        return True
    except (socket.timeout, ConnectionRefusedError):  # 端口不可达或连接被拒绝
        return False
    finally:
        sock.close()


def support_gbk(zip_file: zipfile.ZipFile):
    """
    用于支持解码中文路径，避免乱码
    """
    name_to_info = zip_file.NameToInfo
    for name, info in name_to_info.copy().items():
        name_list = os.path.split(name)
        real_name = ""
        for n in name_list:
            try:
                encoding = chardet.detect(n.encode("cp437")).get("encoding")
            except UnicodeEncodeError:
                real_name = "/" + n
            else:
                if encoding:
                    real_name += "/" + n.encode("cp437").decode(encoding)
                else:
                    real_name += "/" + n

        if real_name != name:
            info.filename = real_name
            del name_to_info[name]
            name_to_info[real_name] = info
    return zip_file


def unzip_file(zip_path, target_dir):
    with support_gbk(zipfile.ZipFile(zip_path, "r")) as zip_ref:
        zip_ref.extractall(target_dir)

    # 删除解压目录中的__MACOSX .DS_Store
    for root, dirs, files in os.walk(target_dir):
        if "__MACOSX" in dirs:
            macosx_dir = os.path.join(root, "__MACOSX")
            shutil.rmtree(macosx_dir)
        for file in files:
            if ".DS_Store" == file:
                macosx_dir = os.path.join(root, ".DS_Store")
                os.remove(macosx_dir)


def move_image(source_dir, target_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 检查是否为图片文件（这里以.jpg和.png为例，根据需要添加更多格式）
            if file.endswith((".jpg", ".jpeg", ".png")):
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(target_dir, file)
                # 如果目标路径不在目标目录下，则创建相应的子目录结构
                dst_subdir = os.path.dirname(dst_file_path)
                if not os.path.exists(dst_subdir):
                    os.makedirs(dst_subdir)
                # 移动文件
                shutil.move(src_file_path, dst_file_path)


def xml_to_txt(source_dir: str, target_dir: str):
    # 读取原始目录下所有xml, 获取xml中的所有标签, 生成标签文件
    classes = set()
    new_labels_dir = os.path.join(target_dir, "labels")
    new_images_dir = os.path.join(target_dir, "images")
    os.makedirs(new_images_dir, exist_ok=True)
    os.makedirs(new_labels_dir, exist_ok=True)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 检查是否为xml文件
            if file.endswith("xml"):
                xml_filename = os.path.join(root, file)
                tree = ET.parse(xml_filename)
                root_doc = tree.getroot()
                for obj in root_doc.findall("object"):
                    class_label = obj.findtext("name")
                    classes.add(class_label)
    # 读取原始目录下所有xml, 将xml中的标注信息转换为yolo格式,
    classes_list = list(classes)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 检查是否为xml文件
            boxes = []
            if file.endswith("xml"):
                xml_filename = os.path.join(root, file)
                tree = ET.parse(xml_filename)
                root_doc = tree.getroot()
                width = float(root_doc.findtext(".//width"))  # noqa
                height = float(root_doc.findtext(".//height"))  # noqa
                filename = root_doc.findtext(".//filename")
                # 文件名中可能有多个., 去除最后的后缀
                split_list = filename.split(".")
                split_list.pop(-1)
                txt_filename = ".".join(split_list) + ".txt"
                for obj in tree.iter("object"):
                    cls_name = obj.findtext("name")
                    cls = classes_list.index(cls_name)
                    xmin = float(obj.findtext("bndbox/xmin"))
                    ymin = float(obj.findtext("bndbox/ymin"))
                    xmax = float(obj.findtext("bndbox/xmax"))
                    ymax = float(obj.findtext("bndbox/ymax"))
                    w = xmax - xmin
                    h = ymax - ymin
                    cx = xmin + w / 2
                    cy = ymin + h / 2
                    off_cx, off_cy = cx / width, cy / height
                    off_w, off_h = w / width, h / height
                    boxes.append(f"{cls} {off_cx} {off_cy} {off_w} {off_h}")
                with open(f"{target_dir}/labels/{txt_filename}", "w") as f:
                    f.write("\n".join(boxes))
    # 将原始目录所有图片文件移动到f"{output_dir}/images"下
    move_image(source_dir, os.path.join(target_dir, "images"))
    with open(f"{target_dir}/classes.txt", "w") as f:
        f.write("\n".join(classes_list))
