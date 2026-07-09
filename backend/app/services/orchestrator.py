# from app.models.auth_model import UserDB
# from sqlalchemy.orm import Session
# import json
# import asyncio
# import re
# import traceback  # 🌟 引入堆栈追踪库，用于精确捕获后台错误

# # 引入数据库连接池，用于在后台任务里安全地创建独立会话
# from app.database import SessionLocal

# from app.config import settings
# from app.services.dify_client import dify_client
# from app.utils.file_helper import file_helper

# # 引入官方底层接口
# from app.crud.projects_crud import get_project_by_id, update_project_status_or_zip
# from app.crud.agents_crud import (
#     add_project_agent_result, 
#     get_project_agents, 
#     update_agent_output
# )
# from app.models.auth_model import UserDB

# class StepOrchestrator:

#     def _clean_think_block(self, text: str) -> str:
#         """自动滤除 DeepSeek 思考过程"""
#         if not text:
#             return ""
#         return re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    
#     async def step_1_run_pm(self, project_id: int):
#         """【第一步】触发产品经理生成 PRD（全量 Debug 监控版）"""
#         print(f"\n🚀 [DEBUG - STEP 1] 开始执行 PM 任务, 项目 ID: {project_id}")
#         db = SessionLocal()
#         try:
#             # 1. 读取项目
#             project = get_project_by_id(db, project_id)
#             if not project:
#                 print(f"❌ [DEBUG - STEP 1] 错误：未在数据库中找到项目 ID {project_id}，终止流程")
#                 return
            
#             print(f"📋 [DEBUG - STEP 1] 找到项目: '{project.title}', 关联用户 ID: {project.user_id}")
#             user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
#             username = user.user_name if user else "default_user"
#             print(f"👤 [DEBUG - STEP 1] 解析关联用户名: '{username}'")
            
#             # 2. 修改项目状态
#             print(f"💾 [DEBUG - STEP 1] 正在更新项目状态为: RUNNING...")
#             update_project_status_or_zip(db, project_id, status="RUNNING")
#             print(f"💾 [DEBUG - STEP 1] 项目状态已成功变更为: RUNNING")

#             # 3. 调用 Dify API
#             pm_inputs = {"user_requirement": project.description}
#             print(f"📡 [DEBUG - STEP 1] 准备请求 Dify PM 工作流, 接口地址: {settings.DIFY_BASE_URL}, 参数: {pm_inputs}")
            
#             pm_res = await dify_client.run_workflow(settings.DIFY_PM_API_KEY, pm_inputs)
            
#             print(f"📡 [DEBUG - STEP 1] Dify 网络请求返回, success={pm_res['success']}")
#             if not pm_res["success"]:
#                 print(f"❌ [DEBUG - STEP 1] Dify PM 工作流执行失败, 错误详情: {pm_res['error']}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             raw_prd = pm_res["outputs"].get("prd_content") or pm_res["outputs"].get("text", "")
#             print(f"📝 [DEBUG - STEP 1] 成功从 Dify 拿到 PRD 文本, 原始字符长度: {len(raw_prd)}")
            
#             prd_content = self._clean_think_block(raw_prd)
#             print(f"🧹 [DEBUG - STEP 1] 过滤 <think> 后的 PRD 字符长度: {len(prd_content)}")

#             # 4. 物理写入磁盘
#             print(f"💾 [DEBUG - STEP 1] 正在尝试将 PRD.md 写入服务器磁盘...")
#             relative_path = file_helper.save_prd(username, project_id, project.title, prd_content)
#             print(f"💾 [DEBUG - STEP 1] 物理磁盘写入成功! 保存相对路径为: {relative_path}")

#             # 5. 将成果路径及文本登记到数据库
#             print(f"💾 [DEBUG - STEP 1] 正在查询该项目是否已存在 PM 智能体记录...")
#             agents = get_project_agents(db, project_id)
#             pm_agent = next((a for a in agents if a.role == "PM"), None)
            
#             if pm_agent:
#                 print(f"💾 [DEBUG - STEP 1] 已存在 PM 记录 (ID: {pm_agent.id}), 执行 update_agent_output...")
#                 update_agent_output(db, pm_agent.id, final_output=prd_content, path=relative_path)
#             else:
#                 print(f"💾 [DEBUG - STEP 1] 未发现已有记录, 执行 add_project_agent_result 插入新成果...")
#                 add_project_agent_result(
#                     db, 
#                     project_id=project_id, 
#                     role="PM", 
#                     agent_name="Product Manager", 
#                     elapsed_time=0, 
#                     final_output=prd_content,
#                     path=relative_path
#                 )
#             print(f"💾 [DEBUG - STEP 1] project_agents 成果表数据已成功写入/更新")

