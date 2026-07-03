import os
import zipfile
import shutil

class FileHelper:
    def __init__(self):
        # 本地绝对路径定位到 backend/exports/
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.exports_dir = os.path.join(self.base_dir, 'exports')
        os.makedirs(self.exports_dir, exist_ok=True)

    def get_project_dir(self, username: str, project_id: int, project_title: str) -> str:
        """🌟 核心修改：拼入 username，与你修改后的 projects_crud.py 保持 100% 一致！"""
        safe_title = "".join([c for c in project_title if c.isalnum() or c in ('_', '-')])
        return os.path.join(self.exports_dir, username, f"project_{project_id}_{safe_title}")

    def save_prd(self, username: str, project_id: int, project_title: str, prd_content: str) -> str:
        """物理保存 PRD 到隔离账号目录下"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        os.makedirs(project_dir, exist_ok=True)
        prd_path = os.path.join(project_dir, "PRD.md")
        with open(prd_path, 'w', encoding='utf-8') as f:
            f.write(prd_content)
        return "PRD.md"

    def read_prd(self, username: str, project_id: int, project_title: str) -> str:
        """读取隔离账号目录下的 PRD"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        prd_path = os.path.join(project_dir, "PRD.md")
        if not os.path.exists(prd_path):
            raise FileNotFoundError("未找到 PRD 文件")
        with open(prd_path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_src_codes(self, username: str, project_id: int, project_title: str, files_list: list) -> str:
        """物理保存代码到隔离账号目录下的 src/ 目录"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        src_dir = os.path.join(project_dir, "src")
        
        if os.path.exists(src_dir):
            shutil.rmtree(src_dir)
        os.makedirs(src_dir, exist_ok=True)

        for file_obj in files_list:
            file_name = file_obj.get("file_name") or file_obj.get("filename") or "index.html"
            code_content = file_obj.get("code_block") or file_obj.get("code_content") or ""
            
            file_path = os.path.join(src_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
        return "src/"

    def read_src_codes_combined(self, username: str, project_id: int, project_title: str) -> str:
        """读取隔离账号下的多文件代码并拼接"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        src_dir = os.path.join(project_dir, "src")
        if not os.path.exists(src_dir):
            return ""
        
        combined = ""
        for root, _, files in os.walk(src_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, src_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined += f"=== File: {rel_path} ===\n{f.read()}\n\n"
        return combined
    
    def read_qa_report(self, username: str, project_id: int, project_title: str) -> str:
        """读取隔离账号目录下的 Test_Report.md 文本"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        qa_path = os.path.join(project_dir, "Test_Report.md")
        if not os.path.exists(qa_path):
            raise FileNotFoundError("未找到测试报告文件")
        with open(qa_path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_qa_report(self, username: str, project_id: int, project_title: str, qa_report: str) -> str:
        """物理保存测试报告到隔离账号目录下"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        qa_path = os.path.join(project_dir, "Test_Report.md")
        with open(qa_path, 'w', encoding='utf-8') as f:
            f.write(qa_report)
        return "Test_Report.md"

    def zip_project(self, username: str, project_id: int, project_title: str) -> str:
        """打包隔离账号下的项目目录"""
        project_dir = self.get_project_dir(username, project_id, project_title)
        user_dir = os.path.dirname(project_dir)
        zip_path = os.path.join(user_dir, f"project_{project_id}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_full_path, project_dir)
                    zipf.write(file_full_path, rel_path)
        # 返回对齐 Dify 和打包的相对路径：previews/{username}/project_{id}.zip
        return f"exports/{username}/project_{project_id}.zip"

# 实例化全局单例
file_helper = FileHelper()