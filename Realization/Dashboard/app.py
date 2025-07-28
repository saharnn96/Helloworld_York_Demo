import dash
from dash import dcc, html, Input, Output, State, ctx
import plotly.graph_objs as go
import redis
import json
import time
import logging
import os

# Setup logging
logger = logging.getLogger("dashboard")

# Custom Redis Log Handler
class RedisLogHandler(logging.Handler):
    def __init__(self, redis_client, key_name="dashboard:logs", max_logs=100):
        super().__init__()
        self.redis_client = redis_client
        self.key_name = key_name
        self.max_logs = max_logs
    
    def emit(self, record):
        try:
            # Format the log record
            log_message = self.format(record)
            # Add timestamp
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
            formatted_message = f"[{timestamp}] {log_message}"
            
            # Push to Redis list
            self.redis_client.lpush(self.key_name, formatted_message)
            # Trim list to keep only the latest logs
            self.redis_client.ltrim(self.key_name, 0, self.max_logs - 1)
        except Exception:
            # Don't let logging errors crash the app
            pass

r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)

# Add Redis handler to logger
redis_handler = RedisLogHandler(r, "dashboard:logs")
redis_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
redis_handler.setFormatter(formatter)
logger.addHandler(redis_handler)

app = dash.Dash(__name__)
app.title = "RoboSAPIENS Adaptive Platform Dashboard"

# Log application startup
logger.info("Dashboard application starting up")
logger.info("Redis log handler configured for dashboard:logs")

app.layout = html.Div([
    # Header Section
    html.Div([
        html.H1("RoboSAPIENS Adaptive Platform Dashboard", 
                style={
                    'textAlign': 'center', 
                    'color': '#2c3e50',
                    'marginBottom': '10px',
                    'fontWeight': '300',
                    'fontSize': '2.5rem'
                }),
        html.P("Real-time monitoring and control of distributed components", 
               style={
                   'textAlign': 'center', 
                   'color': '#7f8c8d',
                   'marginBottom': '30px',
                   'fontSize': '1.1rem'
               })
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '40px 20px',
        'marginBottom': '30px',
        'borderRadius': '0 0 15px 15px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
    }),

    # Gantt Chart Section
    html.Div([
        html.H3("Components Activation Timeline", 
                style={
                    'color': '#2c3e50',
                    'marginBottom': '20px',
                    'fontWeight': '400'
                }),
        dcc.Graph(id="gantt-chart", style={'height': '400px'})
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '25px',
        'marginBottom': '30px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.08)',
        'border': '1px solid #e9ecef'
    }),

    # Device Cards Section
    html.Div([
        html.Div([
            html.H3("Device Status", 
                    style={
                        'color': '#2c3e50',
                        'marginBottom': '20px',
                        'fontWeight': '400',
                        'display': 'inline-block'
                    }),
            html.Button('+ Add Device', 
                       id='add-processor-btn', 
                       style={
                           'backgroundColor': '#3498db',
                           'color': 'white',
                           'border': 'none',
                           'padding': '8px 16px',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'fontSize': '14px',
                           'float': 'right',
                           'transition': 'all 0.3s ease'
                       })
        ], style={'marginBottom': '20px'}),
        html.Div(id='processor-cards', 
                style={
                    'display': 'grid', 
                    'gridTemplateColumns': 'repeat(auto-fill, minmax(280px, 1fr))', 
                    'gap': '20px'
                })
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '25px',
        'marginBottom': '30px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.08)',
        'border': '1px solid #e9ecef'
    }),

    # Logs Section
    html.Div([
        html.Div([
            html.H3("System Logs", 
                    style={
                        'color': '#2c3e50',
                        'marginBottom': '20px',
                        'fontWeight': '400',
                        'display': 'inline-block'
                    }),
            html.Button('🔄 Refresh Log Sources', 
                       id='refresh-log-sources-btn',
                       style={
                           'backgroundColor': '#17a2b8',
                           'color': 'white',
                           'border': 'none',
                           'padding': '8px 16px',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'fontSize': '14px',
                           'float': 'right',
                           'transition': 'all 0.3s ease'
                       })
        ], style={'marginBottom': '15px'}),
        
        html.Div([
            html.Label("Select Log Sources:", style={
                'fontWeight': '600',
                'color': '#2c3e50',
                'marginBottom': '10px',
                'display': 'block'
            }),
            dcc.Checklist(
                id='log-sources-checklist',
                options=[],
                value=[],
                style={
                    'marginBottom': '15px'
                },
                inputStyle={
                    'marginRight': '8px'
                },
                labelStyle={
                    'display': 'inline-block',
                    'marginRight': '15px',
                    'marginBottom': '5px',
                    'color': '#34495e',
                    'fontSize': '14px'
                }
            )
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '15px',
            'borderRadius': '5px',
            'border': '1px solid #dee2e6',
            'marginBottom': '15px'
        }),
        
        html.Pre(id='live-log', 
                style={
                    'height': '300px', 
                    'overflowY': 'auto', 
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '5px',
                    'padding': '15px',
                    'fontFamily': 'Monaco, Consolas, "Courier New", monospace',
                    'fontSize': '12px',
                    'lineHeight': '1.4'
                })
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '25px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.08)',
        'border': '1px solid #e9ecef'
    }),

    # Intervals
    dcc.Interval(id='interval-gantt', interval=1000, n_intervals=0),
    dcc.Interval(id='interval-redis', interval=2000, n_intervals=0),
    dcc.Interval(id='interval-log', interval=1000, n_intervals=0),
    dcc.Interval(id='interval-log-sources', interval=5000, n_intervals=0)  # Check for new sources every 5 seconds
], style={
    'backgroundColor': '#f5f6fa',
    'minHeight': '100vh',
    'padding': '0',
    'margin': '0',
    'fontFamily': '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif'
})