#             # 6. 更新项目状态为 PENDING_APPROVAL
#             print(f"💾 [DEBUG - STEP 1] 正在更新项目状态为: PENDING_APPROVAL...")
#             update_project_status_or_zip(db, project_id, status="PENDING_APPROVAL")
#             print(f"✅ [DEBUG - STEP 1] PM 阶段业务流转全部成功结束!")

#         except Exception as e:
#             print(f"💥 [DEBUG - STEP 1 ERROR] 发生未捕获异常!")
#             traceback.print_exc()  # 打印详细报错行数和原因
#             try:
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 print(f"💾 [DEBUG - STEP 1] 异常处理：已将项目状态重置为 FAILED")
#             except Exception as db_err:
#                 print(f"💥 [DEBUG - STEP 1] 尝试重置项目状态为 FAILED 时再次失败: {db_err}")
#         finally:
#             db.close()
#             print(f"🔌 [DEBUG - STEP 1] SQLite 数据库连接已安全释放")

#     async def step_2_handle_approval(self, db: Session, project_id: int, approved: bool, feedback: str):
#         """【第二步】处理用户审批（全量 Debug 监控版）"""
#         print(f"\n🚀 [DEBUG - STEP 2] 接收到前端审批请求, 项目 ID: {project_id}, 同意={approved}")
#         try:
#             project = get_project_by_id(db, project_id)
#             if not project:
#                 print(f"❌ [DEBUG - STEP 2] 错误：未在数据库中找到项目 ID {project_id}")
#                 return

#             if approved:
#                 print(f"💾 [DEBUG - STEP 2] 用户批准开发，正在将项目状态修改为 RUNNING...")
#                 update_project_status_or_zip(db, project_id, status="RUNNING")
#                 print(f"💾 [DEBUG - STEP 2] 状态更新成功，准备异步调起 Dev 阶段...")
#                 asyncio.create_task(self.step_3_run_dev(project_id))
#             else:
#                 print(f"💾 [DEBUG - STEP 2] 用户驳回开发，正在合并驳回反馈，准备重置状态...")
#                 from app.models.projects_model import ProjectDB
#                 db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
#                 if db_project:
#                     db_project.description = f"【上次需求】: {db_project.description}\n【修改意见】: {feedback}"
#                     db_project.status = "RUNNING"
#                     db.commit()
#                 print(f"💾 [DEBUG - STEP 2] 数据更新成功，准备异步重跑 PM 阶段...")
#                 asyncio.create_task(self.step_1_run_pm(project_id))
#         except Exception as e:
#             print(f"💥 [DEBUG - STEP 2 ERROR] 发生异常!")
#             traceback.print_exc()

#     async def step_3_run_dev(self, project_id: int):
#         """【第三步】触发程序员编写代码（全量 Debug 监控版）"""
#         print(f"\n🚀 [DEBUG - STEP 3] 开始执行 Dev 任务, 项目 ID: {project_id}")
#         db = SessionLocal()
#         try:
#             project = get_project_by_id(db, project_id)
#             if not project:
#                 return

#             user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
#             username = user.user_name if user else "default_user"

#             # 从数据库读取 PM 路径并加载文件
#             print(f"💾 [DEBUG - STEP 3] 正在查询 PM 角色在数据库中登记的成果文件路径...")
#             agents = get_project_agents(db, project_id)
#             pm_agent = next((a for a in agents if a.role == "PM"), None)
#             if not pm_agent or not pm_agent.path:
#                 print(f"❌ [DEBUG - STEP 3] 错误：未找到 PM 在数据库登记的成果路径")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             print(f"💾 [DEBUG - STEP 3] 找到 PRD 物理登记名: '{pm_agent.path}'，尝试从磁盘加载内容...")
#             try:
#                 prd_content = file_helper.read_file_by_db_path(username, project_id, project.title, pm_agent.path)
#                 print(f"📝 [DEBUG - STEP 3] PRD 文件读取成功，内容长度: {len(prd_content)}")
#             except Exception as file_err:
#                 print(f"❌ [DEBUG - STEP 3] 磁盘文件读取失败: {file_err}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             # 调用 Dify Dev API
#             print(f"📡 [DEBUG - STEP 3] 正在向 Dify 调起 Dev 编码工作流...")
#             dev_res = await dify_client.run_workflow(settings.DIFY_DEV_API_KEY, {"prd_content": prd_content})
            
