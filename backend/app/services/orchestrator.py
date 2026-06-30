import json
from app.config import settings
from app.services.dify_client import dify_client

class Orchestrator:
    async def run_full_pipeline(self, user_requirement: str) -> dict:
        """
        串行链式调用：PM -> Dev -> QA 的完整业务闭环
        """
        print("\n" + "="*50)
        print("🚀 [调度中心] 开始执行多智能体协同流水线...")
        print("="*50)

        # ---------------------------------------------------------
        # 1. 触发产品经理 (PM_Workflow)
        # ---------------------------------------------------------
        print("\n[第一步: 产品经理 (PM_Agent) 介入]")
        print("   - 职责: 分析原始需求并撰写需求规格说明书 (PRD)...")
        
        pm_inputs = {"user_requirement": user_requirement}
        pm_res = await dify_client.run_workflow(
            api_key=settings.DIFY_PM_API_KEY,
            inputs=pm_inputs
        )
        
        if not pm_res["success"]:
            print(f"   ❌ PM 阶段执行失败: {pm_res['error']}")
            return {"success": False, "error": f"PM 阶段失败: {pm_res['error']}"}
        
        prd_content = pm_res["outputs"].get("prd_content", "")
        if not prd_content:
            prd_content = pm_res["outputs"].get("text", "")
            
        print("   ✅ PM 规划完毕！成功生成需求文档。")

        # ---------------------------------------------------------
        # 【人机协作插桩】
        # ---------------------------------------------------------
        print("\n[人机协作插桩] 自动批准 PRD，进入开发阶段...")

        # ---------------------------------------------------------
        # 2. 触发程序员 (Dev_Workflow)
        # ---------------------------------------------------------
        print("\n[第二步: 程序员 (Dev_Agent) 介入]")
        print("   - 职责: 正在理解 PRD 并编写源代码...")
        
        dev_inputs = {"prd_content": prd_content}
        dev_res = await dify_client.run_workflow(
            api_key=settings.DIFY_DEV_API_KEY,
            inputs=dev_inputs
        )
        
        if not dev_res["success"]:
            print(f"   ❌ Dev 阶段执行失败: {dev_res['error']}")
            return {"success": False, "error": f"Dev 阶段失败: {dev_res['error']}"}
        
        raw_files_list = dev_res["outputs"].get("code_json")
        if raw_files_list is None:
            raw_files_list = dev_res["outputs"].get("files", [])
            
        print(f"   ✅ Dev 编码完毕！共从 Dify 接收到 {len(raw_files_list)} 个原始代码数据。")

        # =========================================================
        # 🌟【核心修复：将 Dify 的 "code_block" 标准化为 "code_content"】
        # =========================================================
        standardized_files = []
        combined_code = ""
        
        for file_obj in raw_files_list:
            # 读取文件名（兼容 file_name 和 filename）
            file_name = file_obj.get("file_name") or file_obj.get("filename") or "index.html"
            
            # 读取代码内容（精准匹配你们 Dify 返回的 "code_block"）
            code_content = file_obj.get("code_block") or file_obj.get("code_content") or ""
            
            # 1. 组装标准化列表（提供给 file_helper 写入硬盘和数据库）
            standardized_files.append({
                "file_name": file_name,
                "file_path": file_obj.get("file_path") or file_name,
                "code_content": code_content
            })
            
            # 2. 拼接为大文本，用于喂给测试工程师 (QA_Agent)
            combined_code += f"=== File: {file_name} ===\n{code_content}\n\n"

        # ---------------------------------------------------------
        # 3. 触发测试工程师 (QA_Workflow)
        # ---------------------------------------------------------
        print("\n[第三步: 测试工程师 (QA_Agent) 介入]")
        print("   - 职责: 对比 PRD 与源代码，执行静态分析并输出测试报告...")
        
        qa_inputs = {
            "prd_content": prd_content,
            "code_text": combined_code  # 传入拼接好的真实代码
        }
        qa_res = await dify_client.run_workflow(
            api_key=settings.DIFY_QA_API_KEY,
            inputs=qa_inputs
        )
        
        if not qa_res["success"]:
            print(f"   ❌ QA 阶段执行失败: {qa_res['error']}")
            return {"success": False, "error": f"QA 阶段失败: {qa_res['error']}"}
        
        test_report = qa_res["outputs"].get("test_report", "")
        if not test_report:
            test_report = qa_res["outputs"].get("text", "")
            
        print("   ✅ QA 测试完成！已输出测试报告。")

        return {
            "success": True,
            "prd": prd_content,
            "files": standardized_files,  # 返回已经标准化好的文件结构
            "qa_report": test_report
        }

# 实例化全局单例
orchestrator = Orchestrator()