@app.callback(
    Output("gantt-chart", "figure"),
    Input("interval-gantt", "n_intervals")
)
def update_gantt(_):
    fig = go.Figure()
    phase_colors = {
        "Monitor": "#1f77b4",
        "Analysis": "#2ca02c",
        "Plan": "#ff7f0e",
        "Execute": "#d62728",
        "Legitimate": "#9467bd",
        "Trustworthiness": "#8c564b"
    }
    device_names = r.lrange('devices:list', 0, -1)
    now = time.time()
    for device in device_names:
        nodes = r.lrange(f"devices:{device}:nodes", 0, -1)
        for node in nodes:
            execution_time = r.get(f"{node}:execution_time")
            start_execution = r.get(f"{node}:start_execution")
            try:
                if execution_time and start_execution:
                    start_exec = float(start_execution)
                    if now - start_exec <= 10:
                        exec_time = float(execution_time)
                        fig.add_trace(go.Bar(
                            name=f"{node}",
                            x=[exec_time],
                            y=[f"{node}"],
                            base=start_execution,
                            orientation="h",
                            marker=dict(color=phase_colors.get(node, "#7f7f7f"))
                        ))
            except ValueError:
                continue

    fig.update_layout(
        title={
            'text': "MAPE-K Phases Timeline (Last 10 Seconds)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50'}
        },
        xaxis_title="Time (seconds)",
        yaxis_title="Components",
        barmode="overlay",
        template="plotly_white",
        showlegend=False,
        plot_bgcolor="rgba(248, 249, 250, 1)",
        paper_bgcolor="rgba(255, 255, 255, 1)",
        font={'family': '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif'},
        margin={'l': 80, 'r': 20, 't': 60, 'b': 60}
    )
    return fig