#             print(f"📡 [DEBUG - STEP 3] Dify Dev 返回, success={dev_res['success']}")
#             if not dev_res["success"]:
#                 print(f"❌ [DEBUG - STEP 3] Dify Dev 调用失败, 错误详情: {dev_res['error']}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             raw_files = dev_res["outputs"].get("code_json") or dev_res["outputs"].get("files", [])
#             print(f"📝 [DEBUG - STEP 3] 从 Dify 接收到 {len(raw_files)} 个代码文件对象")
            
#             # 物理写入代码
#             print(f"💾 [DEBUG - STEP 3] 尝试将代码写入磁盘 /src/ 目录...")
#             relative_path = file_helper.save_src_codes(username, project_id, project.title, raw_files)
#             print(f"💾 [DEBUG - STEP 3] 磁盘源码物理写入成功, 相对路径: {relative_path}")

#             # 写入数据库成果
#             dev_agent = next((a for a in agents if a.role == "DEV"), None)
#             if dev_agent:
#                 print(f"💾 [DEBUG - STEP 3] 发现已有 DEV 记录 (ID: {dev_agent.id}), 执行更新...")
#                 update_agent_output(db, dev_agent.id, final_output="多文件源码已物理写入磁盘", path=relative_path)
#             else:
#                 print(f"💾 [DEBUG - STEP 3] 未发现已有 DEV 记录, 插入新记录...")
#                 add_project_agent_result(
#                     db, 
#                     project_id=project_id, 
#                     role="DEV", 
#                     agent_name="Software Developer", 
#                     elapsed_time=0, 
#                     final_output="多文件源码已物理写入磁盘",
#                     path=relative_path
#                 )
#             print(f"💾 [DEBUG - STEP 3] DEV 角色成果表数据已成功写入/更新")

#             print(f"💾 [DEBUG - STEP 3] 正在更新状态并自动触发测试阶段...")
#             update_project_status_or_zip(db, project_id, status="RUNNING")
#             asyncio.create_task(self.run_qa_stage(project_id))
#             print(f"✅ [DEBUG - STEP 3] Dev 阶段业务流转全部成功结束!")

#         except Exception as e:
#             print(f"💥 [DEBUG - STEP 3 ERROR] 发生异常!")
#             traceback.print_exc()
#             try:
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#             except Exception:
#                 pass
#         finally:
#             db.close()
#             print(f"🔌 [DEBUG - STEP 3] SQLite 数据库连接已安全释放")

#     async def step_3_revise_dev(self, project_id: int, feedback: str):
#         """【代码修改阶段】触发程序员进行代码重构（全量安全监控版）"""
#         print(f"\n🚀 [DEBUG - REVISE] 开始执行代码重构/修复任务, 项目 ID: {project_id}")
#         print(f"💬 [DEBUG - REVISE] 用户的修改建议: '{feedback}'")
#         db = SessionLocal()
#         try:
#             # 1. 获取项目与用户
#             project = get_project_by_id(db, project_id)
#             if not project:
#                 print(f"❌ [DEBUG - REVISE] 错误：未在数据库中找到项目 ID {project_id}，终止流程")
#                 return

#             print(f"📋 [DEBUG - REVISE] 找到项目: '{project.title}', 关联用户 ID: {project.user_id}")
#             user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
#             username = user.user_name if user else "default_user"
#             print(f"👤 [DEBUG - REVISE] 解析关联用户名: '{username}'")

#             # 2. 读取原 PRD
#             print(f"💾 [DEBUG - REVISE] 正在查询 PM 角色在数据库中登记的成果文件路径...")
#             agents = get_project_agents(db, project_id)
#             pm_agent = next((a for a in agents if a.role == "PM"), None)
#             if not pm_agent or not pm_agent.path:
#                 print("❌ [DEBUG - REVISE] 错误：未找到原 PRD 路径，无法获取原始需求描述进行修改，流程中断")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return
            
#             print(f"💾 [DEBUG - REVISE] 找到 PRD 物理登记名: '{pm_agent.path}'，尝试从磁盘加载内容...")
#             original_prd = file_helper.read_file_by_db_path(username, project_id, project.title, pm_agent.path)
#             print(f"📝 [DEBUG - REVISE] 原 PRD 文档读取成功，长度: {len(original_prd)} 字符")

