
import joblib
from urllib.parse import unquote, urlparse
from detector import detect_attack

def preprocess_url(url):
    if not isinstance(url, str):
        return ""
    url = unquote(unquote(url)).lower().strip()
    parsed = urlparse(url)
    return parsed.path + "?" + parsed.query

def apply_pipeline(df):
    df = df.copy()
    df["clean_url"] = df["url"].apply(preprocess_url)
    df["Rule_Detection"] = df["clean_url"].apply(detect_attack)
    try:
        vec, model = joblib.load("url_model.pkl")
        df["ML_Prediction"] = model.predict(vec.transform(df["clean_url"]))
    except:
        df["ML_Prediction"] = "Normal"
    df["Final_Attack"] = df.apply(
        lambda r: r["Rule_Detection"] if r["Rule_Detection"] != "Normal" else r["ML_Prediction"],
        axis=1
    )
    def outcome(r):
        if r["Final_Attack"] != "Normal" and r["status_code"] in [200,302]:
            return "Likely Successful"
        elif r["Final_Attack"] != "Normal":
            return "Attempt"
        return "Benign"
    df["Outcome"] = df.apply(outcome, axis=1)
    def priority(r):
        if r["Outcome"] == "Likely Successful":
            return "High"
        elif r["Final_Attack"] != "Normal":
            return "Medium"
        return "Low"
    df["Priority"] = df.apply(priority, axis=1)
    return df
