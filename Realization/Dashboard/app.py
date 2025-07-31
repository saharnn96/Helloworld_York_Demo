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

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

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
                    'marginBottom': '5px',
                    'fontWeight': '300',
                    'fontSize': '1.8rem'
                }),
        html.P("Real-time monitoring and control of distributed components", 
               style={
                   'textAlign': 'center', 
                   'color': '#7f8c8d',
                   'marginBottom': '10px',
                   'fontSize': '0.9rem'
               })
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '20px 20px',
        'marginBottom': '15px',
        'borderRadius': '0 0 10px 10px',
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
    }),

    # Main Content Grid
    html.Div([
        # Left Column: Gantt Chart
        html.Div([
            html.Div([
                html.H3("Components Timeline", 
                        style={
                            'color': '#2c3e50',
                            'marginBottom': '10px',
                            'fontWeight': '400',
                            'fontSize': '1.1rem'
                        }),
                dcc.Graph(id="gantt-chart", style={'height': '320px'})
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
                'border': '1px solid #e9ecef',
                'height': '370px'
            })
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right Column: Device Cards
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Device Status", 
                            style={
                                'color': '#2c3e50',
                                'marginBottom': '10px',
                                'fontWeight': '400',
                                'display': 'inline-block',
                                'fontSize': '1.1rem'
                            }),
                    html.Button('+ Add Device', 
                               id='add-processor-btn', 
                               style={
                                   'backgroundColor': '#3498db',
                                   'color': 'white',
                                   'border': 'none',
                                   'padding': '6px 12px',
                                   'borderRadius': '4px',
                                   'cursor': 'pointer',
                                   'fontSize': '12px',
                                   'float': 'right',
                                   'transition': 'all 0.3s ease'
                               })
                ], style={'marginBottom': '10px'}),
                html.Div(id='processor-cards', 
                        style={
                            'display': 'grid', 
                            'gridTemplateColumns': '1fr', 
                            'gap': '8px',
                            'maxHeight': '320px',
                            'overflowY': 'auto'
                        })
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
                'border': '1px solid #e9ecef',
                'height': '370px'
            })
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
    ], style={'marginBottom': '15px'}),

    # Logs Section
    html.Div([
        html.Div([
            html.H3("System Logs", 
                    style={
                        'color': '#2c3e50',
                        'marginBottom': '10px',
                        'fontWeight': '400',
                        'display': 'inline-block',
                        'fontSize': '1.1rem'
                    }),
            html.Button('🔄 Refresh Log Sources', 
                       id='refresh-log-sources-btn',
                       style={
                           'backgroundColor': '#17a2b8',
                           'color': 'white',
                           'border': 'none',
                           'padding': '6px 12px',
                           'borderRadius': '4px',
                           'cursor': 'pointer',
                           'fontSize': '12px',
                           'float': 'right',
                           'transition': 'all 0.3s ease'
                       })
        ], style={'marginBottom': '8px'}),
        
        html.Div([
            html.Label("Select Log Sources:", style={
                'fontWeight': '600',
                'color': '#2c3e50',
                'marginBottom': '5px',
                'display': 'block',
                'fontSize': '12px'
            }),
            dcc.Checklist(
                id='log-sources-checklist',
                options=[],
                value=[],
                style={
                    'marginBottom': '8px'
                },
                inputStyle={
                    'marginRight': '6px'
                },
                labelStyle={
                    'display': 'inline-block',
                    'marginRight': '12px',
                    'marginBottom': '3px',
                    'color': '#34495e',
                    'fontSize': '12px'
                }
            )
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '8px',
            'borderRadius': '4px',
            'border': '1px solid #dee2e6',
            'marginBottom': '8px'
        }),
        
        html.Pre(id='live-log', 
                style={
                    'height': '200px', 
                    'overflowY': 'auto', 
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '4px',
                    'padding': '8px',
                    'fontFamily': 'Monaco, Consolas, "Courier New", monospace',
                    'fontSize': '11px',
                    'lineHeight': '1.3',
                    'margin': '0'
                })
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '15px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'border': '1px solid #e9ecef',
        'height': '300px'
    }),

    # Intervals
    dcc.Interval(id='interval-gantt', interval=1000, n_intervals=0),
    dcc.Interval(id='interval-redis', interval=2000, n_intervals=0),
    dcc.Interval(id='interval-log', interval=1000, n_intervals=0),
    dcc.Interval(id='interval-log-sources', interval=5000, n_intervals=0)  # Check for new sources every 5 seconds
], style={
    'backgroundColor': '#f5f6fa',
    'minHeight': '100vh',
    'maxHeight': '100vh',
    'padding': '10px',
    'margin': '0',
    'fontFamily': '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
    'overflow': 'hidden'
})

