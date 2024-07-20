import os
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
from dateutil.parser import parse
from datetime import datetime, date
import json
import yaml
from typing import List, Dict, Tuple, Union, Optional, Callable, Any, Literal
try:
    from .date_formatter import python_to_luxon_format
    from .utility_functions import allow_top_navigation
except:
    from date_formatter import python_to_luxon_format
    from utility_functions import allow_top_navigation
# from streamlit_callback import register_callback


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

COMPONENT_NAME = "streamlit_datatables_net"

if _RELEASE:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        COMPONENT_NAME, path=build_dir)

else:
    _component_func = components.declare_component(
        COMPONENT_NAME,
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.


# @st.cache_data(show_spinner=False)
def get_datatables_net_config(dt_config: str) -> Tuple[str, list[str], list[str]]:
    try:
        file_path = "config_datatables_net.yaml"
        with open(file_path, "r") as f:
            config_datatables_net: Dict = yaml.safe_load(f)
        config: Dict = config_datatables_net.get(dt_config)
        return config.get("class_name"), config.get("js_scripts"), config.get("stylesheets")
    except:
        return None, None, None


def df_to_denormalized_dict(df: pd.DataFrame, sep="."):
    """ The opposite of json_normalize. """
    result = []
    for idx, row in df.iterrows():
        parsed_row = {}
        for col_label, v in row.items():
            keys = col_label.split(sep)

            current = parsed_row
            for i, k in enumerate(keys):
                if i == len(keys)-1:
                    current[k] = v
                else:
                    if k not in current.keys():
                        current[k] = {}
                    current = current[k]
        result.append(parsed_row)
    return result


def apply_date_formatting(df: pd.DataFrame, date_format='%-m/%d/%Y', denormalize: bool = False):
    """Identify datetime columns and apply the desired format"""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime(date_format)
        elif df[col].apply(lambda x: isinstance(x, date)).all():
            df[col] = df[col].apply(lambda x: x.strftime(date_format))

    return df


def st_datatable(data: pd.DataFrame | list[dict], column_order: List[str] = None, props: Dict = None, dt_config: str = "default", table_id: str = None, class_name: str = None, js_scripts: List[str] = None, stylesheets: List[str] = None, disabled: bool = False, enable_top_navigation: bool = False, date_format: str = None, is_datetime: bool = False, export_file_name: str = None, on_select: Optional[Union[Literal["ignore"], Literal["rerun"], Callable]] = "rerun", on_change: Optional[Callable] = None, on_click: Optional[Callable] = None, args: Optional[Tuple[Any, ...]] = None,
                 kwargs: Optional[Dict[str, Any]] = None, key=None):
    """Create a new instance of "st_datatable".

    Parameters
    ----------
    data: pandas.DataFrame, list(dict)
        The data to display.
    column_order: List[str]
        Specifies the display order of columns. This also affects which columns are visible. For example, column_order=("col2", "col1") will display 'col2' first, followed by 'col1', and will hide all other non-index columns. If None (default), the order is inherited from the original data structure.
    props: dict
        The props to set the data attributes and configuration options for the datatable.
    dt_config: str
        An optional parameter to use a YAML configuration file to specify the class_name, js_scripts, and stylesheets.  The YAML file should be named config_datatables_net.yaml and follow this structure:

    default: 
        js_scripts:\n
            -  https://cdn.datatables.net/v/dt/jq-3.7.0/jszip-3.10.1/dt-1.13.6/b-2.4.1/b-html5-2.4.1/b-print-2.4.1/r-2.5.0/datatables.min.js\n
        stylesheets:\n
            - https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css\n
        class_name: compact row-border hover nowrap\n

    class_name: str or None
        An optional str of class names to apply to the datatable (e.g., 'compact hover').
    js_scripts: list or None
        An optional list of urls for javascripts to apply to the datatable.
    stylesheets: list or None
        An optional list of urls for stylesheets to apply to the datatable.
    disabled:
        An optional boolean, which disables the component and sets the component value to an empty dict if set to True. The default is False.
    enable_top_navigation:
        An optional boolean, which allows opening html links using target="top" or target="parent". The default is False.
    date_format:
        An optional string which will display datetime fields in the specified date format (e.g. '%m/%d/%Y'). Datetime fields should be provided in the specfied string. Alternatively, you may also enable the is_datetime option to convert datetime fields to the specified date_format.  The default is None.
    is_datetime:
        An optional boolean indicating date/time fields are of Python datetime, date or time types and should be used to convert to the date_format string.  The default is False.
    export_file_name:
        An optional string to use for file name of downloaded files if using Datatable export buttons (e.g, Excel, csv).  Default value is 'datatable'.
    on_change:
        An optional callback invoked when the datatable is clicked.  Note, it does does support args and kwargs.
    on_click:
        This feature is disabled until further notice.
    on_select : "ignore" or "rerun" or callable
            How the datatable should respond to user selection events. This
            controls whether or not the datatable behaves like an input widget.
            ``on_select`` can be one of the following:

            - ``"rerun"`` (default): Streamlit will rerun the app when the user selects
              rows in the datatable. In this case, ``st_datatable``
              will return the selection data as a dictionary.

            - ``"ignore"``: Streamlit will not react to any selection
              events in the datatable. The datatable will not behave like an
              input widget.            

            - A ``callable``: Streamlit will rerun the app and execute the
              ``callable`` as a callback function before the rest of the app.
              In this case, ``st_datatable`` will return the selection data
              as a dictionary.

    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    dict
        A dict with details of the datatable row clicked by the user.

        Example response:
        {
            "event_type": "row_click",
            "data": {
                "id": "1",
                "name": "Tiger Nixon",
                "position": "System Architect",
                "salary": 320800,
                "start_date": "datetime.datetime(2012, 4, 25, 0, 0)",
                "office": "Edinburgh",
                "extn": "5421",
                "address": {
                "street": "123 Main St",
                "city": "Anytown"
                }
            },
            "dataset": {},
            "classList": {
                "0": "sorting_1"
            },
            "click_id" "fRVZN3uz60"
        }


    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    if props is None:
        props = {}

    if class_name is None and js_scripts is None and stylesheets is None:
        class_name, js_scripts, stylesheets = get_datatables_net_config(
            dt_config)

    if column_order:
        props["columns"] = [{"data": column, "title": column, "name": column}
                            for column in column_order]

    if isinstance(data, pd.DataFrame):
        if date_format is not None and is_datetime:
            df = apply_date_formatting(data, date_format=date_format)
            df_dict = df.to_dict(orient='records')
            props["data"] = df_dict
        else:
            props["data"] = json.loads(data.to_json(orient="records"))

        if "columns" not in props:
            props["columns"] = [{"data": column, "title": column, "name": column}
                                for column in data.columns]
    elif isinstance(data, list):
        df_dict = None
        if date_format is not None and is_datetime:
            df = pd.json_normalize(data)
            df = apply_date_formatting(df, date_format=date_format)
            df_dict = df_to_denormalized_dict(df)
            data = df_dict
        props["data"] = data
        if "columns" not in props and data:
            if df_dict is None:
                df = pd.json_normalize(data)
                df_dict = df.to_dict(orient="records")
            columns = list(df_dict[0].keys())
            props["columns"] = [{"data": column, "title": column, "name": column}
                                for column in columns]
        elif "columns" not in props:
            st.warning("Unable to display datatable: data is invalid")
            return {}
    else:
        st.warning("Unable to display datatable: data is invalid")
        return {}

    luxon_date_format = None
    if date_format is not None:
        luxon_date_format = python_to_luxon_format(date_format)

    match on_select:
        case "ignore":
            disabled = True
            on_select = None
        case "rerun":
            disabled = False
            on_select = None
        case func if callable(func):
            disabled = False
            on_change = on_select

    component_value = _component_func(
        props=props, table_id=table_id, class_name=class_name, js_scripts=js_scripts, stylesheets=stylesheets, key=key, on_change=on_change, disabled=disabled, date_format=luxon_date_format, export_file_name=export_file_name, default=None)

    if enable_top_navigation:
        iframe_title = f"{COMPONENT_NAME}.{COMPONENT_NAME}"
        if __name__ == "__main__":
            iframe_title = f"__init__.{COMPONENT_NAME}"
        allow_top_navigation(iframe_title)

    if component_value and "data" in component_value and date_format is not None:
        for key, value in component_value["data"].items():
            try:
                component_value["data"][key] = datetime.strptime(
                    value, date_format)
            except:
                continue

    # if on_click is not None and component_value:
    #     if args is None:
    #         args = ()
    #     if kwargs is None:
    #         kwargs = {}
    #     on_click(*args, **kwargs)

    #  Including for future
    # if on_click is not None:
    #     if key is None:
    #         st.error(
    #             "You must pass a key if you want to use the on_click callback for st_datatable")
    #     else:
    #         args = args if args is not None else []
    #         kwargs = kwargs if kwargs is not None else {}
    #         register_callback(key, on_click, *args, **kwargs)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.

    return component_value


def my_on_click_function(key=None):
    print("You clicked me!", st.session_state["example_1"])


if not _RELEASE:
    st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

    col_l, content_column, col_r = st.columns([1, 10, 1])
    with content_column:
        with st.container(border=True):
            st.write("Example: List of dictionaries")
            dt_container = st.container()
            with st.expander("Code"):
                with st.echo():
                    data = [
                        {
                            "id": "1",
                            "name": "Tiger Nixon",
                            "position": "System Architect",
                            "salary": 320800,
                            "start_date": "2012/04/25",
                            "office": "Edinburgh",
                            "extn": "5421",
                            "address": {"street": "123 Main St", "city": "Anytown"}
                        },
                        {
                            "id": "2",
                            "name": "Garrett Summers",
                            "position": "Accountant",
                            "salary": 170750,
                            "start_date": "2011/07/25",
                            "office": "Tokyo",
                            "extn": "8422",
                            "address": {"street": "456 Main St", "city": "Anytown"}
                        },
                        {
                            "id": "3",
                            "name": "Clark Kent",
                            "position": "Reporter",
                            "salary": 170750,
                            "start_date": "2009/09/30",
                            "office": "Gotham",
                            "extn": "8523",
                            "address": {"street": "789 Main St", "city": "Anytown"}
                        },
                    ]
                    column_order = ["name", "position", "start_date", "salary",
                                    "start_date", "office", "extn", "address.street", "address.city"]

                    props = {}
                    props["lengthChange"] = False
                    # props["responsive"] = True
                    # props["scrollX"] = True
                    props["stateSave"] = True
                    props["stateDuration"] = -1
                    props["layout"] = {
                        "top2Start":  {"buttons": ['excel']},
                        "topStart": {"buttons": ['pageLength']},
                        'topEnd': 'search',
                        'bottomStart': 'info',
                        'bottomEnd': 'paging'
                    }
                    for row in data:
                        row["start_date"] = (parse(row["start_date"])).date()

                    big_data = []
                    for i in range(10):
                        big_data.extend(data)

                    with dt_container:
                        dt_response = st_datatable(
                            big_data, column_order=column_order, props=props, table_id="example_1", key="example_1", dt_config="default", date_format="%m/%d/%Y", is_datetime=True, enable_top_navigation=True, export_file_name="Example 1", on_select=my_on_click_function)
                        st.write(dt_response)
        with st.container(border=True):
            st.write("Example: List of dictionaries with columns property")
            dt_container = st.container()
            with st.expander("Code"):
                with st.echo():
                    for item in data:
                        item["edit_link"] = "https://google.com"

                    columns = [
                        {"data": "name", "title": "Name"},
                        {"data": "start_date", "title": "Start Date"},
                        {"data": "office", "title": "Office"},
                        {"data": "salary", "title": "Salary",
                            "render": ['number', ',', '.', 0, '$']},
                        {"data": "", "title": "Actions",
                            "column_type": "actions", "actions": ["view", "edit", "delete", "pdf", "download"]},
                        {"data": "", "title": "Open", "column_type": "url",
                            "url": "https://google.com", "display_text": "Google"},
                        {"data": "edit_link", "title": "Edit Link"},
                        {"data": "extn", "title": "extn", "className": "my_class"},
                    ]
                    props = {}
                    props["columns"] = columns

                    with dt_container:
                        on_select = st.selectbox("on_select", options=[
                            "ignore", "rerun", "callable"])
                        if on_select == "callable":
                            on_select = my_on_click_function

                        dt_response = st_datatable(
                            data, props=props, table_id="example_1b", key="example_1b", enable_top_navigation=True, date_format="%b %d %Y", is_datetime=True, on_select=on_select)
                        st.write(dt_response)

        with st.container(border=True):
            st.write("Example: Pandas Dataframe")
            dt_container = st.container()
            with st.expander("Code"):
                with st.echo():
                    data = pd.DataFrame(
                        {
                            "name": ["Roadmap", "Extras", "Issues"],
                            "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
                            'date1': ['2021-11-01', '2021-02-01', '2022-01-01']
                        }
                    )
                    with dt_container:
                        dt_response = st_datatable(
                            data, key="example_2", date_format='%Y-%b-%d', on_select="ignore")
                        st.write(dt_response)

        with st.container(border=True):
            st.write("Example: Empty list with columns property")
            dt_container = st.container()
            with st.expander("Code"):
                with st.echo():
                    data = []
                    props = {}
                    props["columns"] = [{"data": "name", "title": "name"}, {
                        "data": "url", "title": "url"}]
                    with dt_container:
                        st_datatable(data, props=props, key="example_3")

        with st.container(border=True):
            st.write("Example: Invalid data")
            dt_container = st.container()
            with st.expander("Code"):
                with st.echo():
                    data = None
                    with dt_container:
                        st_datatable(data, key="example_4")

        st.write(st.session_state)
