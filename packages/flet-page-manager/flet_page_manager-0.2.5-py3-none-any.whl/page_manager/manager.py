from __future__ import annotations

import asyncio
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from typing import Generic, ParamSpec, TypeVar, Any, Awaitable, Callable, Iterable

import flet as ft
from flet import AppView
from loguru import logger

from .pages import PageBase
from .state import StateBase
from .utils import get_free_port
__PageManager_StateT = TypeVar("__PageManager_StateT", bound = StateBase)


class PageManager(Generic[__PageManager_StateT]):
    logger = logger
    page_mapping: dict[str, type[PageBase]] = {}

    @staticmethod
    def register_page(
        name: str | None = None,
    ) -> Callable[[type[PageBase[__PageManager_StateT]]], type[PageBase[__PageManager_StateT]]]:
        def _register_page(page_cls: type[PageBase[__PageManager_StateT]]) -> type[PageBase[__PageManager_StateT]]:
            PageManager.page_mapping[name or page_cls.__name__] = page_cls
            return page_cls

        return _register_page

    @staticmethod
    def set_level(level: str | int):
        logger.remove(0)
        logger.add(sys.stdout, level=level)

    def __init__(
        self,
        state: __PageManager_StateT,
        *,
        view: AppView = AppView.FLET_APP,
        assets_dir: str = "public",
    ) -> None:
        self.state = state
        self.view = view
        self.assets_dir = assets_dir

        self.page_count: int = 0
        self.page_tasks: list[asyncio.Task[Any]] = []
        self.backgroud_futures: list[Future[Any]] = []
        self.need_restart: bool = False
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
    __PageManager_run_task_InputT = ParamSpec("__PageManager_run_task_InputT")
    __PageManager_run_task_RetT = TypeVar("__PageManager_run_task_RetT")

    def run_task(
        self,
        handler: Callable[__PageManager_run_task_InputT, Awaitable[__PageManager_run_task_RetT]],
        *args: __PageManager_run_task_InputT.args,
        **kwargs: __PageManager_run_task_InputT.kwargs,
    ) -> Future[__PageManager_run_task_RetT]:
        assert asyncio.iscoroutinefunction(handler)
        task = asyncio.run_coroutine_threadsafe(handler(*args, **kwargs), self.loop)
        self.backgroud_futures.append(task)
        return task
    __PageManager_run_thread_InputT = ParamSpec("__PageManager_run_thread_InputT")

    def run_thread(
        self, handler: Callable[__PageManager_run_thread_InputT, Any], *args: __PageManager_run_thread_InputT.args, **kwargs: __PageManager_run_thread_InputT.kwargs
    ):
        self.loop.call_soon_threadsafe(
            self.loop.run_in_executor, self.executor, partial(handler, *args, **kwargs)
        )

    async def cancel_tasks(self, tasks: Iterable[asyncio.Task[Any]]):
        wrapped_tasks: list[asyncio.Task[Any]] = []
        for task in tasks:
            if not task.done():
                task.cancel()
                self.logger.info("PageManager: Task {:} canceled".format(task.get_name()))
                wrapped_tasks.append(task)
        await asyncio.gather(*wrapped_tasks, return_exceptions=True)

    async def cancel_futures(self, futures: Iterable[Future[Any]]):
        wrapped_futures: list[asyncio.Future[Any]] = []

        for future in futures:
            if not future.done():
                future.cancel()
                self.logger.info("PageManager: Future canceled")
                wrapped_futures.append(asyncio.wrap_future(future))

        await asyncio.gather(*wrapped_futures, return_exceptions=True)

    async def check_page_count(self):
        while self.page_count > 0 and not self.need_restart:
            for task in self.page_tasks:
                await asyncio.sleep(0.1)
                if task.done():
                    self.page_count -= 1
                    self.page_tasks.remove(task)
        await self.cancel_tasks(asyncio.all_tasks() - {asyncio.current_task()})
        self.logger.info("PageManager: Event loop stopped, exiting...")

    def open_page(self, name: str, *, port: int = 0):
        if name not in PageManager.page_mapping:
            logger.error("Page `{:}` not found".format(name))
            return
        if port == 0:
            port = get_free_port()
        page_obj = PageManager.page_mapping[name]()
        self.page_count += 1
        task = self.loop.create_task(
            ft.app_async(
                target=partial(page_obj, pm=self),
                view=self.view,
                port=port,
                assets_dir=self.assets_dir,
            )
        )
        self.page_tasks.append(task)
        logger.info("PageManager: Opening page `{:}` on port http://127.0.0.1:{:}".format(name, port))

    def restart(self):
        self.need_restart = True

    def start(self, name: str, *, port: int = 0):
        while True:
            self.open_page(name, port=port)
            self.loop.run_until_complete(self.check_page_count())
            if not self.need_restart:
                break
            logger.info("PageManager: Restarting...")
            # TODO: port should be reused, but port already in use
            port = get_free_port()
            self.need_restart = False
        self.loop.close()

    async def close(self):
        # TODO
        for p in self.state.running_pages:
            p.window_destroy()
