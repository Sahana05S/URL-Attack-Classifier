# URL Attack Detection System

An enterprise-style Streamlit app for detecting malicious URL activity from web access logs. It combines fast rule-based detection with a lightweight ML classifier to triage traffic, surface likely attacks, and prioritize SOC review.

## Detection Pipeline
- **Ingestion & cleaning**: Accepts CSV logs containing at least `url` and `status_code` (other columns are preserved). URLs are decoded, lowercased, and parsed to a normalized path/query string.
- **Rule pass**: Applies deterministic signatures to flag common web attacks directly from the cleaned URL.
- **ML pass**: Loads a serialized scikit-learn vectorizer and model from `url_model.pkl`; predicts an attack/normal label for URLs not caught by rules. If the model is missing, the pipeline defaults the ML output to `Normal`.
- **Decision fusion**: Chooses the rule verdict when present; otherwise falls back to the ML prediction as `Final_Attack`.
- **Outcome & priority**: Infers `Outcome` (`Benign`, `Attempt`, `Likely Successful` using status codes) and `Priority` (`Low`, `Medium`, `High`) to support triage.

## Rule-Based Engine
- Defined in `detector.py` as regex signatures for **SQL Injection**, **XSS**, **Directory Traversal**, **Command Injection**, and **SSRF**.
- Each URL is checked against these patterns; the first match returns the attack type, otherwise `Normal`.

## ML Model
- Stored in `url_model.pkl` as a tuple `(vectorizer, model)` built with scikit-learn text features over cleaned URLs.
- Expects preprocessed URL text; if the file is absent or unloadable, the app safely defaults to `Normal` predictions without failing the pipeline.

## Run the App
1. Install dependencies: `pip install -r requirements.txt`
2. Start Streamlit: `streamlit run app.py`
3. Use the UI:
   - **Upload Logs**: Provide a CSV with `url`, `status_code`, and any contextual fields.
   - **Dashboard**: View metrics, attack summaries, and styled traffic table with priority and outcome highlights.

## Repository Layout
- `app.py` — Landing page and theme toggle.
- `pages/` — Streamlit multipage views (Home, Upload, Dashboard, etc.).
- `pipeline.py` — End-to-end detection pipeline (preprocess, rules, ML, fusion, outcomes).
- `detector.py` — Regex rule engine for web attacks.
- `assets/` — CSS themes for dark/light UI.***
