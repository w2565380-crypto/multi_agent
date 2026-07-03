import asyncio
import sys

# 确保能正确导入 app 包
sys.path.append('.')

from app.services.orchestrator import orchestrator
from app.utils.file_helper import file_helper  # 引入我们刚才写好的文件助手

async def run_full_company_simulation():
    # 用户在前端输入的原始需求描述
    user_requirement = "我需要一个简单的待办事项应用，支持添加、删除和标记任务完成。"
    
    # 启动一键式智能体流水线
    result = await orchestrator.run_full_pipeline(user_requirement)
    
    if result["success"]:
        print("\n" + "★"*20 + " 开始写入物理文件与打包 " + "★"*20)
        
        # 调用文件助手，将产物保存到 exports/my_first_project 目录下
        project_dir, zip_path = file_helper.save_project_artifacts(
            prd_content=result["prd"],
            files_list=result["files"],
            qa_report=result["qa_report"],
            folder_name="my_first_project"  # 保存的文件夹名称
        )
        
        print("\n" + "★"*20 + " 保存完成 " + "★"*20)
        print(f"📂 产物物理文件夹路径: {project_dir}")
        print(f"🎁 压缩包下载路径: {zip_path}")
        print("💡 提示：你现在可以在 VS Code 左侧的 exports 目录下查看生成的文件了！")
        
    else:
        print(f"\n❌ 流水线执行失败！原因: {result['error']}")

if __name__ == "__main__":
    asyncio.run(run_full_company_simulation())