#             # 3. 尝试读取历史测试报告
#             qa_agent = next((a for a in agents if a.role == "QA"), None)
#             qa_report_content = ""
#             if qa_agent and qa_agent.path:
#                 print(f"💾 [DEBUG - REVISE] 检测到已存在历史测试报告登记路径: '{qa_agent.path}'，尝试从磁盘加载...")
#                 try:
#                     qa_report_content = file_helper.read_file_by_db_path(username, project_id, project.title, qa_agent.path)
#                     print(f"📝 [DEBUG - REVISE] 历史测试报告读取成功，长度: {len(qa_report_content)} 字符，准备联合输入给 Dev Agent")
#                 except Exception as qa_err:
#                     print(f"⚠️ [DEBUG - REVISE] 历史测试报告物理读取失败(可能文件已被清理): {qa_err}，将忽略测试报告，仅传 PRD 重新修改")

#             # 4. 内存中动态合成重构需求
#             print(f"⚙️ [DEBUG - REVISE] 正在组装‘合成式重构 PRD’提示词...")
#             synthesized_prd = f"# 原始产品需求文档 (Original PRD)\n\n{original_prd}\n\n"
#             synthesized_prd += f"## 🌟 核心修改指令 (User Feedback)\n用户对当前生成的代码不满意，请务必根据以下具体修改建议，对代码进行重构与修复：\n> {feedback}\n\n"
            
#             if qa_report_content:
#                 synthesized_prd += f"## 📋 现有测试缺陷报告参考 (Test Report)\n请参考以下测试人员找出的 Bug 列表进行协同修复：\n\n{qa_report_content}"
#             print(f"⚙️ [DEBUG - REVISE] 重构 PRD 提示词组装完毕，总长度: {len(synthesized_prd)} 字符")

#             # 5. 更新项目状态为 RUNNING
#             print(f"💾 [DEBUG - REVISE] 正在更新项目状态为: RUNNING...")
#             update_project_status_or_zip(db, project_id, status="RUNNING")

#             # 6. 调用 Dify Dev API
#             print(f"📡 [DEBUG - REVISE] 正在向 Dify 发送重构代码请求...")
#             dev_res = await dify_client.run_workflow(settings.DIFY_DEV_API_KEY, {"prd_content": synthesized_prd})
            
#             print(f"📡 [DEBUG - REVISE] Dify 重构返回, success={dev_res['success']}")
#             if not dev_res["success"]:
#                 print(f"❌ [DEBUG - REVISE] Dify 重构代码失败, 错误原因: {dev_res['error']}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             raw_files = dev_res["outputs"].get("code_json") or dev_res["outputs"].get("files", [])
#             print(f"📝 [DEBUG - REVISE] 从 Dify 接收到 {len(raw_files)} 个最新重构后的代码文件对象")

#             # 7. 物理写入磁盘
#             print(f"💾 [DEBUG - REVISE] 正在物理覆盖写入最新修改后的代码文件到 /src/ 目录...")
#             relative_path = file_helper.save_src_codes(username, project_id, project.title, raw_files)
#             print(f"💾 [DEBUG - REVISE] 重构代码源码物理写入磁盘成功, 相对路径: {relative_path}")

#             # 8. 更新/追加 成果表中的 DEV 记录
#             dev_agent = next((a for a in agents if a.role == "DEV"), None)
#             if dev_agent:
#                 print(f"💾 [DEBUG - REVISE] 发现已有 DEV 记录 (ID: {dev_agent.id}), 执行更新...")
#                 update_agent_output(db, dev_agent.id, final_output="多文件源码已重构物理覆盖写入磁盘", path=relative_path)
#             else:
#                 print(f"💾 [DEBUG - REVISE] 未发现已有 DEV 记录, 插入新记录...")
#                 add_project_agent_result(
#                     db, 
#                     project_id=project_id, 
#                     role="DEV", 
#                     agent_name="Software Developer", 
#                     elapsed_time=0, 
#                     final_output="多文件源码已重构物理覆盖写入磁盘",
#                     path=relative_path
#                 )
#             print(f"💾 [DEBUG - REVISE] DEV 角色成果表数据已成功写入/更新")

#             # 9. 自动重新触发 QA 测试并重新打包
#             print(f"💾 [DEBUG - REVISE] 代码重构落盘成功，正在自动启动 QA 重新测试...")
#             asyncio.create_task(self.run_qa_stage(project_id))
#             print(f"✅ [DEBUG - REVISE] 代码重构指令已完美成功下达后台执行!")

#         except Exception as e:
#             print(f"💥 [DEBUG - REVISE ERROR] 发生未捕获异常!")
#             traceback.print_exc()
#             try:
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#             except Exception:
#                 pass
#         finally:
#             db.close()
#             print(f"🔌 [DEBUG - REVISE] SQLite 数据库连接已安全释放")

