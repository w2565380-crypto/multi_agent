import os
import zipfile
import shutil

class FileHelper:
    def __init__(self):
        # 定位项目根目录 (backend/)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.exports_dir = os.path.join(self.base_dir, 'exports')
        
        # 确保 exports 目录存在
        os.makedirs(self.exports_dir, exist_ok=True)

    def save_project_artifacts(self, prd_content: str, files_list: list, qa_report: str, folder_name: str = "latest_project") -> tuple:
        """
        保存 PRD、源码和测试报告到服务器，并一键打包为 ZIP
        :return: (保存的物理路径, 打包后的 ZIP 路径)
        """
        project_dir = os.path.join(self.exports_dir, folder_name)
        
        # 1. 每次保存前，如果存在同名旧目录，先清空，保证输出干净
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        os.makedirs(project_dir, exist_ok=True)

        # 2. 物理保存产品经理的 PRD.md
        prd_path = os.path.join(project_dir, 'PRD.md')
        with open(prd_path, 'w', encoding='utf-8') as f:
            f.write(prd_content)
        print(f"   💾 [文件助手] 已写入需求文档: exports/{folder_name}/PRD.md")

        # 3. 物理保存测试工程师的 Test_Report.md
        qa_path = os.path.join(project_dir, 'Test_Report.md')
        with open(qa_path, 'w', encoding='utf-8') as f:
            f.write(qa_report)
        print(f"   💾 [文件助手] 已写入测试报告: exports/{folder_name}/Test_Report.md")

        # 4. 创建代码子目录 src/ 并保存所有代码文件
        src_dir = os.path.join(project_dir, 'src')
        os.makedirs(src_dir, exist_ok=True)
        
        for file_obj in files_list:
            file_name = file_obj.get("file_name", "index.html")
            code_content = file_obj.get("code_content", "")
            
            # 支持多层子目录（如 src/css/style.css）
            file_path = os.path.join(src_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            print(f"   💾 [文件助手] 已生成源码文件: exports/{folder_name}/src/{file_name}")

        # 5. 一键打包为 ZIP 压缩包
        zip_path = os.path.join(self.exports_dir, f"{folder_name}.zip")
        self._zip_folder(project_dir, zip_path)
        print(f"   📦 [文件助手] 已成功打包项目为: exports/{folder_name}.zip")
        
        return project_dir, zip_path

    def _zip_folder(self, folder_path, zip_path):
        """将文件夹打包为 ZIP 格式"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    # 计算相对路径，防止把服务器绝对路径压缩进去
                    rel_path = os.path.relpath(file_full_path, folder_path)
                    zipf.write(file_full_path, rel_path)

# 实例化全局单例
file_helper = FileHelper()