import sqlite3
from datetime import datetime

import pandas
from plotly import express, graph_objs


def pipeline_runtime_cmd(
    database_file: str,
    plot_file: str,
    reference: str,
    moving_average_window: int,
    clamp_min: int | None = None,
    clamp_max: int | None = None,
    after: datetime | None = None,
    before: datetime | None = None,
    **kwargs,
):
    with sqlite3.connect(database_file) as conn:
        df = get_pipeline_runtime_df(
            conn,
            reference,
            moving_average_window,
            clamp_min,
            clamp_max,
            after,
            before,
        )
        fig = plot_pipeline_runtime(df, f'Pipeline Runtime for <i>{reference}</i>')
        fig.write_html(plot_file)


def get_pipeline_runtime_df(
    conn: sqlite3.Connection,
    reference: str,
    moving_average_window: int,
    clamp_min: int | None = None,
    clamp_max: int | None = None,
    after: datetime | None = None,
    before: datetime | None = None,
) -> pandas.DataFrame:
    result = pandas.read_sql(
        '''
        SELECT
            pipeline_id,
            created_at,
            duration,
            json_extract(data, '$.status') status,
            json_extract(data, '$.queued_duration') queued_duration
        FROM pipeline
        WHERE
            ref = :ref
            AND duration IS NOT NULL
            AND (:after IS NULL OR :after <= created_at)
            AND (:before IS NULL OR created_at <= :before)
            AND (:clamp_min IS NULL OR :clamp_min <= duration)
            AND (:clamp_max IS NULL OR duration <= :clamp_max)
        ORDER BY pipeline_id DESC
        ''',
        conn,
        params={
            'ref': reference,
            'clamp_min': clamp_min,
            'clamp_max': clamp_max,
            'after': after.timestamp() if after else None,
            'before': before.timestamp() if before else None,
        },
    )

    result['created_at'] = pandas.to_datetime(result['created_at'], unit='s', origin='unix')
    result['duration_delta'] = (
        pandas.to_timedelta(result['duration'], unit='s') + pandas.to_datetime(0)
    )
    result['duration_avg'] = (
        pandas.to_timedelta(
            (
                result['duration']
                .rolling(moving_average_window, center=True)
                .mean()
            ),
            unit='s',
        ) + pandas.to_datetime(0)
    )

    return result


def plot_pipeline_runtime(df: pandas.DataFrame, title: str) -> graph_objs.Figure:
    scatter = express.scatter(
        df,
        x='created_at',
        y='duration_delta',
        color='status',
        hover_data=['queued_duration'],
    )

    line = express.line(
        df,
        x='created_at',
        y='duration_avg',
    )
    line.update_traces(line=dict(color='#333'))

    fig = graph_objs.Figure(scatter.data + line.data)
    fig.update_layout(
        title=title,
        yaxis_tickformat='%H:%M:%S ',
        showlegend=True,
    )

    return fig