#     async def run_qa_stage(self, project_id: int):
#         """【第四步】触发测试工程师并打包归档（全量 Debug 监控版）"""
#         print(f"\n🚀 [DEBUG - STEP 4] 开始执行 QA 任务, 项目 ID: {project_id}")
#         db = SessionLocal()
#         try:
#             project = get_project_by_id(db, project_id)
#             if not project:
#                 return

#             user = db.query(UserDB).filter(UserDB.id == project.user_id).first()
#             username = user.user_name if user else "default_user"

#             # 严格根据数据库路径去读文件
#             print(f"💾 [DEBUG - STEP 4] 正在查询 PM 与 DEV 角色在数据库中登记的成果文件路径...")
#             agents = get_project_agents(db, project_id)
#             pm_agent = next((a for a in agents if a.role == "PM"), None)
#             dev_agent = next((a for a in agents if a.role == "DEV"), None)
            
#             if not pm_agent or not dev_agent or not pm_agent.path or not dev_agent.path:
#                 print(f"❌ [DEBUG - STEP 4] 错误：未找到 PM 或 DEV 的数据库登记路径")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             print(f"💾 [DEBUG - STEP 4] 找到 PM 路径: '{pm_agent.path}', DEV 路径: '{dev_agent.path}'")
#             try:
#                 prd_content = file_helper.read_file_by_db_path(username, project_id, project.title, pm_agent.path)
#                 combined_code = file_helper.read_src_codes_combined_by_db_path(username, project_id, project.title, dev_agent.path)
#                 print(f"📝 [DEBUG - STEP 4] 磁盘数据成功加载。PRD长度: {len(prd_content)}, 源码长度: {len(combined_code)}")
#             except Exception as file_err:
#                 print(f"❌ [DEBUG - STEP 4] 磁盘文件读取失败: {file_err}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             # 调用 Dify QA API
#             print(f"📡 [DEBUG - STEP 4] 正在向 Dify 调起 QA 静态审查工作流...")
#             qa_res = await dify_client.run_workflow(settings.DIFY_QA_API_KEY, {
#                 "prd_content": prd_content,
#                 "code_text": combined_code
#             })
            
#             print(f"📡 [DEBUG - STEP 4] Dify QA 返回, success={qa_res['success']}")
#             if not qa_res["success"]:
#                 print(f"❌ [DEBUG - STEP 4] Dify QA 调用失败, 错误详情: {qa_res['error']}")
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#                 return

#             raw_report = qa_res["outputs"].get("test_report") or qa_res["outputs"].get("text", "")
#             test_report = self._clean_think_block(raw_report)
#             print(f"🧹 [DEBUG - STEP 4] 过滤 <think> 后的测试报告长度: {len(test_report)}")

#             # 保存测试报告至本地物理硬盘
#             print(f"💾 [DEBUG - STEP 4] 正在将测试报告写入本地磁盘...")
#             relative_path = file_helper.save_qa_report(username, project_id, project.title, test_report)
#             print(f"💾 [DEBUG - STEP 4] 测试报告物理写入成功, 相对路径: {relative_path}")

#             # 写入数据库成果
#             qa_agent = next((a for a in agents if a.role == "QA"), None)
#             if qa_agent:
#                 print(f"💾 [DEBUG - STEP 4] 发现已有 QA 记录 (ID: {qa_agent.id}), 执行更新...")
#                 update_agent_output(db, qa_agent.id, final_output=test_report, path=relative_path)
#             else:
#                 print(f"💾 [DEBUG - STEP 4] 未发现已有 QA 记录, 插入新记录...")
#                 add_project_agent_result(
#                     db, 
#                     project_id=project_id, 
#                     role="QA", 
#                     agent_name="QA Engineer", 
#                     elapsed_time=0, 
#                     final_output=test_report,
#                     path=relative_path
#                 )
#             print(f"💾 [DEBUG - STEP 4] QA 角色成果表数据已成功写入/更新")

#             # 5. 异步调用文件助手，在 exports/{username}/ 下打包生成 ZIP
#             print(f"💾 [DEBUG - STEP 4] 正在执行全量打包 ZIP...")
#             zip_relative_path = file_helper.zip_project(username, project_id, project.title)
#             print(f"💾 [DEBUG - STEP 4] ZIP 打包成功, 相对路径: {zip_relative_path}")
            
