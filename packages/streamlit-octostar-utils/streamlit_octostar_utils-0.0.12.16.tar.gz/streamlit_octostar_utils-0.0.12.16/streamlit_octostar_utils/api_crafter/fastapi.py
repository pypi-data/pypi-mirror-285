import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Union, List, Optional, Literal
from io import BytesIO
import zipfile
import json
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import ast
import uuid
import itertools
from concurrent.futures import ThreadPoolExecutor
from sortedcontainers import SortedDict
import traceback
import logging

MAX_ERROR_MESSAGE_BYTES = 256
MAX_ERROR_TRACEBACK_BYTES = 10240
DEFAULT_PROCESSOR_SUFFIX = 'main'

class CommonParsers(object):
    async def parse_form_list(form_data: str,
                              format=Literal['csv', 'python']) -> Optional[List[str]]:
        try:
            if not form_data:
                return None
            if format == 'csv':
                return form_data.split(',')
            elif format == 'python':
                return ast.literal_eval(form_data)
        except:
            raise ValidationError("Parsing failed in parse_from_list!")

class Route(object):
    pass

class CommonModels(object):
    class OKResponseModel(BaseModel):
        message: str = "OK"
        status: str = "success"
        
    class DataResponseModel(BaseModel):
        data: Union[list, dict]
        status: str = "success"

    class ZipResponseModel(object):
        class Element(object):
            def __init__(self, file: bytes, path: str, filename: str, json: dict):
                self.file = file
                self.path = path
                self.filename = filename
                self.json = json
            
        def __init__(self, elements: List[Element], paths: Optional[List[str]] = None, filename: Optional[str] = None, status: str = "success"):
            self.elements = elements
            self.paths = paths
            self.status = status
            self.filename = filename
        
        def get(self):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for element in self.elements: 
                    file_name = f"{element.path}/{element.filename}"
                    zip_file.writestr(file_name, element.file)
                    json_name = f"{element.path}/{element.filename}.dict"
                    zip_file.writestr(json_name, json.dumps(element.json, indent=4))
                for path in self.paths:
                    zip_file.writestr(path + "/", '')
                zip_file.writestr('response.dict', json.dumps({'status': self.status}, indent=4))
            zip_buffer.seek(0)
            headers = {}
            headers['Content-Disposition'] = 'attachment;'
            filename = self.filename or (str(uuid.uuid4()) + ".zip")
            headers['Content-Disposition'] += f' filename="{filename}"'
            return StreamingResponse(zip_buffer, media_type='application/zip', headers=headers)

class DefaultErrorRoute(Route):
    error_responses = {
        500: {
            "description": "Generic Server Error",
            "content": {
                "application/json": {
                    "example": {"message": "Something unexpected went wrong!", "status": "error"}
                }
            }
        },
        501: {
            "description": "Not Implemented",
            "content": {
                "application/json": {
                    "example": {"message": "This method (with these parameters) is not implemented!", "status": "error"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"message": "These two lists must have the same length!", "status": "error"}
                }
            }            
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {"message": "Validation error on 0 -> filename!", "status": "error"}
                }
            }            
        },        
    }
    
    def format_error(exc):
        '''Generic Error Handler'''
        status_code = 500
        if isinstance(exc, StarletteHTTPException):
            status_code = exc.status_code
        elif isinstance(exc, NotImplementedError):
            status_code = 501
        elif isinstance(exc, AssertionError):
            status_code = 400
        elif isinstance(exc, ValidationError) or isinstance(exc, RequestValidationError):
            status_code = 422
        try:
            message = exc.message
        except:
            message = str(exc)
        if len(message) > MAX_ERROR_MESSAGE_BYTES:
            message = message[-MAX_ERROR_MESSAGE_BYTES:]
        tcbk = traceback.format_exception(exc)
        if len(tcbk) > MAX_ERROR_TRACEBACK_BYTES:
            tcbk = tcbk[-MAX_ERROR_TRACEBACK_BYTES:]
        return JSONResponse(
            status_code=status_code,
            content={"message": message, 'status': 'error', 'traceback': tcbk}
        )
    
    async def handle_error(request: Request, exc: Exception):
        return DefaultErrorRoute.format_error(exc)
    
    def add_default_exceptions_handler(fs_app):
        fs_app.add_exception_handler(RequestValidationError, DefaultErrorRoute.handle_error)
        fs_app.add_exception_handler(StarletteHTTPException, DefaultErrorRoute.handle_error)
        fs_app.add_exception_handler(Exception, DefaultErrorRoute.handle_error)
    
class RequestCancelledMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        queue = asyncio.Queue()
        async def message_poller(sentinel, handler_task):
            nonlocal queue
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    handler_task.cancel()
                    return sentinel
                await queue.put(message)
        sentinel = object()
        handler_task = asyncio.create_task(self.app(scope, queue.get, send))
        asyncio.create_task(message_poller(sentinel, handler_task))
        try:
            return await handler_task
        except asyncio.CancelledError:
            print("Cancelling request due to disconnect")

class RoutesQueue(object):
    class RouteTask(object):
        def __init__(self, fn, timeout):
            self.fn = fn
            self.timeout = timeout
            self.future = asyncio.Future()

    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.queues = SortedDict()  # priority-sorted list of round-robined lists of fifo lists
        self.queue_indices = {}
        self.lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
        self.kill_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    async def does_route_exist(self, route_name):
        async with self.lock:
            all_route_names = itertools.chain(*[list(q.keys()) for q in self.queues.values()])
            exists = route_name in all_route_names
            logging.debug(f"Checking if route exists: {route_name} - {exists}")
            return exists

    async def register_route(self, route_name, route_priority):
        if await self.does_route_exist(route_name):
            raise AttributeError("Route already exists!")
        async with self.lock:
            if route_priority not in self.queues:
                self.queues[route_priority] = {}
                self.queue_indices[route_priority] = 0
            self.queues[route_priority][route_name] = []
            logging.debug(f"Registered route: {route_name} with priority: {route_priority}")

    async def add_task(self, route_name, task, timeout=60*15):
        task = RoutesQueue.RouteTask(task, timeout)
        if not await self.does_route_exist(route_name):
            raise ValueError(f"Route {route_name} does not exist.")
        async with self.lock:
            self.queues[self.get_priority(route_name)][route_name].append(task)
            logging.debug(f"Added task to route: {route_name} with timeout: {timeout}")
        return await task.future

    def get_priority(self, route_name):
        for priority, routes in self.queues.items():
            if route_name in routes:
                return priority
        raise ValueError(f"Route {route_name} not found.")

    async def get_next_task(self):
        async with self.lock:
            for priority in self.queues.keys():
                if any(self.queues[priority][route_name] for route_name in self.queues[priority].keys()):
                    route_names = list(self.queues[priority].keys())
                    for _ in range(len(route_names)):
                        idx = self.queue_indices[priority]
                        self.queue_indices[priority] = (idx + 1) % len(self.queues[priority])
                        if len(self.queues[priority][route_names[idx]]) > 0:
                            next_task = self.queues[priority][route_names[idx]].pop(0)
                            logging.debug(f"Selected next task from route: {route_names[idx]} with priority: {priority}")
                            return next_task
            return None

    async def worker(self, i):
        logging.debug(f"Worker {i} started")
        while not self.kill_event.is_set():
            task = await self.get_next_task()
            if task is None:
                await asyncio.sleep(0.5)
                continue
            await self.semaphore.acquire()
            logging.debug(f"Worker {i} acquired semaphore for task: {task}")
            loop_future = asyncio.get_event_loop().run_in_executor(self.executor, task.fn)
            try:
                result = await asyncio.wait_for(loop_future, timeout=task.timeout)
                task.future.set_result(result)
            except asyncio.TimeoutError:
                task.future.set_exception(asyncio.TimeoutError(f"Task {task} exceeded timeout of {task.timeout} seconds"))
            except BaseException as e:
                task.future.set_exception(e)
            finally:
                logging.debug(f"Worker {i} released lock")
                self.semaphore.release()

    def start_worker(self):
        for i in range(self.max_workers):
            asyncio.get_event_loop().create_task(self.worker(i))
            logging.debug(f"Started worker {i}")

    async def shutdown(self):
        self.kill_event.set()
        logging.debug("Shutdown initiated, waiting for workers to complete")
        await self.semaphore.acquire(self.executor._max_workers)
        self.executor.shutdown(wait=True)
        logging.debug("All workers completed, executor shutdown")
        
class RouteContextManager:
    def __init__(self, route_name, route_priority, routes_queue):
        self.route_name = route_name
        self.route_priority = route_priority
        self.routes_queue = routes_queue
        
    async def __aenter__(self):
        try:
            await self.routes_queue.register_route(self.route_name, self.route_priority)
        except AttributeError:
            pass
        return self

    async def run_task(self, task_fn):
        return await self.routes_queue.add_task(self.route_name, task_fn)

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False