@app.callback(
    Output("processor-cards", "children"),
    Input("interval-redis", "n_intervals")
)
def update_processors(_):
    import time
    device_names = r.lrange('devices:list', 0, -1)  # List of device names
    logger.debug(f"Devices in Redis: {device_names}")
    cards = []
    for device in device_names:
        heartbeat = r.get(f"devices:{device}:heartbeat")
        logger.debug(f"{device} heartbeat: {heartbeat}")
        try:
            if heartbeat:
                now = time.time()
                heartbeat_val = float(heartbeat)
                logger.debug(f"{device} now: {now}, heartbeat_val: {heartbeat_val}, diff: {now - heartbeat_val}")
                if now - heartbeat_val < 10:
                    online_status = "🟢 Online"
                    online_color = "green"
                else:
                    online_status = "🔴 Offline"
                    online_color = "red"
            else:
                online_status = "🔴 Offline (no heartbeat)"
                online_color = "red"
        except Exception as e:
            logger.warning(f"Exception for {device} heartbeat: {e}")
            online_status = "Unknown"
            online_color = "gray"

        # Get components for this device
        nodes = r.lrange(f"devices:{device}:nodes", 0, -1)
        logger.debug(f"{device} nodes: {nodes}")
        running_count = 0
        comp_list = []
        for node in nodes:
            status_key = f"devices:{device}:{node}:status"
            status = r.get(status_key)
            logger.debug(f"{device} component {node} status: {status}")
            if status == "running":
                status_text = "🟢 Running"
                status_color = "green"
                running_count += 1
            elif status == "exited":
                status_text = "⏸️ Stopped"
                status_color = "orange"
            else:
                status_text = "⚪ Removed"
                status_color = "gray"
            comp_list.append(html.Div([
                html.Div([
                    html.Span(node, style={
                        'fontWeight': '600', 
                        'color': '#2c3e50',
                        'fontSize': '14px',
                        'marginLeft': '8px',
                        'display': 'inline-block',  # Required for width to apply
                        'width': '80px',            # Fixed width (adjust as needed)
                        'textAlign': 'left',        # Optional: align text inside the fixed box
                        'overflow': 'hidden',       # Optional: hide overflow if text too long
                        'whiteSpace': 'nowrap',     # Optional: prevent wrapping
                        
                    }),
                    html.Span(status_text, style={
                        'color': status_color, 
                        'fontWeight': '500',
                        'fontSize': '12px',
                        'display': 'inline-block',  # Required for width to apply
                        'width': '80px',            # Fixed width (adjust as neede
                        'marginLeft': '8px',
                        'marginRight': '8px'
                    }),
                    html.Button('▶️', 
                               id={'type': 'run-comp-btn', 'proc': device, 'comp': node},
                               style={
                                   'backgroundColor': '#27ae60',
                                   'color': 'white',
                                   'border': 'none',
                                   'borderRadius': '4px',
                                   'padding': '4px 8px',
                                   'marginRight': '4px',
                                   'cursor': 'pointer',
                                   'fontSize': '12px'
                               }),
                    html.Button('⏸️', 
                               id={'type': 'pause-comp-btn', 'proc': device, 'comp': node},
                               style={
                                   'backgroundColor': '#f39c12',
                                   'color': 'white',
                                   'border': 'none',
                                   'borderRadius': '4px',
                                   'padding': '4px 8px',
                                   'marginRight': '4px',
                                   'cursor': 'pointer',
                                   'fontSize': '12px'
                               }),
                    html.Button('❌', 
                               id={'type': 'del-comp-btn', 'proc': device, 'comp': node}, 
                               disabled=True,
                               style={
                                   'backgroundColor': '#bdc3c7',
                                   'color': 'white',
                                   'border': 'none',
                                   'borderRadius': '4px',
                                   'padding': '4px 8px',
                                   'cursor': 'not-allowed',
                                   'fontSize': '12px'
                               })
                ], style={'marginBottom': '8px'}),
            ], style={
                'backgroundColor': '#f8f9fa',
                'border': '1px solid #e9ecef',
                'borderRadius': '8px',
                'padding': '12px',
                'marginBottom': '8px',
                'transition': 'all 0.2s ease'
            }))

        cards.append(html.Div([
            # Device Header
            html.Div([
                html.H4(device, style={
                    'margin': '0',
                    'color': '#2c3e50',
                    'fontSize': '18px',
                    'fontWeight': '600'
                }),
                html.Button('❌', 
                           id={'type': 'del-proc-btn', 'proc': device}, 
                           disabled=True,
                           style={
                               'backgroundColor': '#bdc3c7',
                               'color': 'white',
                               'border': 'none',
                               'borderRadius': '4px',
                               'padding': '4px 8px',
                               'cursor': 'not-allowed',
                               'fontSize': '12px'
                           })
            ], style={
                'display': 'flex', 
                'justifyContent': 'space-between', 
                'alignItems': 'center',
                'marginBottom': '15px',
                'paddingBottom': '10px',
                'borderBottom': '2px solid #ecf0f1'
            }),
            
            # Device Status
            html.Div([
                html.Div([
                    html.Span("Status: ", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                    html.Span(online_status, style={
                        'color': online_color, 
                        'fontWeight': '600',
                        'fontSize': '14px'
                    }),
                    html.Span("Active: ", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                    html.Span(f"{running_count}/{len(nodes)}", style={
                        'fontWeight': '600',
                        'color': '#2c3e50',
                        'leftMargin': '8px',
                        'fontSize': '14px'
                    })
                ], style={'marginBottom': '8px'}),
            ], style={'marginBottom': '20px'}),
            
            # Components List
            html.Div([
                html.H5("Components", style={
                    'margin': '0 0 10px 0',
                    'color': '#34495e',
                    'fontSize': '14px',
                    'fontWeight': '600'
                }),
                html.Div(comp_list)
            ]),
            
            # # Add Component Button
            # html.Button('+ Add Component', 
            #            id={'type': 'add-comp-btn', 'proc': device},
            #            style={
            #                'width': '100%',
            #                'backgroundColor': '#3498db',
            #                'color': 'white',
            #                'border': 'none',
            #                'borderRadius': '6px',
            #                'padding': '10px',
            #                'marginTop': '15px',
            #                'cursor': 'pointer',
            #                'fontSize': '14px',
            #                'fontWeight': '500',
            #                'transition': 'all 0.3s ease'
            #            })
        ], style={
            'backgroundColor': '#ffffff',
            'border': '1px solid #e9ecef',
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.1)',
            'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
            'minHeight': '300px'
        }))
    return cards

@app.callback(
    Output('interval-redis', 'n_intervals'),
    Input('add-processor-btn', 'n_clicks'),
    Input({'type': 'del-proc-btn', 'proc': dash.ALL}, 'n_clicks'),
    Input({'type': 'add-comp-btn', 'proc': dash.ALL}, 'n_clicks'),
    Input({'type': 'del-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'n_clicks'),
    Input({'type': 'run-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'n_clicks'),
    Input({'type': 'pause-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'n_clicks'),
    State({'type': 'del-proc-btn', 'proc': dash.ALL}, 'id'),
    State({'type': 'add-comp-btn', 'proc': dash.ALL}, 'id'),
    State({'type': 'del-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'id'),
    State({'type': 'run-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'id'),
    State({'type': 'pause-comp-btn', 'proc': dash.ALL, 'comp': dash.ALL}, 'id'),
    prevent_initial_call=True
)
def handle_actions(add_proc_clicks, del_proc_clicks, add_comp_clicks, del_comp_clicks, run_clicks, pause_clicks,
                   del_proc_ids, add_comp_ids, del_comp_ids, run_ids, pause_ids):
    logger.debug(f"handle_actions triggered_id: {ctx.triggered_id}")
    # All actions are deactivated for now
    if ctx.triggered_id == 'add-processor-btn':
        device_names = r.lrange('devices', 0, -1)
        logger.debug(f"Devices before add: {device_names}")
        new_device = f"Device{len(device_names) + 1}"
        logger.debug(f"Added device: {new_device}")
    elif isinstance(ctx.triggered_id, dict):
        tid = ctx.triggered_id
        logger.debug(f"handle_actions tid: {tid}")
        if tid['type'] == 'del-proc-btn':
            logger.debug(f"Delete device action is deactivated.")
            pass
        elif tid['type'] == 'add-comp-btn':
            device = tid['proc']
            comps = r.lrange(f'{device}:components', 0, -1)
            logger.debug(f"Adding component to {device}, current comps: {comps}")
            comp_name = f"Component{len(comps) + 1}"
            # r.rpush(f'{device}:components', comp_name)
            logger.debug(f"Added component: {comp_name}")
        elif tid['type'] == 'del-comp-btn':
            logger.debug(f"Delete component action is deactivated.")
            pass
        elif tid['type'] == 'run-comp-btn':
            device, comp = tid['proc'], tid['comp']
            msg = {"command": "up", "app": comp}
            r.publish("orchestrator-control", json.dumps(msg))
            logger.debug(f"Setting {device}:{comp} to running")

        elif tid['type'] == 'pause-comp-btn':
            device, comp = tid['proc'], tid['comp']
            msg = {"command": "down", "app": comp}
            r.publish("orchestrator-control", json.dumps(msg))
            logger.debug(f"Setting {device}:{comp} to paused")

        elif tid['type'] == 'del-proc-btn':
            device, comp = tid['proc'], tid['comp']
            msg = {"command": "remove", "app": comp}
            r.set(f'devices:{device}:{comp}:status', 'removed')
            r.publish("orchestrator-control", json.dumps(msg))
            logger.debug(f"Deleted device: {device}")

            # elif tid['type'] == 'del-comp-btn':
            #     device, comp = tid['proc'], tid['comp']
            #     # Remove component from device's nodes list
            #     r.lrem(f"devices:{device}:nodes", 0, comp)
            #     # Clean up component status
            #     r.delete(f"devices:{device}:{comp}:status")
            #     logger.debug(f"Deleted component {comp} from device {device}")

    return dash.no_update

@app.callback(
    Output('log-sources-checklist', 'options'),
    Output('log-sources-checklist', 'value'),
    [Input('refresh-log-sources-btn', 'n_clicks')],
    [State('log-sources-checklist', 'value')],
    prevent_initial_call=False
)
def update_log_sources(refresh_clicks, current_values):
    """Update the available log sources by scanning Redis for *:logs keys"""
    try:
        # Get all keys matching the pattern *:logs
        all_keys = r.keys('*')
        log_keys = []
        
        for key in all_keys:
            if key.endswith(':logs'):
                log_keys.append(key)
        
        # Also include the general 'log' key if it exists
        if r.exists('log'):
            log_keys.append('log')
        
        # Sort the keys for consistent ordering
        log_keys = sorted(set(log_keys))
            
        # Create options for checklist
        options = [{'label': key, 'value': key} for key in log_keys]
        
        # Preserve current user selections, or select all if first load
        if current_values is None:
            # First load - select all available sources
            values = log_keys if log_keys else []
        else:
            # Keep only the currently selected sources that still exist
            values = [source for source in current_values if source in log_keys]
            # If no valid selections remain and we have sources, don't auto-select
            if not values and log_keys:
                values = []
        
        logger.info(f"Found log sources: {log_keys}, Selected: {values}")
        return options, values
        
    except Exception as e:
        logger.error(f"Error updating log sources: {e}")
        # Return some default options for testing
        default_options = [{'label': 'log', 'value': 'log'}]
        return default_options, current_values if current_values else []

@app.callback(
    Output('log-sources-checklist', 'options', allow_duplicate=True),
    [Input('interval-log-sources', 'n_intervals')],
    [State('log-sources-checklist', 'options'),
     State('log-sources-checklist', 'value')],
    prevent_initial_call=True
)
def auto_refresh_log_sources(_, current_options, current_values):
    """Automatically refresh log sources options without changing user selections"""
    try:
        # Get all keys matching the pattern *:logs
        all_keys = r.keys('*')
        log_keys = []
        
        for key in all_keys:
            if key.endswith(':logs'):
                log_keys.append(key)
        
        # Also include the general 'log' key if it exists
        if r.exists('log'):
            log_keys.append('log')
        
        # Sort the keys for consistent ordering
        log_keys = sorted(set(log_keys))
        
        # Get current options values
        current_option_values = [opt['value'] for opt in current_options] if current_options else []
        
        # Only update if there are new sources
        if set(log_keys) != set(current_option_values):
            options = [{'label': key, 'value': key} for key in log_keys]
            logger.info(f"Auto-refreshed log sources: {log_keys}")
            return options
        else:
            # No change needed
            return dash.no_update
            
    except Exception as e:
        logger.error(f"Error auto-refreshing log sources: {e}")
        return dash.no_update

@app.callback(
    Output('live-log', 'children'),
    [Input('interval-log', 'n_intervals'),
     Input('log-sources-checklist', 'value')],
    prevent_initial_call=False
)
def update_log(_, selected_sources):
    """Update log display based on selected sources"""
    try:
        # If no sources selected or None, try to show default log
        if not selected_sources:
            if r.exists('log'):
                logs = r.lrange('log', -10, -1)
                if logs:
                    return '\n'.join(logs)
            return "No log sources selected. Please select log sources from the checklist above."
        
        all_logs = []
        
        for source in selected_sources:
            try:
                # Get logs from each source (latest 10 entries per source)
                logs = r.lrange(source, -10, -1)
                if logs:
                    # Add source prefix to each log entry
                    source_name = source.replace(':logs', '') if source.endswith(':logs') else source
                    for log_entry in logs:
                        formatted_log = f"[{source_name}] {log_entry}"
                        all_logs.append(formatted_log)
                        
            except Exception as e:
                logger.warning(f"Error reading logs from {source}: {e}")
                all_logs.append(f"[ERROR] Could not read from {source}: {str(e)}")
                continue
        
        if all_logs:
            # Get the latest 10 entries from all combined logs
            latest_logs = all_logs[-10:] if len(all_logs) > 10 else all_logs
            return '\n'.join(latest_logs)
        else:
            return "No logs found in selected sources."
            
    except Exception as e:
        logger.error(f"Error updating logs: {e}")
        return f"Error loading logs: {str(e)}"

if __name__ == '__main__':
    # Get configuration from environment variables
    dash_host = os.getenv('DASH_HOST', '0.0.0.0')
    dash_port = int(os.getenv('DASH_PORT', '8051'))
    logger.info("Starting Dash server in debug mode")
    app.run(host=dash_host, port=dash_port, debug=True)