#             print(f"💾 [DEBUG - STEP 4] 正在将项目状态标志更新为: COMPLETED...")
#             update_project_status_or_zip(db, project_id, status="COMPLETED", zip_path=zip_relative_path)
#             print(f"🎉 [DEBUG - STEP 4] 所有协同任务圆满交付结束!")
#         except Exception as e:
#             print(f"💥 [DEBUG - STEP 4 ERROR] 发生异常!")
#             traceback.print_exc()
#             try:
#                 update_project_status_or_zip(db, project_id, status="FAILED")
#             except Exception:
#                 pass
#         finally:
#             db.close()
#             print(f"🔌 [DEBUG - STEP 4] SQLite 数据库连接已安全释放")

# # 实例化全局单例
# step_orchestrator = StepOrchestrator()

import json
import asyncio
import re
import traceback

# 引入数据库连接池
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.config import settings
from app.services.dify_client import dify_client
from app.utils.file_helper import file_helper

# 引入官方底层接口
from app.crud.projects_crud import get_project_by_id, update_project_status_or_zip
from app.crud.agents_crud import (
    add_project_agent_result, 
    get_project_agents, 
    update_agent_output
)
from app.models.auth_model import UserDB

class StepOrchestrator:

    def _clean_think_block(self, text: str) -> str:
        """自动滤除 DeepSeek 思考过程"""
        if not text:
            return ""
        return re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    
    async def step_1_run_pm(self, project_id: int):
        """【第一步】触发产品经理生成 PRD"""
        print(f"\n🚀 [DEBUG - PM] 开始执行 PM 任务, 项目 ID: {project_id}")
        db = SessionLocal()
        try:
            project = get_project_by_id(db, project_id)
            if not project:
                return
            
            update_project_status_or_zip(db, project_id, status="RUNNING")

            pm_inputs = {"user_requirement": project.description}
            pm_res = await dify_client.run_workflow(settings.DIFY_PM_API_KEY, pm_inputs)
            
            if not pm_res["success"]:
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            raw_prd = pm_res["outputs"].get("prd_content") or pm_res["outputs"].get("text", "")
            prd_content = self._clean_think_block(raw_prd)

            relative_path = file_helper.save_prd(project.user_id, project_id, project.title, prd_content)

            agents = get_project_agents(db, project_id)
            pm_agent = next((a for a in agents if a.role == "PM"), None)
            
            if pm_agent:
                update_agent_output(db, pm_agent.id, final_output=prd_content, path=relative_path)
            else:
                add_project_agent_result(
                    db, 
                    project_id=project_id, 
                    role="PM", 
                    agent_name="Product Manager", 
                    elapsed_time=0, 
                    final_output=prd_content,
                    path=relative_path
                )

            update_project_status_or_zip(db, project_id, status="PENDING_APPROVAL")
        except Exception as e:
            print(f"💥 [DEBUG - PM ERROR] 发生异常!")
            traceback.print_exc()
            try:
                update_project_status_or_zip(db, project_id, status="FAILED")
            except Exception:
                pass
        finally:
            db.close()

    async def step_2_handle_approval(self, db: Session, project_id: int, approved: bool, feedback: str):
        """【第二步】处理用户审批"""
        try:
            if approved:
                update_project_status_or_zip(db, project_id, status="RUNNING")
                asyncio.create_task(self.step_3_run_dev(project_id))
            else:
                from app.models.projects_model import ProjectDB
                db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
                if db_project:
                    db_project.description = f"【上次需求】: {db_project.description}\n【修改意见】: {feedback}"
                    db_project.status = "RUNNING"
                    db.commit()
                asyncio.create_task(self.step_1_run_pm(project_id))
        except Exception as e:
            print(f"💥 [DEBUG - HITL ERROR] 发生异常!")
            traceback.print_exc()

    async def step_3_run_dev(self, project_id: int):
        """【第三步】触发程序员编写代码"""
        print(f"\n🚀 [DEBUG - DEV] 开始执行 Dev 任务, 项目 ID: {project_id}")
        db = SessionLocal()
        try:
            project = get_project_by_id(db, project_id)
            if not project:
                return

            agents = get_project_agents(db, project_id)
            pm_agent = next((a for a in agents if a.role == "PM"), None)
            if not pm_agent or not pm_agent.path:
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            try:
                prd_content = file_helper.read_file_by_db_path(project.user_id, project_id, project.title, pm_agent.path)
            except Exception:
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            dev_res = await dify_client.run_workflow(settings.DIFY_DEV_API_KEY, {"prd_content": prd_content})
            if not dev_res["success"]:
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            raw_files = dev_res["outputs"].get("code_json") or dev_res["outputs"].get("files", [])
            relative_path = file_helper.save_src_codes(project.user_id, project_id, project.title, raw_files)

            dev_agent = next((a for a in agents if a.role == "DEV"), None)
            if dev_agent:
                update_agent_output(db, dev_agent.id, final_output="多文件源码已物理写入磁盘", path=relative_path)
            else:
                add_project_agent_result(
                    db, 
                    project_id=project_id, 
                    role="DEV", 
                    agent_name="Software Developer", 
                    elapsed_time=0, 
                    final_output="多文件源码已物理写入磁盘",
                    path=relative_path
                )

            update_project_status_or_zip(db, project_id, status="RUNNING")
            asyncio.create_task(self.run_qa_stage(project_id))
        except Exception as e:
            print(f"💥 [DEBUG - DEV ERROR] 发生异常!")
            traceback.print_exc()
            try:
                update_project_status_or_zip(db, project_id, status="FAILED")
            except Exception:
                pass
        finally:
            db.close()

    async def step_3_revise_dev(self, project_id: int, feedback: str):
        """【代码修改阶段】触发程序员进行代码重构（🌟 智能更新 PRD Addendum 完美闭环版）"""
        print(f"\n🚀 [DEBUG - REVISE] 开始执行代码重构/修复任务, 项目 ID: {project_id}")
        print(f"💬 [DEBUG - REVISE] 用户的最新修改/新增需求建议: '{feedback}'")
        db = SessionLocal()
        try:
            project = get_project_by_id(db, project_id)
            if not project:
                return

            # 1. 检索已有 PRD 路径
            agents = get_project_agents(db, project_id)
            pm_agent = next((a for a in agents if a.role == "PM"), None)
            if not pm_agent or not pm_agent.path:
                print("❌ [DEBUG - REVISE] 错误：未找到原 PRD 路径，无法获取原始需求描述进行修改")
                update_project_status_or_zip(db, project_id, status="FAILED")
                return
            
            # 读取旧 PRD
            original_prd = file_helper.read_file_by_db_path(project.user_id, project_id, project.title, pm_agent.path)

            # 2. 🌟 逻辑重构核心：在原 PRD 末尾动态追加“需求变更说明”，使 PRD 升级为包含新功能要求的正式文档
            addendum_header = "\n\n# 🌈 需求变更追加说明 (Agile Change Requests)\n"
            if addendum_header not in original_prd:
                updated_prd = original_prd + addendum_header
            else:
                updated_prd = original_prd

            # 追加带有格式的最新修改/新增指令（QA Agent 读取后会将其视为官方白名单需求）
            updated_prd += f"\n*   **[最新追加指令]**: {feedback}\n"
            print(f"⚙️ [DEBUG - REVISE] 需求文档已同步完成敏捷变更追加，更新后 PRD 字符长度: {len(updated_prd)}")

            # 3. 🌟 将更新后的 PRD 覆写回磁盘，并同步更新到数据库中 PM 角色下，完成数据闭环！
            file_helper.save_prd(project.user_id, project_id, project.title, updated_prd)
            update_agent_output(db, pm_agent.id, final_output=updated_prd, path=pm_agent.path)
            print(f"💾 [DEBUG - REVISE] 最新 PRD 已成功物理写盘并更新数据库，确保 QA 校验不会产生偏航！")

            # 4. 尝试读取历史测试报告
            qa_agent = next((a for a in agents if a.role == "QA"), None)
            qa_report_content = ""
            if qa_agent and qa_agent.path:
                try:
                    qa_report_content = file_helper.read_file_by_db_path(project.user_id, project_id, project.title, qa_agent.path)
                    print(f"📝 [DEBUG - REVISE] 历史测试报告读取成功")
                except Exception:
                    pass

            # 5. 组装输入给 Dev 的上下文（包含更新后的 PRD、新指令和旧测试报告）
            synthesized_dev_input = f"{updated_prd}\n\n"
            if qa_report_content:
                synthesized_dev_input += f"## 📋 现有测试缺陷报告参考 (Test Report)\n请参考以下测试人员找出的 Bug 列表进行协同修复：\n\n{qa_report_content}"

            # 6. 更新项目状态为 RUNNING
            update_project_status_or_zip(db, project_id, status="RUNNING")

            # 调用 Dify Dev API
            print(f"📡 [DEBUG - REVISE] 正在向 Dify 发送重构代码请求...")
            dev_res = await dify_client.run_workflow(settings.DIFY_DEV_API_KEY, {"prd_content": synthesized_dev_input})
            if not dev_res["success"]:
                print(f"❌ [DEBUG - REVISE] Dify 重构代码失败, 原因: {dev_res['error']}")
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            raw_files = dev_res["outputs"].get("code_json") or dev_res["outputs"].get("files", [])

            # 物理覆写最新源码
            relative_path = file_helper.save_src_codes(project.user_id, project_id, project.title, raw_files)

            # 更新 DEV 成果记录
            dev_agent = next((a for a in agents if a.role == "DEV"), None)
            if dev_agent:
                update_agent_output(db, dev_agent.id, final_output="多文件源码已重构物理覆盖写入磁盘", path=relative_path)
            else:
                add_project_agent_result(
                    db, 
                    project_id=project_id, 
                    role="DEV", 
                    agent_name="Software Developer", 
                    elapsed_time=0, 
                    final_output="多文件源码已重构物理覆盖写入磁盘",
                    path=relative_path
                )

            # 7. 自动触发重新测试并打包（此时 QA 拿到的是更新后的 PRD，新功能完美通过验证！）
            print(f"💾 [DEBUG - REVISE] 代码重构落盘成功，自动启动 QA 重新测试...")
            asyncio.create_task(self.run_qa_stage(project_id))

        except Exception as e:
            print(f"💥 [DEBUG - REVISE ERROR] 发生未捕获异常!")
            traceback.print_exc()
            try:
                update_project_status_or_zip(db, project_id, status="FAILED")
            except Exception:
                pass
        finally:
            db.close()
            print(f"🔌 [DEBUG - REVISE] SQLite 数据库连接已安全释放")

    async def run_qa_stage(self, project_id: int):
        """【第四步】触发测试工程师并打包归档"""
        print(f"\n🚀 [DEBUG - QA] 开始执行 QA 任务, 项目 ID: {project_id}")
        db = SessionLocal()
        try:
            project = get_project_by_id(db, project_id)
            if not project:
                return

            # 获取登记的 PRD 与代码路径
            agents = get_project_agents(db, project_id)
            pm_agent = next((a for a in agents if a.role == "PM"), None)
            dev_agent = next((a for a in agents if a.role == "DEV"), None)
            
            if not pm_agent or not dev_agent or not pm_agent.path or not dev_agent.path:
                print(f"❌ [DEBUG - QA] 错误：未找到 PM 或 DEV 的数据库登记路径")
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            try:
                # 读取 PRD（如果是修改阶段，读到的是带 Addendum 变更说明的最新的 PRD）
                prd_content = file_helper.read_file_by_db_path(project.user_id, project_id, project.title, pm_agent.path)
                combined_code = file_helper.read_src_codes_combined_by_db_path(project.user_id, project_id, project.title, dev_agent.path)
            except Exception as file_err:
                print(f"❌ [DEBUG - QA] 磁盘文件读取失败: {file_err}")
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            # 调用 Dify QA API
            print(f"📡 [DEBUG - QA] 正在向 Dify 调起 QA 静态审查工作流...")
            qa_res = await dify_client.run_workflow(settings.DIFY_QA_API_KEY, {
                "prd_content": prd_content,
                "code_text": combined_code
            })
            
            if not qa_res["success"]:
                print(f"❌ [DEBUG - QA] Dify QA 调用失败, 错误详情: {qa_res['error']}")
                update_project_status_or_zip(db, project_id, status="FAILED")
                return

            raw_report = qa_res["outputs"].get("test_report") or qa_res["outputs"].get("text", "")
            test_report = self._clean_think_block(raw_report)

            # 保存测试报告至本地物理硬盘
            relative_path = file_helper.save_qa_report(project.user_id, project_id, project.title, test_report)

            # 写入成果表
            qa_agent = next((a for a in agents if a.role == "QA"), None)
            if qa_agent:
                update_agent_output(db, qa_agent.id, final_output=test_report, path=relative_path)
            else:
                add_project_agent_result(
                    db, 
                    project_id=project_id, 
                    role="QA", 
                    agent_name="QA Engineer", 
                    elapsed_time=0, 
                    final_output=test_report,
                    path=relative_path
                )

            # 物理打包为 ZIP
            zip_relative_path = file_helper.zip_project(project.user_id, project_id, project.title)
            
            # 更新项目表
            update_project_status_or_zip(db, project_id, status="COMPLETED", zip_path=zip_relative_path)
            print(f"🎉 [DEBUG - QA] 所有协同任务圆满交付结束!")
        except Exception as e:
            print(f"💥 [DEBUG - QA ERROR] 发生异常!")
            traceback.print_exc()
            try:
                update_project_status_or_zip(db, project_id, status="FAILED")
            except Exception:
                pass
        finally:
            db.close()
            print(f"🔌 [DEBUG - QA] SQLite 数据库连接已安全释放")

# 实例化全局单例
step_orchestrator = StepOrchestrator()