"""Minimal Streamlit UI for the SYN-flood detection demo

Features:
- select or upload a features CSV
- choose a trained model
- run detection (uses src.detect.detect_and_write_alerts)
- display alerts table and allow download
- generate sample alerts (demo)
"""
from pathlib import Path
import json
import runpy
import streamlit as st
import pandas as pd
from src.detect import detect_and_write_alerts
from src.auth import validate_password
from src.validation import validate_model_path, validate_features_df
from src.background import run_detection_background

REPO_ROOT = Path(__file__).resolve().parents[2]

# helper to render alerts list (JSON list of alerts)
def render_alerts(alerts, feats_df=None):
    rows = []
    for a in alerts:
        r = {
            'timestamp': a.get('timestamp'),
            'alert_id': a.get('alert_id'),
            'score': a.get('score'),
            'verdict': a.get('verdict'),
            'explanation': a.get('explanation')
        }
        feats = a.get('features', {})
        r.update({f'feat_{k}': v for k, v in feats.items()})
        rows.append(r)

    if not rows:
        st.info('No alerts detected (0)')
        return

    df = pd.DataFrame(rows)
    st.subheader('Detected Alerts')
    st.dataframe(df.sort_values('timestamp'))
    st.json({'count': len(rows), 'sample': rows[:3]})

    # JSON download
    content = '\n'.join(json.dumps(a) for a in alerts)
    st.download_button('Download alerts (JSON)', data=content.encode('utf-8'), file_name='alerts.json', mime='application/json')

    # CSV download
    alerts_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download alerts (CSV)', data=alerts_csv, file_name='alerts.csv', mime='text/csv')

    # merged features (if available)
    if feats_df is not None and 'ts_start' in feats_df.columns:
        try:
            feats_df['ts_iso'] = pd.to_datetime(feats_df['ts_start'], unit='s', utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            feats_df['ts_iso'] = pd.to_datetime(feats_df['ts_start'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        df_ts = set(df['timestamp'].tolist())
        feats_df['is_alert'] = feats_df['ts_iso'].isin(df_ts)

        merged_csv = feats_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download merged features (CSV)', data=merged_csv, file_name='features_with_alerts.csv', mime='text/csv')

    # plotting overlay: try Altair to show features with red rules for alerts
    try:
        import altair as alt
        if feats_df is not None and not feats_df.empty:
            default_feats = ['packets_per_sec', 'bytes_per_sec', 'syn_ratio', 'entropy_src_ip', 'entropy_dst_ip']
            available_feats = [c for c in default_feats if c in feats_df.columns]
            select_feats_local = available_feats[:2]

            plot_data = feats_df.reset_index()[['time'] + select_feats_local] if 'time' in feats_df.columns else feats_df[select_feats_local]
            base = alt.Chart(plot_data).transform_fold(select_feats_local, as_=['feature', 'value']).mark_line().encode(
                x='time:T', y='value:Q', color='feature:N')

            alerts_df = pd.DataFrame(rows)
            alerts_df['timestamp_dt'] = pd.to_datetime(alerts_df['timestamp'])
            rules = alt.Chart(alerts_df).mark_rule(color='red').encode(x='timestamp_dt:T')

            st.subheader('Feature plots (alerts shown in red)')
            st.altair_chart(base + rules, width='stretch')
    except Exception:
        # fallback visualizations
        st.subheader('Alerts (table)')
        st.table(pd.DataFrame(rows))
        if feats_df is not None and not feats_df.empty:
            st.subheader('Feature plots')
            if 'time' in feats_df.columns:
                st.line_chart(feats_df.set_index('time')[select_feats_local])
            else:
                st.line_chart(feats_df[select_feats_local])

st.title('Projet_PE — Détection SYN flood (Streamlit UI)')
st.markdown('Simple UI to run the detection pipeline and visualize alerts')

# simple authentication

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    pw = st.text_input('Password (leave blank if none configured)', type='password')
    if st.button('Login'):
        if validate_password(pw):
            st.session_state['authenticated'] = True
            # Try to rerun if available. Otherwise do a single client reload using a small JS snippet and a session flag
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
            else:
                st.session_state['just_logged_in'] = True
                import streamlit.components.v1 as components
                components.html("<script>setTimeout(()=>{location.reload();}, 100);</script>", height=0)
                st.stop()
        else:
            st.error('Invalid password')
    st.stop()  # stop rendering the rest of the app until authenticated

# Clear the one-time just_logged_in flag after a reload to avoid loops
if st.session_state.get('just_logged_in'):
    st.session_state['just_logged_in'] = False
    st.success('Logged in — welcome!')

# discover data files
search_dirs = [REPO_ROOT / 'data', REPO_ROOT / 'projet_PE' / 'data']
csv_files = []
for d in search_dirs:
    if d.exists():
        csv_files.extend(sorted([str(p) for p in d.glob('*.csv')]))

uploaded_file = st.file_uploader('Upload features CSV (columns: packets_per_sec, bytes_per_sec, entropy_src_ip, entropy_dst_ip, syn_ratio, ts_start)', type=['csv'])

selected_file = None
if uploaded_file is not None:
    # save to a temp file to pass to detection
    tmp = Path('data') / 'uploaded_features.csv'
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    selected_file = str(tmp)
else:
    selected = st.selectbox('Or select a features CSV from repository', options=['-- choose --'] + csv_files)
    if selected and selected != '-- choose --':
        selected_file = selected

# model chooser
model_candidates = []
for m in [REPO_ROOT / 'models' / 'final_model.pkl', REPO_ROOT / 'models' / 'model.pkl', REPO_ROOT / 'projet_PE' / 'models' / 'model.pkl']:
    if m.exists():
        model_candidates.append(str(m))

if not model_candidates:
    st.warning('No model found in repository. Run the demo to train a model: `python run_demo.py`')
    model_path = st.text_input('Model path', value='models/model.pkl')
else:
    model_path = st.selectbox('Select model', options=model_candidates, index=0)

# validate model path and ability to load
if model_path:
    ok, msg = validate_model_path(str(model_path))
    if not ok:
        st.error('Model validation failed: ' + msg)


st.write('Output will be written to the `outputs` directory (temporary copy is shown below).')

# Background job status area (auto-refresh while running)
if 'detection_status' in st.session_state:
    ds = st.session_state['detection_status']
    if ds.get('running'):
        st.info('Background detection is running... (this page will auto-refresh)')
        # auto-refresh the page every 2s while running so status updates are shown
        import streamlit.components.v1 as components
        components.html("<script>setInterval(()=>{location.reload();}, 2000);</script>", height=0)
    elif ds.get('error'):
        st.error('Background detection failed: ' + str(ds.get('error')))
    elif ds.get('result') is not None:
        # render results and optionally the features if available
        try:
            feats_df = pd.read_csv(st.session_state.get('last_selected_file')) if st.session_state.get('last_selected_file') else None
        except Exception:
            feats_df = None
        alerts = ds.get('result')
        render_alerts(alerts, feats_df=feats_df)
        # clear result after showing once
        st.session_state['detection_status']['result'] = None

# Preview selected features file and allow plotting of features
if selected_file:
    try:
        feats_df = pd.read_csv(selected_file)

        ok, errors = validate_features_df(feats_df)
        if not ok:
            st.error('Invalid features CSV: ' + '; '.join(errors))
        else:
            st.subheader('Features preview')
            st.write(f"Loaded `{selected_file}` — {len(feats_df)} rows")
            st.dataframe(feats_df.head())

            # prepare a time column if ts_start exists
            if 'ts_start' in feats_df.columns:
                try:
                    feats_df['time'] = pd.to_datetime(feats_df['ts_start'], unit='s', utc=True)
                except Exception:
                    feats_df['time'] = pd.to_datetime(feats_df['ts_start'], utc=True)

            default_feats = ['packets_per_sec', 'bytes_per_sec', 'syn_ratio', 'entropy_src_ip', 'entropy_dst_ip']
            available_feats = [c for c in default_feats if c in feats_df.columns]
            select_feats = st.multiselect('Features to plot', options=available_feats, default=available_feats[:2])

            if select_feats:
                try:
                    import altair as alt
                    plot_data = feats_df.reset_index()[['time'] + select_feats] if 'time' in feats_df.columns else feats_df[select_feats]
                    chart = alt.Chart(plot_data).transform_fold(select_feats, as_=['feature', 'value']).mark_line().encode(
                        x='time:T', y='value:Q', color='feature:N').interactive()
                    st.altair_chart(chart, use_container_width=True)
                except Exception:
                    if 'time' in feats_df.columns:
                        st.line_chart(feats_df.set_index('time')[select_feats])
                    else:
                        st.line_chart(feats_df[select_feats])

    except Exception as e:
        st.error(f'Unable to load preview of selected file: {e}')

sample_button = st.button('Generate sample alerts (demo)')

if sample_button:
    st.info('Generating sample test trace and sample alerts...')
    # run the sample generator script as a module (it writes to outputs/sample_alerts.json)
    try:
        runpy.run_module('src.generate_sample_alerts', run_name='__main__')
        st.success('Wrote outputs/sample_alerts.json')
    except Exception as e:
        st.error(f'Error generating sample alerts: {e}')

# Two explicit buttons: background and blocking
col1, col2 = st.columns(2)
start_bg = col1.button('Start detection in background')
run_blocking = col2.button('Run detection (blocking)')

if start_bg or run_blocking:
    if not selected_file:
        st.error('No features CSV selected or uploaded')
    else:
        out_dir = REPO_ROOT / 'outputs'
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / 'alerts.json'
        try:
            # load and validate features
            try:
                feats_df = pd.read_csv(selected_file)
            except Exception as e:
                st.error('Unable to read features CSV: ' + str(e))
                feats_df = None
                st.stop()

            ok_feats, feat_errors = validate_features_df(feats_df)
            if not ok_feats:
                st.error('Invalid features CSV: ' + '; '.join(feat_errors))
                st.stop()

            # model validation
            ok_model, model_err = validate_model_path(str(model_path))
            if not ok_model:
                st.error('Model validation failed: ' + model_err)
                st.stop()

            # Background run
            if start_bg:
                if 'detection_status' not in st.session_state:
                    st.session_state['detection_status'] = {'running': False, 'error': None, 'result': None}

                if st.session_state['detection_status']['running']:
                    st.info('Detection already running in background...')
                else:
                    st.session_state['detection_status']['running'] = True
                    # remember which file was used so we can show features after completion
                    st.session_state['last_selected_file'] = str(selected_file)
                    run_detection_background(detect_and_write_alerts, args=(str(model_path), str(selected_file), str(out_path)), status_container=st.session_state['detection_status'])
                    st.success('Background detection started')

            # Blocking run
            if run_blocking:
                with st.spinner('Running detection...'):
                    alerts = detect_and_write_alerts(str(model_path), str(selected_file), str(out_path))
                st.success(f'Wrote {out_path} — found {len(alerts)} alert(s)')

                if len(alerts) == 0:
                    st.info('No alerts detected (model predicted all samples as normal)')

                # display flattened table
                rows = []
                for a in alerts:
                    r = {
                        'timestamp': a.get('timestamp'),
                        'alert_id': a.get('alert_id'),
                        'score': a.get('score'),
                        'verdict': a.get('verdict'),
                        'explanation': a.get('explanation')
                    }
                    feats = a.get('features', {})
                    r.update({f'feat_{k}': v for k, v in feats.items()})
                    rows.append(r)

                # present alerts and improved downloads
                df = pd.DataFrame(rows)
                if not df.empty:
                    st.subheader('Detected Alerts')
                    st.dataframe(df.sort_values('timestamp'))
                    st.json({'count': len(rows), 'sample': rows[:3]})

                    # JSON download
                    content = '\n'.join(json.dumps(a) for a in alerts)
                    st.download_button('Download alerts (JSON)', data=content.encode('utf-8'), file_name='alerts.json', mime='application/json')

                    # CSV download
                    alerts_csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button('Download alerts (CSV)', data=alerts_csv, file_name='alerts.csv', mime='text/csv')

                    # merged features (mark rows that are alerts by matching timestamp)
                    if feats_df is not None and 'ts_start' in feats_df.columns:
                        try:
                            feats_df['ts_iso'] = pd.to_datetime(feats_df['ts_start'], unit='s', utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                        except Exception:
                            feats_df['ts_iso'] = pd.to_datetime(feats_df['ts_start'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

                        df_ts = set(df['timestamp'].tolist())
                        feats_df['is_alert'] = feats_df['ts_iso'].isin(df_ts)

                        merged_csv = feats_df.to_csv(index=False).encode('utf-8')
                        st.download_button('Download merged features (CSV)', data=merged_csv, file_name='features_with_alerts.csv', mime='text/csv')

                    # plotting overlay: try Altair to show features with red rules for alerts
                    try:
                        import altair as alt
                        if feats_df is not None and not feats_df.empty:
                            default_feats = ['packets_per_sec', 'bytes_per_sec', 'syn_ratio', 'entropy_src_ip', 'entropy_dst_ip']
                            available_feats = [c for c in default_feats if c in feats_df.columns]
                            select_feats = available_feats[:2] if 'select_feats' not in globals() else select_feats

                            plot_data = feats_df.reset_index()[['time'] + select_feats] if 'time' in feats_df.columns else feats_df[select_feats]
                            base = alt.Chart(plot_data).transform_fold(select_feats, as_=['feature', 'value']).mark_line().encode(
                                x='time:T', y='value:Q', color='feature:N')

                            alerts_df = df.copy()
                            alerts_df['timestamp_dt'] = pd.to_datetime(alerts_df['timestamp'])
                            rules = alt.Chart(alerts_df).mark_rule(color='red').encode(x='timestamp_dt:T')

                            st.subheader('Feature plots (alerts shown in red)')
                            st.altair_chart(base + rules, use_container_width=True)
                    except Exception:
                        # fallback visualizations
                        st.subheader('Alerts (table)')
                        st.table(df)
                        if feats_df is not None and not feats_df.empty:
                            st.subheader('Feature plots')
                            if 'time' in feats_df.columns:
                                st.line_chart(feats_df.set_index('time')[select_feats if 'select_feats' in globals() else available_feats[:2]])
                            else:
                                st.line_chart(feats_df[select_feats if 'select_feats' in globals() else available_feats[:2]])

        except Exception as e:
            st.error(f'Error during detection: {e}')
st.markdown('---')
st.markdown('**Note:** This is a minimal prototype. For production, add authentication, input validation, and better error handling.')