@app.callback(
    Output("gantt-chart", "figure"),
    Input("interval-gantt", "n_intervals")
)
def update_gantt(_):
    fig = go.Figure()
    phase_colors = {
        "Monitor": "#3498db",
        "Analyze": "#2ecc71", 
        "Plan": "#f39c12",
        "Execute": "#e74c3c",
        "Knowledge": "#9b59b6"
    }
    
    device_names = r.lrange('devices:list', 0, -1)
    now = time.time()
    time_window = 15  # Show last 60 seconds to keep history
    
    for device in device_names:
        nodes = r.lrange(f"devices:{device}:nodes", 0, -1)
        for node in nodes:
            # Get execution history for this component
            history_key = f"devices:{device}:{node}:execution_history"
            execution_history = r.lrange(history_key, 0, -1)  # Get all history entries
            
            # Also check for current execution data (single execution)
            execution_time_key = f"{node}:execution_time"
            start_execution_key = f"{node}:start_execution"
            device_execution_time_key = f"devices:{device}:{node}:execution_time"
            device_start_execution_key = f"devices:{device}:{node}:start_execution"
            
            execution_time = r.get(execution_time_key) or r.get(device_execution_time_key)
            start_execution = r.get(start_execution_key) or r.get(device_start_execution_key)
            
            # Process execution history if available
            if execution_history:
                for history_entry in execution_history:
                    try:
                        # Parse history entry (format: "start_time,duration,status")
                        parts = history_entry.split(',')
                        if len(parts) >= 2:
                            start_exec = float(parts[0])
                            exec_time = float(parts[1])
                            status = parts[2] if len(parts) > 2 else "completed"
                            
                            # Calculate relative time positions
                            start_relative = now - start_exec
                            
                            # Show all executions within time window
                            if start_relative <= time_window and start_relative >= 0:
                                bar_start = -start_relative
                                bar_width = exec_time
                                
                                # Adjust bar width if it extends beyond current time
                                if bar_start + bar_width > 0:
                                    bar_width = -bar_start
                                
                                if bar_width > 0:
                                    # Color based on node type and status
                                    node_color = phase_colors.get(node, "#95a5a6")
                                    if status == "active" or status == "running":
                                        node_color = phase_colors.get(node, "#27ae60")
                                    elif status == "building":
                                        node_color = "#f1c40f"
                                    elif status == "error":
                                        node_color = "#e67e22"
                                    elif status == "completed":
                                        # Use slightly faded color for completed executions
                                        base_color = phase_colors.get(node, "#95a5a6")
                                        node_color = base_color + "AA"  # Add transparency
                                    
                                    fig.add_trace(go.Bar(
                                        name=f"{device}:{node}",
                                        x=[bar_width],
                                        y=[f"{device}:{node}"],
                                        base=bar_start,
                                        orientation="h",
                                        marker=dict(
                                            color=node_color,
                                            line=dict(color='rgba(0,0,0,0.3)', width=1)
                                        ),
                                        hovertemplate=(
                                            f"<b>{device}:{node}</b><br>"
                                            f"Started: {start_relative:.1f}s ago<br>"
                                            f"Duration: {exec_time:.1f}s<br>"
                                            f"Status: {status}<br>"
                                            "<extra></extra>"
                                        ),
                                        showlegend=False
                                    ))
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing history entry {history_entry}: {e}")
                        continue
            
            # ALWAYS check for current/new execution data (even if history exists)
            if execution_time and start_execution:
                try:
                    start_exec = float(start_execution)
                    exec_time = float(execution_time)
                    
                    # Check if this execution is already in history to avoid duplicates
                    is_duplicate = False
                    if execution_history:
                        for history_entry in execution_history:
                            try:
                                parts = history_entry.split(',')
                                if len(parts) >= 2:
                                    hist_start = float(parts[0])
                                    hist_duration = float(parts[1])
                                    # Consider it duplicate if start time and duration match closely
                                    if abs(hist_start - start_exec) < 0.1 and abs(hist_duration - exec_time) < 0.1:
                                        is_duplicate = True
                                        break
                            except (ValueError, IndexError):
                                continue
                    
                    # Only process if not a duplicate
                    if not is_duplicate:
                        # Calculate relative time positions
                        start_relative = now - start_exec
                        
                        # Show if within time window
                        if start_relative <= time_window and start_relative >= 0:
                            bar_start = -start_relative
                            bar_width = exec_time
                            
                            # Adjust bar width if it extends beyond current time
                            if bar_start + bar_width > 0:
                                bar_width = -bar_start
                            
                            if bar_width > 0:
                                # Get component status for color coding
                                status = r.get(f"devices:{device}:{node}:status")
                                node_color = phase_colors.get(node, "#95a5a6")
                                
                                # Modify color based on status
                                if status == "active" or status == "running":
                                    node_color = phase_colors.get(node, "#27ae60")
                                elif status == "building":
                                    node_color = "#f1c40f"
                                elif status == "error":
                                    node_color = "#e67e22"
                                
                                fig.add_trace(go.Bar(
                                    name=f"{device}:{node}",
                                    x=[bar_width],
                                    y=[f"{device}:{node}"],
                                    base=bar_start,
                                    orientation="h",
                                    marker=dict(
                                        color=node_color,
                                        line=dict(color='rgba(0,0,0,0.3)', width=1)
                                    ),
                                    hovertemplate=(
                                        f"<b>{device}:{node}</b><br>"
                                        f"Started: {start_relative:.1f}s ago<br>"
                                        f"Duration: {exec_time:.1f}s<br>"
                                        f"Status: {status or 'current'}<br>"
                                        "<extra></extra>"
                                    ),
                                    showlegend=False
                                ))
                                
                                logger.debug(f"Added NEW bar for {device}:{node} - start: {bar_start:.2f}, width: {bar_width:.2f}")
                            
                            # Store this NEW execution in history for future reference
                            history_entry = f"{start_exec},{exec_time},{status or 'active'}"
                            r.lpush(f"devices:{device}:{node}:execution_history", history_entry)
                            # Keep only last 50 history entries per component
                            r.ltrim(f"devices:{device}:{node}:execution_history", 0, 49)
                            logger.debug(f"Stored new execution in history: {history_entry}")
                                
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing {device}:{node} execution data: {e}")
                    continue
    
    # Update layout with proper time axis
    fig.update_layout(
        title={
            'text': f"Component Execution History (Last {time_window} Seconds)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 14, 'color': '#2c3e50'}
        },
        xaxis={
            'title': "Time (seconds ago ← | → now)",
            'range': [-time_window, 0],
            'tickmode': 'linear',
            'dtick': 10,
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.1)',
            'zeroline': True,
            'zerolinecolor': 'rgba(231, 76, 60, 0.8)',
            'zerolinewidth': 2
        },
        yaxis={
            'title': "Components",
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.1)',
            'categoryorder': 'category ascending'  # Keep consistent ordering
        },
        barmode="overlay",
        template="plotly_white",
        showlegend=False,
        plot_bgcolor="rgba(248, 249, 250, 1)",
        paper_bgcolor="rgba(255, 255, 255, 1)",
        font={'family': '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif'},
        margin={'l': 120, 'r': 20, 't': 60, 'b': 60},
        height=300
    )
    
    # Add vertical line at current time (x=0)
    fig.add_vline(
        x=0, 
        line_dash="dash", 
        line_color="rgba(231, 76, 60, 0.8)",
        annotation_text="Now",
        annotation_position="top"
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
    dash_port = int(os.getenv('DASH_PORT', '8050'))
    logger.info("Starting Dash server in debug mode")
    app.run(host=dash_host, port=dash_port, debug=True)

