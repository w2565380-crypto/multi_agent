import json
import asyncio
from sqlalchemy.orm import Session
from app.config import settings
from app.services.dify_client import dify_client
from app.utils.file_helper import file_helper
import re

# 严格导入你们现有的三个数据库 Model
from app.models.projects_model import ProjectDB
from app.models.auth_model import UserDB
from app.models.agents_model import ProjectAgentDB



class StepOrchestrator:
    def _clean_think_block(self, text: str) -> str:
        """
        核心工具：自动滤除文本中由 DeepSeek 产生的 <think>...</think> 深度思考部分
        """
        if not text:
            return ""
        # 利用正则表达式，匹配 <think> 标签及其内部所有的文字（跨行），替换为空
        return re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    
    async def step_1_run_pm(self, db: Session, project_id: int):
        """【第一步】触发产品经理生成 PRD，并记入 project_agents 表"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            return
        
        # 安全查询用户名，防止模型中没有 user 级联
        user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
        username = user.user_name if user else "default_user"
        
        project.status = "RUNNING"
        db.commit()

        # 1. 调用 Dify API
        pm_inputs = {"user_requirement": project.description}
        pm_res = await dify_client.run_workflow(settings.DIFY_PM_API_KEY, pm_inputs)
        
        if not pm_res["success"]:
            project.status = "FAILED"
            db.commit()
            return

        raw_prd = pm_res["outputs"].get("prd_content") or pm_res["outputs"].get("text", "")
        prd_content = self._clean_think_block(raw_prd)

        # 2. 🌟 物理写入 PRD.md 到账号隔离的文件夹中
        relative_path = file_helper.save_prd(username, project_id, project.title, prd_content)

        # 3. 写入/更新 AI 角色生成表 (ProjectAgentDB)
        agent = db.query(ProjectAgentDB).filter(
            ProjectAgentDB.project_id == project_id, 
            ProjectAgentDB.role == "PM"
        ).first()
        
        if agent:
            agent.path = relative_path
        else:
            agent = ProjectAgentDB(
                project_id=project_id,
                role="PM",
                agent_name="Product Manager",
                elapsed_time=0,
                path=relative_path
            )
            db.add(agent)

        # 4. 更新项目状态为 PENDING_APPROVAL（待用户审核）
        project.status = "PENDING_APPROVAL"
        db.commit()

    async def step_2_handle_approval(self, db: Session, project_id: int, approved: bool, feedback: str):
        """【第二步】处理用户审批"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            return

        if approved:
            project.status = "RUNNING"
            db.commit()
            asyncio.create_task(self.step_3_run_dev(db, project_id))
        else:
            # 驳回则合并反馈，状态设为 RUNNING，重新交给 PM
            project.description = f"【上次需求】: {project.description}\n【修改意见】: {feedback}"
            project.status = "RUNNING"
            db.commit()
            asyncio.create_task(self.step_1_run_pm(db, project_id))

    async def step_3_run_dev(self, db: Session, project_id: int):
        """【第三步】触发程序员编写代码并物理写入"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            return

        user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
        username = user.user_name if user else "default_user"

        # 从本地物理文件直接读取 PRD 内容
        try:
            prd_content = file_helper.read_prd(username, project_id, project.title)
        except Exception:
            project.status = "FAILED"
            db.commit()
            return

        # 调用 Dify Dev API
        dev_res = await dify_client.run_workflow(settings.DIFY_DEV_API_KEY, {"prd_content": prd_content})
        if not dev_res["success"]:
            project.status = "FAILED"
            db.commit()
            return

        raw_files = dev_res["outputs"].get("code_json") or dev_res["outputs"].get("files", [])
        
        # 🌟 物理写入代码到账号隔离的 src/ 目录下
        relative_path = file_helper.save_src_codes(username, project_id, project.title, raw_files)

        # 写入/更新 AI 角色生成表 (ProjectAgentDB)
        agent = db.query(ProjectAgentDB).filter(
            ProjectAgentDB.project_id == project_id, 
            ProjectAgentDB.role == "DEV"
        ).first()
        
        if agent:
            agent.path = relative_path
        else:
            agent = ProjectAgentDB(
                project_id=project_id,
                role="DEV",
                agent_name="Software Developer",
                elapsed_time=0,
                path=relative_path
            )
            db.add(agent)

        # 自动流转：开发完毕，立即触发 QA
        db.commit()
        asyncio.create_task(self.run_qa_stage(db, project_id))

    async def run_qa_stage(self, db: Session, project_id: int):
        """【第四步】触发测试工程师输出测试报告，并打包 ZIP"""
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            return

        user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
        username = user.user_name if user else "default_user"

        # 物理读取 PRD 和拼接好的多文件代码内容
        try:
            prd_content = file_helper.read_prd(username, project_id, project.title)
            combined_code = file_helper.read_src_codes_combined(username, project_id, project.title)
        except Exception:
            project.status = "FAILED"
            db.commit()
            return

        # 调用 Dify QA API
        qa_res = await dify_client.run_workflow(settings.DIFY_QA_API_KEY, {
            "prd_content": prd_content,
            "code_text": combined_code
        })
        
        if not qa_res["success"]:
            project.status = "FAILED"
            db.commit()
            return

        raw_report = qa_res["outputs"].get("test_report")
        test_report = self._clean_think_block(raw_report)

        # 保存测试报告至本地物理硬盘
        relative_path = file_helper.save_qa_report(username, project_id, project.title, test_report)

        # 写入/更新 AI 角色生成表 (ProjectAgentDB)
        agent = db.query(ProjectAgentDB).filter(
            ProjectAgentDB.project_id == project_id, 
            ProjectAgentDB.role == "QA"
        ).first()
        
        if agent:
            agent.path = relative_path
        else:
            agent = ProjectAgentDB(
                project_id=project_id,
                role="QA",
                agent_name="QA Engineer",
                elapsed_time=0,
                path=relative_path
            )
            db.add(agent)

        # 5. 🌟 异步调用文件助手，在 exports/{username}/ 下打包生成 ZIP
        zip_relative_path = file_helper.zip_project(username, project_id, project.title)
        project.zip_path = zip_relative_path
        project.status = "COMPLETED"
        
        db.commit()

# 实例化全局单例
step_orchestrator = StepOrchestrator()