from octostar.client import make_client, UserContext, User
from functools import wraps
from streamlit_octostar_research.desktop import whoami
from streamlit.runtime.scriptrunner import get_script_run_ctx
import hashlib
import streamlit as st

def impersonating_running_user(**kwargs):
    client = as_running_user(**kwargs).user.client
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['client'] = client
            return func(*args, **kwargs)
        return wrapper
    return decorator

def as_running_user(force_refresh=False):
    script_ctx = get_script_run_ctx()
    internal_st_key = "__run_user"
    if internal_st_key not in st.session_state:
        st.session_state[internal_st_key] = dict()
    prev_run_id = st.session_state[internal_st_key].get('prev_run_id')
    prev_user = st.session_state[internal_st_key].get('prev_user')
    is_first_time = False
    if prev_run_id != id(script_ctx.script_requests): # this changes at every st rerun
        is_first_time = True
    st.session_state[internal_st_key]['prev_run_id'] = id(script_ctx.script_requests)
    if not is_first_time and not force_refresh and prev_user:
        return UserContext(prev_user)
    running_user = whoami()
    if not running_user:
        if prev_user:
            return UserContext(prev_user)
        else:
            st.stop()
    running_user_hash = int(hashlib.md5(running_user['os_jwt'].encode('utf-8')).hexdigest(), 16)
    if not prev_user or hash(prev_user) != running_user_hash:
        client = make_client(fixed_jwt=running_user['os_jwt'])
        user = User(client)
        st.session_state[internal_st_key]['prev_user'] = user
    return UserContext(user)