from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import plotly.graph_objects as go

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename == '':
        return 'No file selected'

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    df.to_csv('original.csv', index=False)

    missing_info = df.isnull().sum().to_dict()

    fig = go.Figure()

    # Original data with gaps (before interpolation)
    for col in df.select_dtypes(include='number').columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines+markers',
            name=f'{col} (Original)',
            line=dict(color='red'),
            connectgaps=False  # This ensures gaps are shown
        ))

    fig.update_layout(
        title='Missing Data with Gaps (Before Interpolation)',
        xaxis_title='Index',
        yaxis_title='Values'
    )

    graph_html_before = fig.to_html(full_html=False)

    return render_template('show_missing.html', data=missing_info, graph_html=graph_html_before)

@app.route('/interpolate', methods=['POST'])
def interpolate_file():
    df = pd.read_csv('original.csv')
    df_interpolated = df.interpolate()

    output_path = os.path.join(UPLOAD_FOLDER, 'interpolated.csv')
    df_interpolated.to_csv(output_path, index=False)

    columns = df_interpolated.columns.tolist()
    data = df_interpolated.values.tolist()

    # Graph showing original data with gaps and interpolated data without gaps
    fig = go.Figure()

    for col in df.select_dtypes(include='number').columns:
        # Plot original data (with gaps)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines+markers',
            name=f'{col} (Original)',
            line=dict(dash='dot', color='red'),
            connectgaps=False  # Gaps in original data
        ))

        # Plot interpolated data (no gaps)
        fig.add_trace(go.Scatter(
            x=df_interpolated.index,
            y=df_interpolated[col],
            mode='lines+markers',
            name=f'{col} (Interpolated)',
            line=dict(dash='solid', color='blue')
        ))

    fig.update_layout(
        title='Comparison: Original vs Interpolated Data',
        xaxis_title='Index',
        yaxis_title='Values'
    )

    graph_html_after = fig.to_html(full_html=False)

    return render_template('show_interpolated.html', columns=columns, data=data, graph_html=graph_html_after)

@app.route('/download')
def download_file():
    path = os.path.join(UPLOAD_FOLDER, 'interpolated.csv')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "Interpolated file not found.", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
