from helpers.api import ApiHandler, Input, Output, Request, Response
from agent import AgentContext
from helpers import persist_chat
from helpers.task_scheduler import TaskScheduler
# P020: Archive-on-close patch — archives chat instead of permanent delete
from usr.plugins._core_patches.patches.p020_chat_archive_on_close import (
    archive_chat_instead_of_delete,
)


class RemoveChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")

        scheduler = TaskScheduler.get()
        scheduler.cancel_tasks_by_context(ctxid, terminate_thread=True)

        context = AgentContext.use(ctxid)
        if context:
            # stop processing any tasks
            context.reset()

        # P020: Archive instead of delete — chat is moved to /a0/usr/chats-archive/
        # Pinned chats are refused (must be unpinned first)
        archive_result = archive_chat_instead_of_delete(ctxid)

        # Only remove from AgentContext (in-memory), chat files are preserved in archive
        AgentContext.remove(ctxid)

        await scheduler.reload()

        tasks = scheduler.get_tasks_by_context_id(ctxid)
        for task in tasks:
            await scheduler.remove_task_by_uuid(task.uuid)

        # Context removal affects global chat/task lists in all tabs.
        from helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="api.chat_remove.RemoveChat")

        if archive_result.get("archived"):
            return {
                "message": f"Chat archived: {archive_result.get('chat_name', ctxid)}",
            }
        else:
            return {
                "message": archive_result.get("message", "Context removed."),
            }
