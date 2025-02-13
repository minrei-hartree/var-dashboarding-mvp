import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class Plot:
    def ___init__(self):
        pass

    @staticmethod
    def plot_timeseries(s1, n1='facade', title='Timeseries'):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=s1.index,
                y=s1.values,
                mode='lines',
                name=title,
            )
        )
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            showlegend=True
        )
        return fig

    @staticmethod
    def plot_timeseries_multiple(*series_args, title='Timeseries', width: int = None):
        """
        Plot multiple time series on the same figure
        
        Args:
            *series_args: Alternating series and names
                        e.g. (series1, 'name1', series2, 'name2', ...)
            title (str): Title for the plot
        """
        fig = go.Figure()
        
        # Iterate through series and names in pairs
        for series, name in zip(series_args[::2], series_args[1::2]):
            fig.add_trace(
                go.Scatter(
                    x=series.index,
                    y=series.values,
                    mode='lines',
                    name=name
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            showlegend=True,
            **({'width': width} if width else {})
        )
        return fig

    @staticmethod
    def make_multi_plot(plot_funcs, layout_title: str = 'default', rows = None, cols : int = 2, file_name: str = 'default', subplot_titles = []):
        n_plots = len(plot_funcs)
        if rows is None:
            rows = max(1, int(0.5 + n_plots / 2))
        
        m = len(subplot_titles)
        for _ in range(n_plots-m):
            subplot_titles.append("")

        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=None if m == 0 else subplot_titles
        )

        for i, (func, args, kwargs) in enumerate(plot_funcs):
            row = (i // cols) + 1
            col = (i % cols) + 1

            temp_fig = func(*args, **kwargs)
            for trace in temp_fig.data:
                fig.add_trace(trace, row=row, col=col)
            
            fig.update_xaxes(
                title_text=temp_fig.layout.yaxis.title.text, 
                row=row,
                col=col
            )

            fig.update_yaxes(
                row=row,
                col=col
            )
        
        fig.update_layout(
            height=500 * (2/cols) * rows,
            width=max(1200, 400*cols),
            title_text=layout_title,
            showlegend=True,
            xaxis=dict(
                rangeslider=dict(visible=False),
                type='date'
            )
        )

        # Link all x-axes together
        fig.update_layout(xaxis=dict(matches='x'))
        for i in range(2, n_plots + 1):
            fig.update_layout({f'xaxis{i}': dict(matches='x')})
        
        if file_name != 'default':
            fig.write_html(f'{file_name}.html')

        return fig
    
    @staticmethod
    def plot_correlations(v1: pd.Series, v2: pd.Series, window: int = 20, lookback: str = "max", title: str = "", width: int =None):
        """_summary_

        Args:
            v1 (pd.Series): index of pd.Datetime, values of returns (simple/log)
            v2 (pd.Series): index of pd.Datetime, values of returns (simple/log)
            window (int, optional): roll for correlation window. Defaults to 20 days.
            lookback (str, optional): _description_. Defaults to "max".
        """
        df = v1.to_frame().join(v2, how='inner', lsuffix=f'_v1', rsuffix=f'_v2')
        cols = df.columns

        # set lookback
        if lookback != "max":
            if lookback == "1y":
                delta = pd.DateOffset(years=1, days=window*2)
            elif lookback == "3y":
                delta = pd.DateOffset(years=1, days=window*2)
            elif lookback == "3m":
                delta = pd.DateOffset(months=3, days=window*2)
            else:
                delta = pd.Timedelta(lookback + window*2)

            lookback_date = df.index.max() - delta
            df = df[df.index >= lookback_date]
        

        v1_rolling_var = df[cols[0]].rolling(window).var()
        v2_rolling_var = df[cols[1]].rolling(window).var()

        # Mask windows where either series has zero variance
        valid_windows = (v1_rolling_var > 0) & (v2_rolling_var > 0)

        # Calculate rolling correlation, masking invalid windows
        rolling_corr = (
            df[cols[0]]
            .rolling(window)
            .corr(df[cols[1]])
            .where(valid_windows)  # Replace invalid windows with NaN
            .dropna()
        )
        average_r2 = rolling_corr.pow(2).mean()

        title = f'{title}; R2 = {average_r2:.3f}'

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=rolling_corr.index,
                y=rolling_corr,
                mode='lines',
                name=title,
                hovertemplate='Date: %{x}<br>Correlation: %{y:.3f}<extra></extra>'
            )
        )

        fig.update_layout(
            title=f'{window}-Day Rolling Correlation: {title}',
            xaxis_title='Date',
            yaxis_title=title,
            yaxis=dict(range=[-1, 1]),
            showlegend=True,
            **({'width': width} if width else {})
        )

        return fig
    
    @staticmethod
    def time_series_metrics(actual_changes: pd.Series, predicted_changes: pd.Series, title: str="", width = None):
        actual = np.array(actual_changes)
        predicted = np.array(predicted_changes)
        unique_dates = actual_changes.index

        # Calculate metrics
        mae = mean_absolute_error(actual, predicted)
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual, predicted)

        print(f"MAE: {mae:.4f}")
        print(f"MSE: {mse:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R²: {r2:.4f}")

        # Create plots
        # 1. Time Series Comparison
        # fig1 = go.Figure()
        # fig1.add_trace(go.Scatter(x=unique_dates, y=actual, name='Actual Changes', line=dict(color='blue')))
        # fig1.add_trace(go.Scatter(x=unique_dates, y=predicted, name='Predicted Changes', line=dict(color='red', dash='dot')))
        # fig1.update_layout(title='Actual vs Predicted Price Changes Over Time',
        #                 xaxis_title='Date',
        #                 yaxis_title='Price Change',
        #                 hovermode='x unified')
        # fig1.show()

        # 2. Scatter Plot with 45-degree line
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=predicted, y=actual, mode='markers', name='Data Points'))
        fig2.add_shape(type='line', 
                    x0=min(actual.min(), predicted.min()),
                    y0=min(actual.min(), predicted.min()),
                    x1=max(actual.max(), predicted.max()),
                    y1=max(actual.max(), predicted.max()),
                    line=dict(color='red', dash='dash'))
        if width:
            fig2.update_layout(title=f'{title} (R² = {r2:.2f})',
                            xaxis_title='Predicted Changes',
                            yaxis_title='Actual Changes',
                            width=width)
        else:
            fig2.update_layout(title=f'{title} (R² = {r2:.2f})',
                            xaxis_title='Predicted Changes',
                            yaxis_title='Actual Changes',
                            )
        fig2.show()

        # 3. Residuals Analysis
        # residuals = actual - predicted

        # fig3 = make_subplots(rows=2, cols=1, subplot_titles=('Residuals Over Time', 'Residual Distribution'))

        # fig3.add_trace(go.Scatter(x=unique_dates, y=residuals, mode='lines', name='Residuals'),
        #             row=1, col=1)
        # fig3.add_trace(go.Histogram(x=residuals, nbinsx=50, name='Residuals'),
        #             row=2, col=1)

        # fig3.update_layout(height=600, width=800, title_text='Residual Analysis')
        # fig3.update_xaxes(title_text='Residual Value', row=2, col=1)
        # fig3.update_yaxes(title_text='Count', row=2, col=1)
        # fig3.show()